"""Product Ranker — multi-criteria scoring + trade-off generation.

Ranks retrieved products against customer needs using both
domain-specific rules and LLM-powered trade-off explanations.
"""
from __future__ import annotations

import logging
from typing import Any

from backend.core.llm_client import llm_generate_json
from backend.models.schemas import Category, CustomerNeed, Product, ProductRecommendation

logger = logging.getLogger(__name__)

# ── Domain-specific scoring rules ──────────────────────────────────

def _score_tu_lanh(product: Product, need: CustomerNeed) -> float:
    """Score a refrigerator against customer needs."""
    score = 0.0
    specs = product.specs

    # Capacity vs household size (80-100L per person)
    if need.household_size:
        capacity_str = specs.get("Dung tích tổng", "")
        try:
            capacity = float("".join(c for c in capacity_str if c.isdigit() or c == "."))
            ideal_min = need.household_size * 80
            ideal_max = need.household_size * 100
            if ideal_min <= capacity <= ideal_max * 1.3:
                score += 30
            elif capacity >= ideal_min * 0.8:
                score += 15
        except (ValueError, TypeError):
            pass

    # Budget fit
    if need.budget_max and product.effective_price:
        if product.effective_price <= need.budget_max:
            # Prefer products that use 60-90% of budget (good value)
            ratio = product.effective_price / need.budget_max
            if 0.6 <= ratio <= 0.9:
                score += 25
            elif ratio <= 0.6:
                score += 15  # too cheap might mean fewer features
            else:
                score += 20

    # Priority matching
    priorities_lower = [p.lower() for p in need.priorities]
    if "tiết kiệm điện" in priorities_lower or "inverter" in priorities_lower:
        if "inverter" in specs.get("Công nghệ tiết kiệm điện", "").lower():
            score += 20
        energy = specs.get("Điện năng tiêu thụ", "")
        if energy:
            try:
                kwh = float("".join(c for c in energy if c.isdigit() or c == "."))
                if kwh < 300:
                    score += 10
            except ValueError:
                pass

    if "êm" in " ".join(priorities_lower) or "ít ồn" in " ".join(priorities_lower):
        if "inverter" in specs.get("Công nghệ tiết kiệm điện", "").lower():
            score += 10

    # Promotion bonus
    if product.price_promo and product.price_original:
        if product.price_promo < product.price_original:
            score += 5

    return score


CATEGORY_SCORERS = {
    Category.TU_LANH: _score_tu_lanh,
    # Add more category scorers as needed
}


async def rank_products(
    candidates: list[dict[str, Any]],
    need: CustomerNeed,
    top_k: int = 3,
) -> list[ProductRecommendation]:
    """Rank candidates and generate trade-off explanations.

    Step 1: Domain-specific scoring
    Step 2: LLM-powered trade-off explanation for top K
    """
    # Step 1: Score each candidate
    scored = []
    scorer = CATEGORY_SCORERS.get(need.category)

    for candidate in candidates:
        product: Product = candidate["product"]
        similarity = candidate.get("similarity", 0.0)

        domain_score = scorer(product, need) if scorer else 0.0
        # Combine: 60% domain rules + 40% semantic similarity
        total_score = domain_score * 0.6 + similarity * 100 * 0.4

        scored.append({
            **candidate,
            "total_score": total_score,
            "domain_score": domain_score,
        })

    # Sort by total score descending
    scored.sort(key=lambda x: x["total_score"], reverse=True)
    top_candidates = scored[:top_k]

    # Step 2: Generate trade-off explanations via LLM
    recommendations = await _generate_trade_offs(top_candidates, need)

    return recommendations


async def _generate_trade_offs(
    candidates: list[dict[str, Any]],
    need: CustomerNeed,
) -> list[ProductRecommendation]:
    """Use LLM to generate human-friendly trade-off explanations."""
    # Build product summaries for the LLM
    product_summaries = []
    for i, c in enumerate(candidates):
        product: Product = c["product"]
        api_data = c.get("api_data", {})
        price_info = api_data.get("price", {})
        promo_info = api_data.get("promotion", {})
        review_info = api_data.get("reviews", {})
        stock_info = api_data.get("stock", {})

        summary = {
            "rank": i + 1,
            "product_id": product.id,
            "brand": product.brand,
            "name": product.name,
            "specs": product.specs,
            "price_original": product.price_original,
            "price_promo": product.price_promo,
            "promotion": product.promotion_gift,
            "rating": review_info.get("average_rating") if review_info else None,
            "review_count": review_info.get("review_count") if review_info else None,
            "in_stock": stock_info.get("in_stock") if stock_info else None,
            "installment": price_info.get("installment_available") if price_info else None,
        }
        product_summaries.append(summary)

    prompt = f"""Bạn là chuyên gia tư vấn sản phẩm tại Điện Máy Xanh.

Nhu cầu khách hàng:
- Danh mục: {need.category.value}
- Ngân sách: {f'dưới {need.budget_max:,}đ' if need.budget_max else 'chưa xác định'}
- Số người sử dụng: {need.household_size or 'chưa xác định'}
- Diện tích phòng: {f'{need.room_area}m²' if need.room_area else 'chưa xác định'}
- Ưu tiên: {', '.join(need.priorities) if need.priorities else 'chưa xác định'}
- Mục đích: {', '.join(need.usage_purpose) if need.usage_purpose else 'chưa xác định'}

Top {len(product_summaries)} sản phẩm đã được lọc:
{product_summaries}

Hãy tạo trade-off analysis cho mỗi sản phẩm. Trả về JSON array, mỗi phần tử có:
{{
    "rank": number,
    "product_id": string,
    "strengths": [string],  // 2-3 điểm mạnh, viết bằng ngôn ngữ dễ hiểu cho khách phổ thông
    "trade_offs": [string], // 1-2 điểm đánh đổi, viết trung thực
    "summary": string       // 1 câu tóm tắt tại sao nên/không nên chọn
}}

QUY TẮC:
1. Dùng ngôn ngữ bình dân, KHÔNG dùng thuật ngữ kỹ thuật phức tạp
2. So sánh các sản phẩm với nhau, nêu rõ khác biệt
3. Nếu sản phẩm #1 tốt hơn ở điểm nào, nói rõ
4. KHÔNG bịa thông số, chỉ dựa vào data được cung cấp
5. Nếu thiếu thông tin, nói "chưa có dữ liệu" thay vì đoán
"""

    try:
        result = await llm_generate_json(prompt, temperature=0.3)
        if not isinstance(result, list):
            result = [result]

        recommendations = []
        for i, c in enumerate(candidates):
            product: Product = c["product"]
            trade_off = result[i] if i < len(result) else {}

            rec = ProductRecommendation(
                product=product,
                rank=i + 1,
                match_score=c.get("total_score", 0),
                strengths=trade_off.get("strengths", []),
                trade_offs=trade_off.get("trade_offs", []),
                summary=trade_off.get("summary", ""),
                data_sources=["Catalog sản phẩm", "Price API", "Stock API"],
            )
            recommendations.append(rec)

        return recommendations

    except Exception as e:
        logger.error(f"Failed to generate trade-offs: {e}")
        # Fallback: return without LLM explanations
        return [
            ProductRecommendation(
                product=c["product"],
                rank=i + 1,
                match_score=c.get("total_score", 0),
                strengths=["Phù hợp với nhu cầu dựa trên thông số"],
                trade_offs=[],
                summary=c["product"].description,
                data_sources=["Catalog sản phẩm"],
            )
            for i, c in enumerate(candidates)
        ]
