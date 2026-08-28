"""Data ingestion & processing pipeline.

Reads product data from CSV/Excel files, cleans/normalizes it,
and prepares it for the vector store and mock APIs.
"""
from __future__ import annotations

import json
import logging
import os
import re
from pathlib import Path
from typing import Any

import pandas as pd

from backend.models.schemas import Category, Product

logger = logging.getLogger(__name__)

# ── Column mappings ────────────────────────────────────────────────

# Maps CSV column names to our canonical spec keys
SPEC_COLUMNS = [
    "Kiểu dáng", "Công nghệ làm lạnh", "Sản xuất tại", "Thời gian ra mắt",
    "Chất liệu khay ngăn lạnh", "Dung tích tổng", "Dung tích ngăn đá",
    "Dung tích ngăn lạnh", "Điện năng tiêu thụ", "Chất liệu thân vỏ",
    "Số người sử dụng", "Dung tích sử dụng", "Công nghệ tiết kiệm điện",
    "Công nghệ bảo quản thực phẩm", "Tiện ích", "Chất liệu động cơ",
    "Dung tích ngăn chuyển đổi", "Số cửa", "Cao", "Ngang", "Sâu",
    "Khối lượng máy", "Lấy nước ngoài", "Chế độ tự động",
]


def _parse_price(val: Any) -> int | None:
    """Parse price from various formats: '12,990,000', '12990000', etc."""
    if pd.isna(val) or val is None:
        return None
    s = str(val).replace(",", "").replace(".", "").replace("đ", "").strip()
    s = re.sub(r"[^\d]", "", s)
    if s:
        return int(s)
    return None


def _detect_category_from_columns(columns: list[str]) -> Category:
    """Detect product category from column names."""
    col_text = " ".join(columns).lower()
    if "dung tích" in col_text or "ngăn đá" in col_text:
        return Category.TU_LANH
    if "công suất làm lạnh" in col_text or "btu" in col_text:
        return Category.MAY_LANH
    if "ram" in col_text and ("camera" in col_text or "pin" in col_text):
        return Category.DIEN_THOAI
    if "ram" in col_text and "cpu" in col_text:
        return Category.LAPTOP
    return Category.UNKNOWN


def _generate_product_name(row: dict, brand: str, category: Category) -> str:
    """Generate a human-readable product name."""
    parts = [str(brand).strip()] if brand else []
    if category == Category.TU_LANH:
        capacity = row.get("Dung tích tổng")
        style = row.get("Kiểu dáng")
        if pd.notna(capacity) and str(capacity).strip():
            parts.append(f"Tủ lạnh {str(capacity).strip()}")
        if pd.notna(style) and str(style).strip():
            parts.append(str(style).strip())
    return " ".join(parts) if parts else "Sản phẩm điện máy"


def _generate_description(product: Product) -> str:
    """Generate a human-friendly description from product specs."""
    lines = []
    cat_name = product.category.value.title()
    lines.append(f"{cat_name} {product.brand}")

    specs = product.specs
    if product.category == Category.TU_LANH:
        if specs.get("Dung tích tổng"):
            lines.append(f"dung tích {specs['Dung tích tổng']}")
        if specs.get("Số người sử dụng"):
            lines.append(f"phù hợp {specs['Số người sử dụng']}")
        if specs.get("Kiểu dáng"):
            lines.append(f"kiểu {specs['Kiểu dáng']}")
        if specs.get("Công nghệ tiết kiệm điện"):
            lines.append(f"công nghệ {specs['Công nghệ tiết kiệm điện']}")
        if specs.get("Điện năng tiêu thụ"):
            lines.append(f"tiêu thụ {specs['Điện năng tiêu thụ']}")

    if product.price_promo:
        lines.append(f"giá khuyến mãi {product.price_promo:,}đ".replace(",", "."))
    elif product.price_original:
        lines.append(f"giá {product.price_original:,}đ".replace(",", "."))

    return ", ".join(lines)


def load_csv_products(csv_path: str | Path) -> list[Product]:
    """Load products from a CSV file."""
    logger.info(f"Loading products from CSV: {csv_path}")
    df = pd.read_csv(csv_path, encoding="utf-8")
    category = _detect_category_from_columns(list(df.columns))
    logger.info(f"Detected category: {category.value}, rows: {len(df)}")

    products = []
    for idx, row in df.iterrows():
        row_dict = row.to_dict()

        # Extract specs (non-null only)
        specs = {}
        for col in SPEC_COLUMNS:
            val = row_dict.get(col)
            if pd.notna(val) and str(val).strip():
                specs[col] = str(val).strip()

        brand_val = row_dict.get("brand")
        brand = str(brand_val).strip() if pd.notna(brand_val) else ""
        pid = row_dict.get("productidweb")
        prod_id = f"prod_{idx}_{pid}" if pd.notna(pid) else f"prod_{idx}"
        product = Product(
            id=prod_id,
            model_code=str(row_dict.get("model_code", "") if pd.notna(row_dict.get("model_code")) else ""),
            sku=str(row_dict.get("sku", "") if pd.notna(row_dict.get("sku")) else ""),
            category=category,
            brand=brand,
            name=_generate_product_name(row_dict, brand, category),
            specs=specs,
            price_original=_parse_price(row_dict.get("giá gốc")),
            price_promo=_parse_price(row_dict.get("giá khuyến mãi")),
            promotion_gift=str(row_dict.get("khuyến mãi quà", "")).strip()
                if pd.notna(row_dict.get("khuyến mãi quà")) else "",
        )
        product.description = _generate_description(product)
        products.append(product)

    logger.info(f"Loaded {len(products)} products")
    return products


def load_excel_products(excel_path: str | Path) -> list[Product]:
    """Load products from an Excel file (all sheets)."""
    logger.info(f"Loading products from Excel: {excel_path}")
    all_products = []

    xls = pd.ExcelFile(excel_path)
    for sheet_name in xls.sheet_names:
        logger.info(f"Processing sheet: {sheet_name}")
        df = pd.read_excel(excel_path, sheet_name=sheet_name)
        if len(df) < 2:
            continue

        category = _detect_category_from_columns(list(df.columns))
        # Also try to detect from sheet name
        sheet_lower = sheet_name.lower()
        if "tủ lạnh" in sheet_lower or "tu lanh" in sheet_lower:
            category = Category.TU_LANH
        elif "máy lạnh" in sheet_lower or "may lanh" in sheet_lower:
            category = Category.MAY_LANH
        elif "điện thoại" in sheet_lower or "dien thoai" in sheet_lower:
            category = Category.DIEN_THOAI
        elif "laptop" in sheet_lower:
            category = Category.LAPTOP

        for idx, row in df.iterrows():
            row_dict = row.to_dict()
            specs = {}
            for col in df.columns:
                if col not in ("model_code", "sku", "productidweb", "category_code",
                               "brand_id", "brand", "giá gốc", "giá khuyến mãi",
                               "khuyến mãi quà"):
                    val = row_dict.get(col)
                    if pd.notna(val) and str(val).strip():
                        specs[str(col)] = str(val).strip()

            brand_val = row_dict.get("brand")
            brand = str(brand_val).strip() if pd.notna(brand_val) else ""
            product = Product(
                id=f"{sheet_name}_{idx}_{row_dict.get('productidweb', idx)}",
                model_code=str(row_dict.get("model_code", "") if pd.notna(row_dict.get("model_code")) else ""),
                sku=str(row_dict.get("sku", "") if pd.notna(row_dict.get("sku")) else ""),
                category=category,
                brand=brand,
                name=_generate_product_name(row_dict, brand, category),
                specs=specs,
                price_original=_parse_price(row_dict.get("giá gốc")),
                price_promo=_parse_price(row_dict.get("giá khuyến mãi")),
                promotion_gift=str(row_dict.get("khuyến mãi quà", "")).strip()
                    if pd.notna(row_dict.get("khuyến mãi quà")) else "",
            )
            product.description = _generate_description(product)
            all_products.append(product)

    logger.info(f"Loaded {len(all_products)} products from Excel")
    return all_products


def save_processed_products(products: list[Product], output_path: str | Path) -> None:
    """Save processed products to JSON for quick reload."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    data = [p.model_dump() for p in products]
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logger.info(f"Saved {len(products)} products to {output_path}")


def load_processed_products(json_path: str | Path) -> list[Product]:
    """Load pre-processed products from JSON."""
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [Product(**item) for item in data]
