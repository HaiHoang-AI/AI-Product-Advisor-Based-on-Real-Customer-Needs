"""Mock APIs for Price, Stock, Promotion, and Reviews.

These simulate what real APIs would provide in production.
Data is derived from the product catalog.
"""
from __future__ import annotations

import random
from typing import Any

from backend.models.schemas import Product

# ── Regions ────────────────────────────────────────────────────────

REGIONS = [
    "TP. Hồ Chí Minh", "Hà Nội", "Đà Nẵng", "Cần Thơ",
    "Hải Phòng", "Bình Dương", "Đồng Nai",
]


class PriceAPI:
    """Mock Price API — returns price info from catalog."""

    def __init__(self, products: list[Product]):
        self._price_map: dict[str, dict] = {}
        for p in products:
            self._price_map[p.id] = {
                "product_id": p.id,
                "price_original": p.price_original,
                "price_promo": p.price_promo,
                "currency": "VND",
                "installment_available": random.choice([True, False]),
                "installment_months": random.choice([6, 12, 18, 24]) if random.random() > 0.3 else None,
                "installment_rate": "0%" if random.random() > 0.5 else "1.5%/tháng",
            }

    def get_price(self, product_id: str) -> dict[str, Any] | None:
        return self._price_map.get(product_id)

    def get_prices(self, product_ids: list[str]) -> list[dict[str, Any]]:
        return [self._price_map[pid] for pid in product_ids if pid in self._price_map]


class StockAPI:
    """Mock Stock API — simulates inventory availability."""

    def __init__(self, products: list[Product]):
        self._stock_map: dict[str, dict] = {}
        for p in products:
            available_regions = random.sample(REGIONS, k=random.randint(2, len(REGIONS)))
            self._stock_map[p.id] = {
                "product_id": p.id,
                "in_stock": random.random() > 0.15,
                "available_regions": available_regions,
                "quantity": random.randint(0, 50) if random.random() > 0.15 else 0,
            }

    def get_stock(self, product_id: str) -> dict[str, Any] | None:
        return self._stock_map.get(product_id)

    def check_availability(self, product_id: str, region: str = "") -> bool:
        stock = self._stock_map.get(product_id)
        if not stock:
            return False
        if not stock["in_stock"]:
            return False
        if region and region not in stock["available_regions"]:
            return False
        return True


class PromotionAPI:
    """Mock Promotion API — returns promo info."""

    def __init__(self, products: list[Product]):
        self._promo_map: dict[str, dict] = {}
        for p in products:
            promos = []
            if p.promotion_gift:
                promos.append({"type": "gift", "description": p.promotion_gift})
            if p.price_promo and p.price_original and p.price_promo < p.price_original:
                discount = p.price_original - p.price_promo
                pct = round(discount / p.price_original * 100)
                promos.append({
                    "type": "discount",
                    "description": f"Giảm {discount:,}đ ({pct}%)".replace(",", "."),
                    "amount": discount,
                })
            self._promo_map[p.id] = {
                "product_id": p.id,
                "promotions": promos,
                "has_promotion": len(promos) > 0,
            }

    def get_promotions(self, product_id: str) -> dict[str, Any] | None:
        return self._promo_map.get(product_id)


class ReviewAPI:
    """Mock Review API — generates synthetic review summaries."""

    REVIEW_TEMPLATES = [
        "Sản phẩm chất lượng tốt, {feature} rất ổn.",
        "Dùng {duration} rồi, {aspect} khá hài lòng.",
        "Giá hợp lý so với tính năng, {highlight}.",
        "{brand} lần nào cũng không thất vọng.",
        "Giao hàng nhanh, lắp đặt chuyên nghiệp.",
    ]

    FEATURES = ["làm lạnh nhanh", "tiết kiệm điện", "chạy êm", "thiết kế đẹp", "dung tích lớn"]
    DURATIONS = ["3 tháng", "6 tháng", "1 năm", "2 năm"]
    ASPECTS = ["độ bền", "hiệu năng", "tiếng ồn", "tiết kiệm điện"]
    HIGHLIGHTS = ["inverter rất tốt", "ngăn rau quả rộng", "chạy rất êm", "tiết kiệm điện đáng kể"]

    def __init__(self, products: list[Product]):
        self._review_map: dict[str, dict] = {}
        for p in products:
            rating = round(random.uniform(3.5, 5.0), 1)
            count = random.randint(5, 500)
            summaries = []
            for _ in range(random.randint(2, 4)):
                template = random.choice(self.REVIEW_TEMPLATES)
                summary = template.format(
                    feature=random.choice(self.FEATURES),
                    duration=random.choice(self.DURATIONS),
                    aspect=random.choice(self.ASPECTS),
                    highlight=random.choice(self.HIGHLIGHTS),
                    brand=p.brand,
                )
                summaries.append(summary)

            self._review_map[p.id] = {
                "product_id": p.id,
                "average_rating": rating,
                "review_count": count,
                "summary_highlights": summaries,
            }

    def get_reviews(self, product_id: str) -> dict[str, Any] | None:
        return self._review_map.get(product_id)


class MockAPIManager:
    """Centralized access to all mock APIs."""

    def __init__(self, products: list[Product]):
        self.price = PriceAPI(products)
        self.stock = StockAPI(products)
        self.promotion = PromotionAPI(products)
        self.review = ReviewAPI(products)

    def get_full_product_info(self, product_id: str) -> dict[str, Any]:
        """Get all info for a product from all APIs."""
        return {
            "price": self.price.get_price(product_id),
            "stock": self.stock.get_stock(product_id),
            "promotion": self.promotion.get_promotions(product_id),
            "reviews": self.review.get_reviews(product_id),
        }
