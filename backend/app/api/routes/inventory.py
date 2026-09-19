from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.permissions import require_roles
from app.db.session import get_db
from app.models.user import UserRole
from app.schemas.inventory import InventoryAdjust, InventoryOut
from app.services.inventory_service import InventoryService

router = APIRouter(prefix="/inventory", tags=["inventory"])

VIEWERS = (UserRole.SALES, UserRole.WAREHOUSE, UserRole.ACCOUNTANT, UserRole.MANAGER, UserRole.OWNER)


@router.get("", response_model=list[InventoryOut])
def list_inventory(db: Session = Depends(get_db), _=Depends(require_roles(*VIEWERS))):
    return InventoryService(db).list_all()


@router.get("/low-stock", response_model=list[InventoryOut])
def low_stock(db: Session = Depends(get_db), _=Depends(require_roles(*VIEWERS))):
    return InventoryService(db).list_low_stock()


@router.patch("/{product_id}", response_model=InventoryOut)
def adjust_inventory(
    product_id: int,
    payload: InventoryAdjust,
    db: Session = Depends(get_db),
    _=Depends(require_roles(UserRole.WAREHOUSE, UserRole.OWNER)),
):
    return InventoryService(db).adjust(product_id, payload)