from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class OrderItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    quantity: int
    unit_price_snapshot: Decimal
    tax_rate_snapshot: Decimal
    discount: Decimal
    line_total: Decimal


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_number: str
    order_request_id: int
    customer_id: int
    source: str
    status: str
    subtotal: Decimal
    tax_total: Decimal
    discount_total: Decimal
    total: Decimal
    created_at: datetime
    items: list[OrderItemOut]


class StockCheckItem(BaseModel):
    product_id: int
    product_name: str
    requested: int
    available: int
    shortage: int


class StockCheckResponse(BaseModel):
    order_id: int
    sufficient: bool
    items: list[StockCheckItem]


class OrderRejectRequest(BaseModel):
    reason_code: str = Field(pattern="^(INSUFFICIENT_STOCK|CUSTOMER_REQUEST|PRICING_ISSUE|OTHER)$")
    details: str | None = Field(default=None, max_length=1000)
    
class RejectionInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    reason_code: str
    details: str
    ai_explanation: str | None


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_number: str
    order_request_id: int
    customer_id: int
    source: str
    status: str
    subtotal: Decimal
    tax_total: Decimal
    discount_total: Decimal
    total: Decimal
    created_at: datetime
    items: list[OrderItemOut]
    rejection: RejectionInfo | None = None