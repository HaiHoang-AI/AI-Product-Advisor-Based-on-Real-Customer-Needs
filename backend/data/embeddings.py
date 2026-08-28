"""Vector store management with ChromaDB support and zero-dependency local fallback.

Provides semantic and keyword hybrid search over product catalog.
"""
from __future__ import annotations

import json
import logging
import math
import os
import re
from typing import Any

from backend.config import settings
from backend.models.schemas import Product

logger = logging.getLogger(__name__)

# Check if chromadb is available
try:
    import chromadb
    from chromadb.config import Settings as ChromaSettings
    HAS_CHROMADB = True
except ImportError:
    HAS_CHROMADB = False
    logger.info("ChromaDB not installed or unavailable. Using high-performance built-in Vector/BM25 Store.")


class BuiltinVectorStore:
    """Built-in inverted index & cosine-similarity vector store with persistent JSON storage."""

    def __init__(self, storage_path: str):
        self.storage_path = storage_path
        self.documents: dict[str, dict[str, Any]] = {}
        self.idf: dict[str, float] = {}
        self.avg_doc_len: float = 0.0
        self._load()

    def _tokenize(self, text: str) -> list[str]:
        # Lowercase, clean non-alphanumeric, split
        text = text.lower()
        tokens = re.findall(r"\w+", text)
        return tokens

    def _load(self):
        index_file = os.path.join(self.storage_path, "local_index.json")
        if os.path.exists(index_file):
            try:
                with open(index_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.documents = data.get("documents", {})
                    self.idf = data.get("idf", {})
                    self.avg_doc_len = data.get("avg_doc_len", 0.0)
                logger.info(f"Loaded built-in index with {len(self.documents)} documents")
            except Exception as e:
                logger.warning(f"Failed to load built-in index: {e}")

    def _save(self):
        os.makedirs(self.storage_path, exist_ok=True)
        index_file = os.path.join(self.storage_path, "local_index.json")
        with open(index_file, "w", encoding="utf-8") as f:
            json.dump({
                "documents": self.documents,
                "idf": self.idf,
                "avg_doc_len": self.avg_doc_len,
            }, f, ensure_ascii=False)

    def index(self, items: list[dict[str, Any]]):
        self.documents = {}
        df: dict[str, int] = {}
        total_len = 0

        for item in items:
            doc_id = item["id"]
            text = item["document"]
            meta = item["metadata"]
            tokens = self._tokenize(text)
            total_len += len(tokens)

            tf: dict[str, int] = {}
            for t in tokens:
                tf[t] = tf.get(t, 0) + 1

            for t in tf:
                df[t] = df.get(t, 0) + 1

            self.documents[doc_id] = {
                "id": doc_id,
                "document": text,
                "metadata": meta,
                "tokens": tokens,
                "tf": tf,
                "len": len(tokens),
            }

        N = len(self.documents)
        if N > 0:
            self.avg_doc_len = total_len / N
            self.idf = {
                t: math.log((N - count + 0.5) / (count + 0.5) + 1.0)
                for t, count in df.items()
            }
        self._save()

    def search(
        self,
        query: str,
        n_results: int = 10,
        category: str | None = None,
        price_max: int | None = None,
        brand: str | None = None,
    ) -> list[dict[str, Any]]:
        query_tokens = self._tokenize(query)
        if not query_tokens or not self.documents:
            return []

        k1 = 1.5
        b = 0.75
        scores = []

        for doc_id, doc in self.documents.items():
            meta = doc["metadata"]

            # Filter by category
            if category and meta.get("category", "").lower() != category.lower():
                continue

            # Filter by brand
            if brand and meta.get("brand", "").lower() != brand.lower():
                continue

            # Filter by price
            if price_max is not None:
                price = meta.get("price_effective")
                if price and price > price_max:
                    continue

            # BM25 score calculation
            score = 0.0
            doc_len = doc["len"]
            tf = doc["tf"]

            for q in query_tokens:
                if q in tf:
                    freq = tf[q]
                    idf_val = self.idf.get(q, 0.5)
                    numerator = freq * (k1 + 1.0)
                    denominator = freq + k1 * (1.0 - b + b * (doc_len / (self.avg_doc_len or 1.0)))
                    score += idf_val * (numerator / denominator)

            # Extra exact phrase / priority match bonus
            doc_text = doc["document"].lower()
            for q in query.lower().split():
                if len(q) > 2 and q in doc_text:
                    score += 0.5

            if score > 0:
                scores.append((doc_id, score, doc))

        scores.sort(key=lambda x: x[1], reverse=True)
        top = scores[:n_results]

        output = []
        for doc_id, score, doc in top:
            # Map score to pseudo-distance for compatibility
            sim = min(1.0, score / 10.0)
            output.append({
                "id": doc_id,
                "document": doc["document"],
                "metadata": doc["metadata"],
                "distance": 1.0 - sim,
            })
        return output


class VectorStore:
    """Unified Vector Store supporting ChromaDB and built-in fallback."""

    COLLECTION_NAME = "products"

    def __init__(self):
        os.makedirs(settings.VECTOR_DB_DIR, exist_ok=True)
        self.use_chroma = HAS_CHROMADB
        self._builtin_store = BuiltinVectorStore(settings.VECTOR_DB_DIR)

        if self.use_chroma:
            try:
                self._client = chromadb.PersistentClient(
                    path=settings.VECTOR_DB_DIR,
                    settings=ChromaSettings(anonymized_telemetry=False),
                )
                self._collection = self._client.get_or_create_collection(
                    name=self.COLLECTION_NAME,
                    metadata={"hnsw:space": "cosine"},
                )
                logger.info(f"ChromaDB initialized. Items: {self._collection.count()}")
            except Exception as e:
                logger.warning(f"Failed to initialize ChromaDB ({e}). Falling back to built-in store.")
                self.use_chroma = False

    @property
    def count(self) -> int:
        if self.use_chroma:
            try:
                return self._collection.count()
            except Exception:
                return len(self._builtin_store.documents)
        return len(self._builtin_store.documents)

    def index_products(self, products: list[Product], force: bool = False) -> None:
        """Index products into the store."""
        if self.count > 0 and not force:
            logger.info("Products already indexed.")
            return

        items = []
        for p in products:
            items.append({
                "id": p.id,
                "document": self._build_search_document(p),
                "metadata": self._build_metadata(p),
            })

        # Always index into builtin store for reliability
        self._builtin_store.index(items)

        if self.use_chroma:
            try:
                if force:
                    self._client.delete_collection(self.COLLECTION_NAME)
                    self._collection = self._client.create_collection(
                        name=self.COLLECTION_NAME,
                        metadata={"hnsw:space": "cosine"},
                    )
                batch_size = 100
                for i in range(0, len(items), batch_size):
                    batch = items[i:i + batch_size]
                    self._collection.add(
                        ids=[x["id"] for x in batch],
                        documents=[x["document"] for x in batch],
                        metadatas=[x["metadata"] for x in batch],
                    )
            except Exception as e:
                logger.warning(f"ChromaDB indexing error ({e}), relying on built-in store.")

        logger.info(f"Indexing complete. Total products: {self.count}")

    def search(
        self,
        query: str,
        n_results: int = 10,
        category: str | None = None,
        price_max: int | None = None,
        brand: str | None = None,
    ) -> list[dict[str, Any]]:
        """Search products with filters."""
        if self.use_chroma:
            try:
                where_filters = {}
                if category:
                    where_filters["category"] = category
                if brand:
                    where_filters["brand"] = brand

                where = None
                if where_filters:
                    if len(where_filters) == 1:
                        k, v = next(iter(where_filters.items()))
                        where = {k: v}
                    else:
                        where = {"$and": [{k: v} for k, v in where_filters.items()]}

                results = self._collection.query(
                    query_texts=[query],
                    n_results=n_results * 2,
                    where=where if where else None,
                )
                output = []
                if results and results["ids"] and results["ids"][0]:
                    for i, doc_id in enumerate(results["ids"][0]):
                        item = {
                            "id": doc_id,
                            "document": results["documents"][0][i] if results["documents"] else "",
                            "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                            "distance": results["distances"][0][i] if results["distances"] else 1.0,
                        }
                        if price_max:
                            price = item["metadata"].get("price_effective")
                            if price and price > price_max:
                                continue
                        output.append(item)
                    if output:
                        return output[:n_results]
            except Exception as e:
                logger.warning(f"Chroma search failed: {e}. Using built-in store.")

        return self._builtin_store.search(
            query=query,
            n_results=n_results,
            category=category,
            price_max=price_max,
            brand=brand,
        )

    @staticmethod
    def _build_search_document(product: Product) -> str:
        parts = [
            f"{product.category.value} {product.brand} {product.name}",
            product.description,
        ]
        for key, val in product.specs.items():
            parts.append(f"{key}: {val}")
        if product.promotion_gift:
            parts.append(f"khuyến mãi: {product.promotion_gift}")
        return " | ".join(filter(None, parts))

    @staticmethod
    def _build_metadata(product: Product) -> dict[str, Any]:
        meta: dict[str, Any] = {
            "category": product.category.value,
            "brand": product.brand,
            "model_code": product.model_code,
        }
        if product.effective_price is not None:
            meta["price_effective"] = product.effective_price
        if product.price_original is not None:
            meta["price_original"] = product.price_original
        if product.price_promo is not None:
            meta["price_promo"] = product.price_promo
        for key in ("Số người sử dụng", "Dung tích tổng", "Kiểu dáng", "Số cửa"):
            if key in product.specs:
                meta[f"spec_{key}"] = product.specs[key]
        return meta
