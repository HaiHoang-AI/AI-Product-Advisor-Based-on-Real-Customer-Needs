"""Need Parser — extracts structured customer needs from Vietnamese text.

This is the heart of the system: understanding what the customer really wants
from their natural language input, including slang, abbreviations, and
implicit context.
"""
from __future__ import annotations

import logging
from backend.core.llm_client import llm_generate_json
from backend.models.schemas import Category, CustomerNeed

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Bạn là hệ thống phân tích nhu cầu khách hàng mua sắm tại Điện Máy Xanh.

Nhiệm vụ: Phân tích tin nhắn của khách hàng bằng tiếng Việt và trích xuất nhu cầu mua sắm thành JSON.

Quy tắc:
1. Hiểu tiếng Việt tự nhiên: viết tắt, không dấu, lỗi chính tả, từ địa phương
2. Nhận diện đơn vị: triệu = 1,000,000 VND, m² = mét vuông, HP/mã lực, BTU, lít, inch
3. Hiểu ngữ cảnh mua sắm: "cho gia đình 4 người" → household_size=4
4. Phân loại ưu tiên: tiết kiệm điện, êm, bền, đẹp, giá rẻ, trả góp, làm lạnh nhanh
5. Xác định thông tin còn thiếu quan trọng cần hỏi thêm

Category values: "tủ lạnh", "máy lạnh", "điện thoại", "laptop", "tai nghe", "robot", "unknown"

Trả về JSON với cấu trúc:
{
    "category": string,
    "budget_min": number|null,
    "budget_max": number|null,
    "household_size": number|null,
    "room_area": number|null,
    "room_type": string|null,
    "sun_exposure": boolean|null,
    "usage_purpose": [string],
    "priorities": [string],
    "brand_preference": [string],
    "installment": boolean|null,
    "wants_promotion": boolean|null,
    "additional_notes": string,
    "missing_info": [string]
}

Ví dụ:
- "mua tủ lạnh cho 4 người, dưới 15 tr, tiết kiệm điện" →
  category="tủ lạnh", budget_max=15000000, household_size=4, priorities=["tiết kiệm điện"],
  missing_info=["kiểu dáng ưa thích", "thương hiệu"]

- "em muốn mua máy lạnh phòng 18m2 dưới 20 triệu, ít ồn" →
  category="máy lạnh", budget_max=20000000, room_area=18, priorities=["ít ồn"],
  missing_info=["phòng ngủ hay phòng khách", "hướng nắng"]
"""


async def parse_customer_need(
    message: str,
    existing_need: CustomerNeed | None = None,
    conversation_history: list[dict[str, str]] | None = None,
) -> CustomerNeed:
    """Parse customer message into structured needs.

    If existing_need is provided, merges new info into it (for multi-turn).
    """
    prompt_parts = []

    if conversation_history:
        prompt_parts.append("Lịch sử hội thoại:")
        for msg in conversation_history[-6:]:  # last 6 messages
            role = "Khách" if msg["role"] == "user" else "AI"
            prompt_parts.append(f"  {role}: {msg['content']}")
        prompt_parts.append("")

    if existing_need and existing_need.category != Category.UNKNOWN:
        prompt_parts.append(f"Thông tin đã biết trước đó: {existing_need.model_dump_json()}")
        prompt_parts.append("Hãy cập nhật thông tin mới từ tin nhắn sau, GIỮ NGUYÊN thông tin cũ nếu không bị thay đổi.")
        prompt_parts.append("")

    prompt_parts.append(f"Tin nhắn mới của khách hàng: {message}")
    prompt_parts.append("")
    prompt_parts.append("Phân tích và trả về JSON:")

    prompt = "\n".join(prompt_parts)

    try:
        result = await llm_generate_json(prompt, system_instruction=SYSTEM_PROMPT)

        # Map to CustomerNeed
        need = CustomerNeed(
            category=_parse_category(result.get("category", "unknown")),
            budget_min=result.get("budget_min"),
            budget_max=result.get("budget_max"),
            household_size=result.get("household_size"),
            room_area=result.get("room_area"),
            room_type=result.get("room_type"),
            sun_exposure=result.get("sun_exposure"),
            usage_purpose=result.get("usage_purpose", []),
            priorities=result.get("priorities", []),
            brand_preference=result.get("brand_preference", []),
            installment=result.get("installment"),
            wants_promotion=result.get("wants_promotion"),
            additional_notes=result.get("additional_notes", ""),
            missing_info=result.get("missing_info", []),
            raw_input=message,
        )

        logger.info(f"Parsed need: category={need.category}, budget_max={need.budget_max}")
        return need

    except Exception as e:
        logger.error(f"Failed to parse customer need: {e}")
        return CustomerNeed(raw_input=message, missing_info=["Không hiểu rõ yêu cầu, xin vui lòng mô tả lại."])


def _parse_category(value: str) -> Category:
    """Fuzzy match category from LLM output."""
    value = value.lower().strip()
    mapping = {
        "tủ lạnh": Category.TU_LANH,
        "tu lanh": Category.TU_LANH,
        "refrigerator": Category.TU_LANH,
        "máy lạnh": Category.MAY_LANH,
        "may lanh": Category.MAY_LANH,
        "điều hòa": Category.MAY_LANH,
        "air conditioner": Category.MAY_LANH,
        "điện thoại": Category.DIEN_THOAI,
        "dien thoai": Category.DIEN_THOAI,
        "phone": Category.DIEN_THOAI,
        "laptop": Category.LAPTOP,
        "tai nghe": Category.TAI_NGHE,
        "robot": Category.ROBOT,
    }
    for key, cat in mapping.items():
        if key in value:
            return cat
    return Category.UNKNOWN
