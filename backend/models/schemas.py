"""Pydantic models / schemas for the application."""
from __future__ import annotations

from enum import Enum
from typing import Any
from pydantic import BaseModel, Field


# ── Enums ──────────────────────────────────────────────────────────

class Category(str, Enum):
    TU_LANH = "tủ lạnh"
    MAY_LANH = "máy lạnh"
    DIEN_THOAI = "điện thoại"
    LAPTOP = "laptop"
    TAI_NGHE = "tai nghe"
    ROBOT = "robot"
    UNKNOWN = "unknown"


class ConversationState(str, Enum):
    GREETING = "greeting"
    NEED_COLLECTION = "need_collection"
    FOLLOW_UP = "follow_up"
    RETRIEVAL = "retrieval"
    COMPARISON = "comparison"
    DECISION_SUPPORT = "decision_support"
    REFINEMENT = "refinement"


class SSEEventType(str, Enum):
    TEXT = "text"
    PRODUCTS = "products"
    COMPARISON = "comparison"
    NEED_SUMMARY = "need_summary"
    FOLLOW_UP = "follow_up"
    ERROR = "error"
    DONE = "done"


# ── Customer Need ──────────────────────────────────────────────────

class CustomerNeed(BaseModel):
    """Structured representation of what the customer wants."""
    category: Category = Category.UNKNOWN
    budget_min: int | None = None
    budget_max: int | None = None
    household_size: int | None = None
    room_area: float | None = None          # m² (for AC)
    room_type: str | None = None            # phòng ngủ, phòng khách
    sun_exposure: bool | None = None        # nắng trực tiếp?
    usage_purpose: list[str] = Field(default_factory=list)  # chụp ảnh, game, công việc
    priorities: list[str] = Field(default_factory=list)      # tiết kiệm điện, êm, bền
    brand_preference: list[str] = Field(default_factory=list)
    installment: bool | None = None         # trả góp?
    wants_promotion: bool | None = None     # muốn khuyến mãi?
    additional_notes: str = ""
    missing_info: list[str] = Field(default_factory=list)
    raw_input: str = ""

    def is_sufficient(self) -> bool:
        """Check if we have enough info to make recommendations."""
        if self.category == Category.UNKNOWN:
            return False
        has_budget = self.budget_max is not None
        has_basic_context = len(self.priorities) > 0 or len(self.usage_purpose) > 0
        if self.category == Category.TU_LANH:
            return has_budget and self.household_size is not None
        elif self.category == Category.MAY_LANH:
            return has_budget and self.room_area is not None
        else:
            return has_budget and has_basic_context


# ── Product ────────────────────────────────────────────────────────

class Product(BaseModel):
    """A product from the catalog."""
    id: str
    model_code: str = ""
    sku: str = ""
    category: Category = Category.UNKNOWN
    brand: str = ""
    name: str = ""
    specs: dict[str, Any] = Field(default_factory=dict)
    price_original: int | None = None       # giá gốc (VND)
    price_promo: int | None = None          # giá khuyến mãi (VND)
    promotion_gift: str = ""                # khuyến mãi quà
    description: str = ""                   # human-readable summary
    image_url: str = ""

    @property
    def effective_price(self) -> int | None:
        return self.price_promo or self.price_original


class ProductRecommendation(BaseModel):
    """A recommended product with reasoning."""
    product: Product
    rank: int
    match_score: float = 0.0
    strengths: list[str] = Field(default_factory=list)    # ✅ reasons
    trade_offs: list[str] = Field(default_factory=list)   # ⚠️ reasons
    summary: str = ""                                      # one-line verdict
    data_sources: list[str] = Field(default_factory=list)  # citation


# ── Conversation ───────────────────────────────────────────────────

class ConversationContext(BaseModel):
    """Tracks the state of a conversation."""
    conversation_id: str
    state: ConversationState = ConversationState.GREETING
    customer_need: CustomerNeed = Field(default_factory=CustomerNeed)
    history: list[dict[str, str]] = Field(default_factory=list)  # role/content
    recommended_products: list[ProductRecommendation] = Field(default_factory=list)
    follow_up_count: int = 0
    max_follow_ups: int = 3


# ── API Models ─────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str
    conversation_id: str = ""


class SSEEvent(BaseModel):
    type: SSEEventType
    content: Any
