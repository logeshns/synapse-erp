from sqlalchemy.orm import Session

from app.exceptions import BusinessRuleException, NotFoundException
from app.models.inventory import Inventory
from app.models.product import Product
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.product import ProductCreate


class ProductService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ProductRepository(db)
        self.inventory_repo = InventoryRepository(db)

    def create(self, payload: ProductCreate) -> Product:
        if self.repo.get_by_sku(payload.sku):
            raise BusinessRuleException(f"A product with SKU '{payload.sku}' already exists.", code="DUPLICATE_SKU")

        data = payload.model_dump(exclude={"initial_quantity", "reorder_point"})
        product = Product(**data)
        self.repo.create(product)

        # Every product gets an inventory row at creation — the rest of the
        # system assumes inventory always exists for an active product.
        inventory = Inventory(
            product_id=product.id,
            quantity_on_hand=payload.initial_quantity,
            reorder_point=payload.reorder_point,
        )
        self.inventory_repo.create(inventory)

        self.db.commit()
        self.db.refresh(product)
        return product

    def get(self, product_id: int) -> Product:
        product = self.repo.get_by_id(product_id)
        if not product:
            raise NotFoundException(f"Product {product_id} not found.")
        return product

    def list(self) -> list[Product]:
        return self.repo.list_active()