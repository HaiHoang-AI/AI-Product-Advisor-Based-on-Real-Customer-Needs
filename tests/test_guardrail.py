"""Test anti-hallucination guardrail logic."""
import sys
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from backend.core.guardrail import Guardrail
from backend.models.schemas import Category, Product, ProductRecommendation


class TestGuardrail(unittest.TestCase):

    def setUp(self):
        self.sample_product = Product(
            id="p123",
            model_code="SAM-01",
            category=Category.TU_LANH,
            brand="Samsung",
            name="Tủ lạnh Samsung Inverter 300L",
            price_original=12000000,
            price_promo=10500000,
            specs={"Dung tích tổng": "300 lít", "Kiểu dáng": "Ngăn đá dưới"},
        )
        self.products_map = {self.sample_product.id: self.sample_product}
        self.guardrail = Guardrail(self.products_map)

    def test_validate_valid_product(self):
        rec = ProductRecommendation(
            product=self.sample_product,
            rank=1,
            match_score=95.0,
            strengths=["Dung tích 300L vừa gia đình 3-4 người"],
            trade_offs=["Giá cao hơn các dòng không inverter"],
            summary="Lựa chọn tối ưu cho gia đình",
        )
        validated = self.guardrail.validate_recommendation(rec, {"stock": {"in_stock": True}})
        self.assertIn("Catalog sản phẩm", validated.data_sources)
        self.assertFalse(any("không tìm thấy" in w for w in validated.trade_offs))

    def test_validate_out_of_stock_warning(self):
        rec = ProductRecommendation(
            product=self.sample_product,
            rank=1,
            match_score=90.0,
        )
        validated = self.guardrail.validate_recommendation(rec, {"stock": {"in_stock": False}})
        self.assertTrue(any("hết hàng" in w for w in validated.trade_offs))

    def test_validate_missing_catalog_product(self):
        unknown_product = Product(
            id="fake_999",
            name="Tủ lạnh ảo",
            brand="BiaDat",
            category=Category.TU_LANH,
        )
        rec = ProductRecommendation(product=unknown_product, rank=1)
        validated = self.guardrail.validate_recommendation(rec)
        self.assertTrue(any("không tìm thấy trong catalog" in w for w in validated.trade_offs))


if __name__ == "__main__":
    unittest.main()
