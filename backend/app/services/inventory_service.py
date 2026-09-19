from sqlalchemy.orm import Session

from app.exceptions import NotFoundException
from app.models.inventory import Inventory
from app.repositories.inventory_repository import InventoryRepository
from app.schemas.inventory import InventoryAdjust


class InventoryService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = InventoryRepository(db)

    def list_all(self) -> list[dict]:
        return [self._to_dict(inv, prod) for inv, prod in self.repo.list_with_products()]

    def list_low_stock(self) -> list[dict]:
        return [self._to_dict(inv, prod) for inv, prod in self.repo.list_low_stock()]

    def adjust(self, product_id: int, payload: InventoryAdjust) -> dict:
        inventory = self.repo.get_by_product_id(product_id)
        if not inventory:
            raise NotFoundException(f"No inventory record for product {product_id}.")

        inventory.quantity_on_hand = payload.quantity_on_hand
        if payload.reorder_point is not None:
            inventory.reorder_point = payload.reorder_point

        self.db.commit()
        self.db.refresh(inventory)
        return self._to_dict(inventory, inventory.product)

    @staticmethod
    def _to_dict(inventory: Inventory, product) -> dict:
        return {
            "product_id": product.id,
            "product_name": product.name,
            "sku": product.sku,
            "quantity_on_hand": inventory.quantity_on_hand,
            "reorder_point": inventory.reorder_point,
        }