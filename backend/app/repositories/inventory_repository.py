from sqlalchemy.orm import Session

from app.models.inventory import Inventory
from app.models.product import Product


class InventoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, inventory: Inventory) -> Inventory:
        self.db.add(inventory)
        self.db.flush()
        return inventory

    def get_by_product_id(self, product_id: int) -> Inventory | None:
        return self.db.query(Inventory).filter(Inventory.product_id == product_id).first()

    def get_by_product_id_for_update(self, product_id: int) -> Inventory | None:
        return (
            self.db.query(Inventory)
            .filter(Inventory.product_id == product_id)
            .with_for_update()
            .first()
        )

    def list_with_products(self) -> list[tuple[Inventory, Product]]:
        return (
            self.db.query(Inventory, Product).join(Product, Inventory.product_id == Product.id)
            .order_by(Product.name).all()
        )

    def list_low_stock(self) -> list[tuple[Inventory, Product]]:
        return (
            self.db.query(Inventory, Product).join(Product, Inventory.product_id == Product.id)
            .filter(Inventory.quantity_on_hand <= Inventory.reorder_point).order_by(Product.name).all()
        )