"""Test data loading, cleaning and mock APIs."""
import os
import sys
import unittest
from pathlib import Path

# Add backend to path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from backend.data.pipeline import load_csv_products, load_excel_products
from backend.data.mock_apis import MockAPIManager
from backend.models.schemas import Category


class TestDataPipeline(unittest.TestCase):

    def test_load_csv_tu_lanh(self):
        csv_path = ROOT_DIR / "Spec_cate_gia.xlsx - Tủ Lạnh.csv"
        if not csv_path.exists():
            self.skipTest("CSV file not found")

        products = load_csv_products(csv_path)
        self.assertGreater(len(products), 1000)

        sample = products[0]
        self.assertEqual(sample.category, Category.TU_LANH)
        self.assertTrue(bool(sample.brand))
        self.assertTrue(bool(sample.specs))

    def test_mock_apis(self):
        csv_path = ROOT_DIR / "Spec_cate_gia.xlsx - Tủ Lạnh.csv"
        if not csv_path.exists():
            self.skipTest("CSV file not found")

        products = load_csv_products(csv_path)[:50]
        api = MockAPIManager(products)

        sample = products[0]
        price_info = api.price.get_price(sample.id)
        self.assertIsNotNone(price_info)
        self.assertIn("price_promo", price_info)

        stock_info = api.stock.get_stock(sample.id)
        self.assertIsNotNone(stock_info)

        promo_info = api.promotion.get_promotions(sample.id)
        self.assertIsNotNone(promo_info)


if __name__ == "__main__":
    unittest.main()
