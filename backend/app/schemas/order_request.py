from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class OrderRequestCreate(BaseModel):
    source: str = Field(pattern="^(ONLINE|OFFLINE)$")
    customer_id: int | None = None
    raw_text: str | None = Field(default=None, max_length=4000)


class OrderRequestOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    request_number: str
    source: str
    customer_id: int | None
    submitted_by_sales_user_id: int | None
    raw_text: str | None
    ai_status: str
    extracted_data: dict | None
    review_status: str
    rejection_reason: str | None
    created_at: datetime


class ApprovalItem(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)
    discount: float = Field(default=0, ge=0)


class OrderRequestApprove(BaseModel):
    customer_id: int
    items: list[ApprovalItem] = Field(min_length=1)


class OrderRequestReject(BaseModel):
    reason: str = Field(min_length=3, max_length=500)