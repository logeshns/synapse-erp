from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ExtractedOrderItem(BaseModel):
    product_name: str = Field(min_length=1, description="The name of the product requested.")
    quantity: int = Field(gt=0, description="The quantity of the product requested.")


class ExtractedOrderData(BaseModel):
    customer_name: str | None = Field(None, description="The customer's full name or company name.")
    email: str | None = Field(None, description="The customer's email address, if mentioned.")
    phone: str | None = Field(None, description="The customer's phone number, if mentioned.")
    address: str | None = Field(None, description="The full delivery, shipping, or physical address, if mentioned.")
    items: list[ExtractedOrderItem] = Field(default_factory=list, description="The list of line items requested.")
    requested_delivery_date: str | None = Field(None, description="Requested delivery date, if any.")
    notes: str | None = Field(None, description="Any additional notes or instructions.")


class AIActionLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int | None
    agent_name: str
    model_name: str
    status: str
    error: str | None
    latency_ms: int
    created_at: datetime


class AIActionLogDetailOut(AIActionLogOut):
    request_text: str | None
    tool_calls: dict | None
    structured_output: dict | None
    human_decision: str | None
    request_id: str | None