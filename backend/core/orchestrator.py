"""Orchestrator — conversation state machine that ties everything together.

Manages the flow: greeting → need collection → follow-up → retrieval →
comparison → decision support, with the ability to loop back for refinement.
"""
from __future__ import annotations

import logging
import uuid
from typing import Any, AsyncGenerator

from backend.core.follow_up_engine import format_follow_up_message, get_follow_up_questions
from backend.core.guardrail import Guardrail
from backend.core.llm_client import llm_generate
from backend.core.need_parser import parse_customer_need
from backend.core.product_ranker import rank_products
from backend.core.product_retriever import ProductRetriever
from backend.data.embeddings import VectorStore
from backend.data.mock_apis import MockAPIManager
from backend.models.schemas import (
    Category,
    ChatRequest,
    ConversationContext,
    ConversationState,
    CustomerNeed,
    Product,
    ProductRecommendation,
    SSEEvent,
    SSEEventType,
)

logger = logging.getLogger(__name__)


class Orchestrator:
    """Main conversation orchestrator."""

    def __init__(
        self,
        vector_store: VectorStore,
        api_manager: MockAPIManager,
        products_map: dict[str, Product],
    ):
        self._retriever = ProductRetriever(vector_store, api_manager, products_map)
        self._api = api_manager
        self._products = products_map
        self._guardrail = Guardrail(products_map)
        self._conversations: dict[str, ConversationContext] = {}

    def _get_or_create_conversation(self, conversation_id: str) -> ConversationContext:
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
        if conversation_id not in self._conversations:
            self._conversations[conversation_id] = ConversationContext(
                conversation_id=conversation_id,
            )
        return self._conversations[conversation_id]

    async def handle_message(
        self,
        request: ChatRequest,
    ) -> AsyncGenerator[SSEEvent, None]:
        """Process a chat message and yield SSE events."""
        ctx = self._get_or_create_conversation(request.conversation_id)

        # Add user message to history
        ctx.history.append({"role": "user", "content": request.message})

        try:
            # Step 1: Parse/update customer need
            yield SSEEvent(type=SSEEventType.TEXT, content="🔍 Đang phân tích nhu cầu của bạn...")

            ctx.customer_need = await parse_customer_need(
                message=request.message,
                existing_need=ctx.customer_need if ctx.state != ConversationState.GREETING else None,
                conversation_history=ctx.history,
            )
            ctx.customer_need.raw_input = request.message

            # Emit need summary
            need_summary = self._build_need_summary(ctx.customer_need)
            yield SSEEvent(type=SSEEventType.NEED_SUMMARY, content=need_summary)

            # Step 2: Check if we need to ask follow-up questions
            if not ctx.customer_need.is_sufficient() and ctx.follow_up_count < ctx.max_follow_ups:
                ctx.state = ConversationState.FOLLOW_UP
                ctx.follow_up_count += 1

                questions = get_follow_up_questions(ctx.customer_need)
                if questions:
                    message = format_follow_up_message(questions)
                    yield SSEEvent(type=SSEEventType.TEXT, content=message)

                    # Collect all quick replies
                    all_replies = []
                    for q in questions:
                        all_replies.extend(q.get("quick_replies", []))
                    if all_replies:
                        yield SSEEvent(type=SSEEventType.FOLLOW_UP, content=all_replies)

                    ctx.history.append({"role": "assistant", "content": message})
                    yield SSEEvent(type=SSEEventType.DONE, content=None)
                    return

            # Step 3: We have enough info — retrieve products
            ctx.state = ConversationState.RETRIEVAL
            yield SSEEvent(type=SSEEventType.TEXT, content="🔎 Đang tìm sản phẩm phù hợp...")

            candidates = self._retriever.retrieve(ctx.customer_need, n_results=10)

            if not candidates:
                yield SSEEvent(
                    type=SSEEventType.TEXT,
                    content="Xin lỗi, em chưa tìm thấy sản phẩm nào phù hợp với yêu cầu. "
                            "Anh/chị có thể thử mở rộng ngân sách hoặc thay đổi yêu cầu không ạ?",
                )
                ctx.history.append({"role": "assistant", "content": "Không tìm thấy sản phẩm phù hợp."})
                yield SSEEvent(type=SSEEventType.DONE, content=None)
                return

            # Step 4: Rank and generate trade-offs
            ctx.state = ConversationState.COMPARISON
            yield SSEEvent(type=SSEEventType.TEXT, content="📊 Đang so sánh và phân tích...")

            recommendations = await rank_products(candidates, ctx.customer_need, top_k=3)

            # Step 5: Validate with guardrail
            for rec in recommendations:
                api_data = self._api.get_full_product_info(rec.product.id)
                self._guardrail.validate_recommendation(rec, api_data)

            ctx.recommended_products = recommendations

            # Step 6: Generate response
            ctx.state = ConversationState.DECISION_SUPPORT

            # Emit intro text
            intro = await self._generate_intro(ctx.customer_need, recommendations)
            yield SSEEvent(type=SSEEventType.TEXT, content=intro)

            # Emit product recommendations
            products_data = [
                {
                    "rank": rec.rank,
                    "product_id": rec.product.id,
                    "brand": rec.product.brand,
                    "name": rec.product.name,
                    "price_original": rec.product.price_original,
                    "price_promo": rec.product.price_promo,
                    "promotion_gift": rec.product.promotion_gift,
                    "strengths": rec.strengths,
                    "trade_offs": rec.trade_offs,
                    "summary": rec.summary,
                    "specs": {k: v for k, v in rec.product.specs.items()
                              if k in self._get_key_specs(rec.product.category)},
                    "data_sources": rec.data_sources,
                }
                for rec in recommendations
            ]
            yield SSEEvent(type=SSEEventType.PRODUCTS, content=products_data)

            # Emit comparison data
            comparison = self._build_comparison(recommendations)
            yield SSEEvent(type=SSEEventType.COMPARISON, content=comparison)

            # Final message
            closing = (
                "\n\n💡 Anh/chị muốn em giải thích thêm về sản phẩm nào không ạ? "
                "Hoặc nếu muốn thay đổi yêu cầu (ngân sách, thương hiệu, tính năng...) "
                "cứ nói em biết nhé!"
            )
            yield SSEEvent(type=SSEEventType.TEXT, content=closing)

            # Quick replies for refinement
            yield SSEEvent(
                type=SSEEventType.FOLLOW_UP,
                content=[
                    f"Giải thích thêm về #{r.rank}" for r in recommendations[:3]
                ] + ["Thay đổi ngân sách", "Xem thêm sản phẩm khác"],
            )

            # Save to history
            ctx.history.append({
                "role": "assistant",
                "content": f"Đề xuất top {len(recommendations)} sản phẩm: "
                           + ", ".join(r.product.name for r in recommendations),
            })

        except Exception as e:
            logger.error(f"Error in orchestrator: {e}", exc_info=True)
            yield SSEEvent(
                type=SSEEventType.ERROR,
                content=f"Xin lỗi, đã có lỗi xảy ra. Vui lòng thử lại. ({type(e).__name__})",
            )

        yield SSEEvent(type=SSEEventType.DONE, content=None)

    def _build_need_summary(self, need: CustomerNeed) -> dict[str, Any]:
        """Build a summary of understood needs for the frontend."""
        summary = {}
        if need.category != Category.UNKNOWN:
            summary["category"] = need.category.value
        if need.budget_max:
            summary["budget"] = f"Dưới {need.budget_max:,}đ".replace(",", ".")
        if need.budget_min:
            summary["budget_min"] = f"Từ {need.budget_min:,}đ".replace(",", ".")
        if need.household_size:
            summary["household_size"] = f"{need.household_size} người"
        if need.room_area:
            summary["room_area"] = f"{need.room_area}m²"
        if need.room_type:
            summary["room_type"] = need.room_type
        if need.priorities:
            summary["priorities"] = need.priorities
        if need.usage_purpose:
            summary["usage_purpose"] = need.usage_purpose
        if need.brand_preference:
            summary["brand_preference"] = need.brand_preference
        if need.installment is not None:
            summary["installment"] = "Có" if need.installment else "Không"
        if need.missing_info:
            summary["missing_info"] = need.missing_info
        return summary

    @staticmethod
    def _get_key_specs(category: Category) -> list[str]:
        """Get key specs to display for a category."""
        if category == Category.TU_LANH:
            return [
                "Dung tích tổng", "Kiểu dáng", "Số người sử dụng",
                "Công nghệ tiết kiệm điện", "Điện năng tiêu thụ",
                "Công nghệ làm lạnh", "Số cửa", "Sản xuất tại",
            ]
        elif category == Category.MAY_LANH:
            return [
                "Công suất làm lạnh", "Phòng phù hợp", "Inverter",
                "Độ ồn", "Điện năng tiêu thụ",
            ]
        return list()

    def _build_comparison(self, recommendations: list[ProductRecommendation]) -> list[dict]:
        """Build a comparison table for the frontend."""
        if len(recommendations) < 2:
            return []

        key_specs = self._get_key_specs(recommendations[0].product.category)
        comparison = []
        for rec in recommendations:
            item = {
                "rank": rec.rank,
                "name": f"{rec.product.brand} {rec.product.name}",
                "price": rec.product.effective_price,
                "specs": {},
            }
            for spec in key_specs:
                item["specs"][spec] = rec.product.specs.get(spec, "—")
            comparison.append(item)

        return comparison

    async def _generate_intro(
        self,
        need: CustomerNeed,
        recommendations: list[ProductRecommendation],
    ) -> str:
        """Generate a natural intro for the recommendations."""
        guardrail_prompt = self._guardrail.build_guardrail_prompt()

        prompt = f"""{guardrail_prompt}

Bạn là trợ lý tư vấn tại Điện Máy Xanh. Viết một đoạn giới thiệu ngắn (3-4 câu) cho khách hàng 
trước khi hiển thị top {len(recommendations)} sản phẩm gợi ý.

Nhu cầu khách: {need.category.value}
- Ngân sách: {f'dưới {need.budget_max:,}đ' if need.budget_max else 'chưa xác định'}
- Ưu tiên: {', '.join(need.priorities) if need.priorities else 'chưa xác định'}
- Số người: {need.household_size or 'chưa xác định'}

Tóm tắt top {len(recommendations)}:
{chr(10).join(f'#{r.rank}: {r.product.brand} {r.product.name} - {r.summary}' for r in recommendations)}

Quy tắc:
- Dùng ngôn ngữ bình dân, thân thiện
- Gọi khách là "anh/chị"  
- Tóm tắt vì sao chọn 3 sản phẩm này
- KHÔNG liệt kê thông số, chỉ nêu điểm chính
"""
        try:
            intro = await llm_generate(prompt, temperature=0.4)
            return intro.strip()
        except Exception as e:
            logger.error(f"Failed to generate intro: {e}")
            return (
                f"Dựa trên nhu cầu của anh/chị, em đã chọn ra {len(recommendations)} "
                f"{need.category.value} phù hợp nhất. Mỗi sản phẩm có ưu nhược điểm riêng, "
                "em sẽ giải thích chi tiết bên dưới ạ:"
            )
