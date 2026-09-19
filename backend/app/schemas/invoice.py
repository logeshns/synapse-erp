from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class InvoiceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    invoice_number: str
    order_id: int
    subtotal: Decimal
    tax_total: Decimal
    discount_total: Decimal
    total: Decimal
    due_date: date
    status: str
    created_at: datetime