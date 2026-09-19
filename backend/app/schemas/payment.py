from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class CheckoutSessionOut(BaseModel):
    checkout_url: str
    session_id: str


class PaymentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    invoice_id: int
    provider: str
    provider_reference: str | None
    amount: Decimal
    status: str
    paid_at: datetime | None
    created_at: datetime