"""Follow-up Engine — generates smart follow-up questions by category.

Uses domain-specific knowledge to ask the most impactful questions,
limiting to 2-3 questions max to avoid annoying the customer.
"""
from __future__ import annotations

import logging
from backend.models.schemas import Category, CustomerNeed

logger = logging.getLogger(__name__)

# ── Category-specific question templates ───────────────────────────

FOLLOW_UP_QUESTIONS: dict[Category, list[dict]] = {
    Category.TU_LANH: [
        {
            "condition": lambda n: n.household_size is None,
            "question": "Gia đình mình có bao nhiêu người ạ? (để em gợi ý dung tích phù hợp)",
            "quick_replies": ["2 người", "3-4 người", "5-6 người", "Trên 6 người"],
        },
        {
            "condition": lambda n: "Kiểu dáng" not in " ".join(n.priorities) and not any(
                k in n.additional_notes.lower() for k in ["ngăn đá", "side by side", "cửa", "mini"]
            ),
            "question": "Anh/chị thích kiểu tủ lạnh nào ạ?",
            "quick_replies": ["Ngăn đá trên (phổ biến)", "Ngăn đá dưới", "Side by side", "Tủ mini"],
        },
        {
            "condition": lambda n: n.budget_max is None,
            "question": "Ngân sách dự kiến khoảng bao nhiêu ạ?",
            "quick_replies": ["Dưới 10 triệu", "10-15 triệu", "15-25 triệu", "Trên 25 triệu"],
        },
        {
            "condition": lambda n: n.installment is None and n.budget_max and n.budget_max > 10_000_000,
            "question": "Anh/chị có muốn mua trả góp không ạ?",
            "quick_replies": ["Trả góp 0%", "Trả thẳng", "Tùy giá"],
        },
    ],
    Category.MAY_LANH: [
        {
            "condition": lambda n: n.room_area is None,
            "question": "Phòng cần lắp máy lạnh rộng khoảng bao nhiêu m² ạ?",
            "quick_replies": ["Dưới 15m²", "15-20m²", "20-30m²", "Trên 30m²"],
        },
        {
            "condition": lambda n: n.room_type is None,
            "question": "Đây là phòng ngủ hay phòng khách ạ? (ảnh hưởng đến độ ồn và công suất)",
            "quick_replies": ["Phòng ngủ", "Phòng khách", "Phòng làm việc"],
        },
        {
            "condition": lambda n: n.sun_exposure is None,
            "question": "Phòng có bị nắng trực tiếp chiếu vào không ạ? (cần máy công suất lớn hơn)",
            "quick_replies": ["Có nắng trực tiếp", "Không bị nắng", "Không chắc"],
        },
        {
            "condition": lambda n: n.budget_max is None,
            "question": "Ngân sách dự kiến khoảng bao nhiêu ạ?",
            "quick_replies": ["Dưới 10 triệu", "10-15 triệu", "15-25 triệu", "Trên 25 triệu"],
        },
    ],
    Category.DIEN_THOAI: [
        {
            "condition": lambda n: not n.usage_purpose,
            "question": "Anh/chị dùng điện thoại chủ yếu để làm gì ạ?",
            "quick_replies": ["Chụp ảnh/quay phim", "Chơi game", "Công việc/email", "Dùng cơ bản"],
        },
        {
            "condition": lambda n: n.budget_max is None,
            "question": "Ngân sách dự kiến khoảng bao nhiêu ạ?",
            "quick_replies": ["Dưới 5 triệu", "5-10 triệu", "10-20 triệu", "Trên 20 triệu"],
        },
    ],
    Category.LAPTOP: [
        {
            "condition": lambda n: not n.usage_purpose,
            "question": "Anh/chị dùng laptop chủ yếu để làm gì ạ?",
            "quick_replies": ["Văn phòng/học tập", "Đồ họa/thiết kế", "Chơi game", "Lập trình"],
        },
        {
            "condition": lambda n: n.budget_max is None,
            "question": "Ngân sách dự kiến khoảng bao nhiêu ạ?",
            "quick_replies": ["Dưới 15 triệu", "15-25 triệu", "25-40 triệu", "Trên 40 triệu"],
        },
    ],
}


def get_follow_up_questions(
    need: CustomerNeed,
    max_questions: int = 2,
) -> list[dict]:
    """Get the most relevant follow-up questions for the current need state.

    Returns list of {question, quick_replies} dicts.
    """
    templates = FOLLOW_UP_QUESTIONS.get(need.category, [])
    questions = []

    for template in templates:
        if len(questions) >= max_questions:
            break
        try:
            if template["condition"](need):
                questions.append({
                    "question": template["question"],
                    "quick_replies": template["quick_replies"],
                })
        except Exception as e:
            logger.warning(f"Error evaluating follow-up condition: {e}")
            continue

    return questions


def format_follow_up_message(questions: list[dict]) -> str:
    """Format follow-up questions into a natural Vietnamese message."""
    if not questions:
        return ""

    if len(questions) == 1:
        return questions[0]["question"]

    parts = ["Để em tư vấn chính xác hơn, anh/chị cho em biết thêm:"]
    for i, q in enumerate(questions, 1):
        parts.append(f"{i}. {q['question']}")

    return "\n".join(parts)
