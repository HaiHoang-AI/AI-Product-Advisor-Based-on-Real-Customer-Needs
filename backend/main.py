"""FastAPI application — main entry point for the backend."""
from __future__ import annotations

import json
import logging
import os
import sys
import glob
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse

from backend.config import settings
from backend.core.orchestrator import Orchestrator
from backend.data.embeddings import VectorStore
from backend.data.mock_apis import MockAPIManager
from backend.data.pipeline import (
    load_csv_products,
    load_excel_products,
    load_processed_products,
    save_processed_products,
)
from backend.models.schemas import ChatRequest, Product, SSEEvent

# ── Logging ────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# ── Globals ────────────────────────────────────────────────────────

orchestrator: Orchestrator | None = None
products_map: dict[str, Product] = {}


# ── Startup / Shutdown ─────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Initialize data pipeline and AI components on startup."""
    global orchestrator, products_map

    logger.info("🚀 Starting AI Product Comparison Advisor...")

    # Step 1: Load products
    processed_path = os.path.join(settings.DATA_PROCESSED_DIR, "products.json")

    if os.path.exists(processed_path):
        logger.info("Loading pre-processed products...")
        products = load_processed_products(processed_path)
    else:
        logger.info("Processing raw product data...")
        products = []

        # Load CSV files
        raw_dir = settings.DATA_RAW_DIR
        project_root = settings.PROJECT_ROOT

        # Search for CSV files in project root and data/raw
        for search_dir in [project_root, raw_dir]:
            csv_pattern = os.path.join(search_dir, "*.csv")
            for csv_file in glob.glob(csv_pattern):
                logger.info(f"Loading CSV: {csv_file}")
                products.extend(load_csv_products(csv_file))

        # Search for Excel files
        for search_dir in [project_root, raw_dir]:
            for ext in ["*.xlsx", "*.xls"]:
                excel_pattern = os.path.join(search_dir, ext)
                for excel_file in glob.glob(excel_pattern):
                    # Skip temp files
                    if "~$" in excel_file:
                        continue
                    logger.info(f"Loading Excel: {excel_file}")
                    try:
                        products.extend(load_excel_products(excel_file))
                    except Exception as e:
                        logger.warning(f"Failed to load {excel_file}: {e}")

        if products:
            os.makedirs(settings.DATA_PROCESSED_DIR, exist_ok=True)
            save_processed_products(products, processed_path)

    logger.info(f"📦 Loaded {len(products)} products")

    # Step 2: Build products map
    products_map = {p.id: p for p in products}

    # Step 3: Initialize vector store
    vector_store = VectorStore()
    if vector_store.count == 0 and products:
        logger.info("Indexing products into vector store...")
        vector_store.index_products(products)
    logger.info(f"🔍 Vector store: {vector_store.count} items")

    # Step 4: Initialize mock APIs
    api_manager = MockAPIManager(products)
    logger.info("✅ Mock APIs initialized")

    # Step 5: Create orchestrator
    orchestrator = Orchestrator(vector_store, api_manager, products_map)
    logger.info("🤖 Orchestrator ready!")

    yield

    logger.info("👋 Shutting down...")


# ── FastAPI App ────────────────────────────────────────────────────

app = FastAPI(
    title="AI Product Comparison Advisor",
    description="Trợ lý AI so sánh và tư vấn sản phẩm theo nhu cầu thật của khách hàng — Điện Máy Xanh",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Routes ─────────────────────────────────────────────────────────

@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "products_count": len(products_map),
        "ai_ready": orchestrator is not None,
    }


@app.post("/api/chat")
async def chat(request: ChatRequest):
    """Chat endpoint — returns SSE stream of events."""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="AI engine not initialized")

    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    async def event_generator():
        async for event in orchestrator.handle_message(request):
            data = json.dumps(
                {"type": event.type.value, "content": event.content},
                ensure_ascii=False,
            )
            yield {"data": data}

    return EventSourceResponse(event_generator())


@app.get("/api/products/{product_id}")
async def get_product(product_id: str):
    """Get product details by ID."""
    product = products_map.get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product.model_dump()


@app.get("/api/products")
async def list_products(
    category: str = "",
    brand: str = "",
    limit: int = 20,
    offset: int = 0,
):
    """List products with optional filters."""
    filtered = list(products_map.values())

    if category:
        filtered = [p for p in filtered if p.category.value == category]
    if brand:
        filtered = [p for p in filtered if p.brand.lower() == brand.lower()]

    total = len(filtered)
    items = filtered[offset:offset + limit]

    return {
        "total": total,
        "items": [p.model_dump() for p in items],
    }


# ── Main ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True,
    )
