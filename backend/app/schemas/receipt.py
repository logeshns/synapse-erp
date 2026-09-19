from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PaymentReceiptOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    payment_id: int
    receipt_number: str
    created_at: datetime