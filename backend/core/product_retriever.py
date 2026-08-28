"""Product Retriever — hybrid search combining semantic + hard filters.

Retrieves candidate products from the vector store and enriches them
with price, stock, promotion and review data from mock APIs.
"""
from __future__ import annotations

import logging
from typing import Any

from backend.data.embeddings import VectorStore
from backend.data.mock_apis import MockAPIManager
from backend.models.schemas import Category, CustomerNeed, Product

logger = logging.getLogger(__name__)


class ProductRetriever:
    """Retrieves and enriches products based on customer needs."""

    def __init__(
        self,
        vector_store: VectorStore,
        api_manager: MockAPIManager,
        products_map: dict[str, Product],
    ):
        self._vector_store = vector_store
        self._api = api_manager
        self._products = products_map

    def retrieve(
        self,
        need: CustomerNeed,
        n_results: int = 10,
    ) -> list[dict[str, Any]]:
        """Retrieve products matching customer needs.

        Returns list of dicts with product + enriched data.
        """
        # Build semantic query from need
        query = self._build_query(need)
        logger.info(f"Search query: {query}")

        # Search vector store with filters
        results = self._vector_store.search(
            query=query,
            n_results=n_results * 2,  # over-fetch to account for post-filtering
            category=need.category.value if need.category != Category.UNKNOWN else None,
            price_max=need.budget_max,
            brand=need.brand_preference[0] if need.brand_preference else None,
        )

        # Enrich with product data and API info
        enriched = []
        for r in results:
            product = self._products.get(r["id"])
            if not product:
                continue

            # Post-filter by budget
            if need.budget_max and product.effective_price:
                if product.effective_price > need.budget_max:
                    continue

            # Enrich with mock API data
            api_data = self._api.get_full_product_info(product.id)

            enriched.append({
                "product": product,
                "similarity": 1 - r.get("distance", 1.0),
                "api_data": api_data,
            })

            if len(enriched) >= n_results:
                break

        logger.info(f"Retrieved {len(enriched)} enriched products")
        return enriched

    @staticmethod
    def _build_query(need: CustomerNeed) -> str:
        """Build a natural language query from structured needs."""
        parts = []

        if need.category != Category.UNKNOWN:
            parts.append(need.category.value)

        if need.brand_preference:
            parts.append(" ".join(need.brand_preference))

        if need.priorities:
            parts.append(" ".join(need.priorities))

        if need.usage_purpose:
            parts.append(" ".join(need.usage_purpose))

        if need.household_size:
            parts.append(f"cho {need.household_size} người")

        if need.room_area:
            parts.append(f"phòng {need.room_area}m²")

        if need.budget_max:
            parts.append(f"dưới {need.budget_max:,}đ".replace(",", "."))

        if need.additional_notes:
            parts.append(need.additional_notes)

        return " ".join(parts) if parts else need.raw_input
