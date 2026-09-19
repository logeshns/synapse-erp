from pydantic import BaseModel, ConfigDict, Field


class InventoryAdjust(BaseModel):
    quantity_on_hand: int = Field(ge=0)
    reorder_point: int | None = Field(default=None, ge=0)


class InventoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_id: int
    product_name: str
    sku: str
    quantity_on_hand: int
    reorder_point: int