from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ProductCreate(BaseModel):
    sku: str
    name: str
    category: str | None = None
    description: str | None = None
    unit_price: Decimal = Field(gt=0)
    tax_rate: Decimal = Field(default=Decimal("0.18"), ge=0, le=1)
    initial_quantity: int = Field(default=0, ge=0)
    reorder_point: int = Field(default=0, ge=0)


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sku: str
    name: str
    category: str | None
    description: str | None
    unit_price: Decimal
    tax_rate: Decimal
    is_active: bool