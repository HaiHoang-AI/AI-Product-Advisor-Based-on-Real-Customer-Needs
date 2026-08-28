"""Guardrail — anti-hallucination and data integrity checks.

Ensures all product information comes from the catalog/APIs,
prevents fabrication of prices, stock levels, or specs.
"""
from __future__ import annotations

import logging
import re
from typing import Any

from backend.models.schemas import Product, ProductRecommendation

logger = logging.getLogger(__name__)


class Guardrail:
    """Validates AI responses against source data to prevent hallucination."""

    def __init__(self, products_map: dict[str, Product]):
        self._products = products_map

    def validate_recommendation(
        self,
        recommendation: ProductRecommendation,
        api_data: dict[str, Any] | None = None,
    ) -> ProductRecommendation:
        """Validate a recommendation, adding warnings if data is missing."""
        product = recommendation.product
        warnings = []

        # Check if product exists in catalog
        if product.id not in self._products:
            warnings.append("⚠️ Sản phẩm không tìm thấy trong catalog.")
            logger.warning(f"Product {product.id} not found in catalog")

        # Check price data
        if product.effective_price is None:
            warnings.append("💰 Hiện chưa có thông tin giá cho sản phẩm này.")

        # Check stock data
        if api_data:
            stock = api_data.get("stock", {})
            if stock and not stock.get("in_stock", True):
                warnings.append("📦 Sản phẩm hiện đang hết hàng.")

        # Ensure data sources are cited
        if not recommendation.data_sources:
            recommendation.data_sources = ["Catalog sản phẩm"]

        # Add warnings to trade_offs
        if warnings:
            recommendation.trade_offs = warnings + recommendation.trade_offs

        return recommendation

    def validate_response_text(self, text: str, context_products: list[Product]) -> str:
        """Validate a text response for potential hallucinations.

        Checks for fabricated prices, specs, or claims not in the data.
        """
        # Check for price patterns that might be fabricated
        price_pattern = r"(\d{1,3}(?:[.,]\d{3})*)\s*(?:đ|đồng|VND|vnđ)"
        prices_mentioned = re.findall(price_pattern, text)

        catalog_prices = set()
        for p in context_products:
            if p.price_original:
                catalog_prices.add(str(p.price_original))
            if p.price_promo:
                catalog_prices.add(str(p.price_promo))

        # If we found prices in text, verify them
        for price_str in prices_mentioned:
            normalized = price_str.replace(".", "").replace(",", "")
            if normalized and normalized not in catalog_prices:
                logger.warning(f"Potentially fabricated price in response: {price_str}")
                # We don't modify the text here, just log it
                # The LLM guardrail prompt should handle this

        return text

    @staticmethod
    def build_guardrail_prompt() -> str:
        """Return system prompt instructions for anti-hallucination."""
        return """
QUY TẮC BẮT BUỘC (GUARDRAIL):
1. CHỈ dùng thông tin từ catalog sản phẩm, Price API, Stock API và Promotion API đã được cung cấp.
2. KHÔNG được bịa giá, tồn kho, khuyến mãi hoặc thông số kỹ thuật.
3. Nếu không có dữ liệu cho một thông tin nào đó, PHẢI nói rõ: "Hiện em chưa có thông tin về..." 
4. KHÔNG nói sản phẩm nào cũng tốt. Phải so sánh trung thực, nêu cả ưu và nhược điểm.
5. Mỗi claim phải có thể truy vết về nguồn dữ liệu.
6. Giá hiển thị là giá online tham khảo. Nhắc khách hàng xác nhận tại cửa hàng nếu cần.
7. KHÔNG ép mua, KHÔNG phóng đại. Tư vấn trung thực và khách quan.
"""
