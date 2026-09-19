from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.permissions import require_roles
from app.db.session import get_db
from app.models.user import UserRole
from app.schemas.product import ProductCreate, ProductOut
from app.services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["products"])

VIEWERS = (UserRole.SALES, UserRole.WAREHOUSE, UserRole.ACCOUNTANT, UserRole.MANAGER, UserRole.OWNER)


@router.post("", response_model=ProductOut, status_code=201)
def create_product(
    payload: ProductCreate,
    db: Session = Depends(get_db),
    _=Depends(require_roles(UserRole.WAREHOUSE, UserRole.OWNER)),
):
    return ProductService(db).create(payload)


@router.get("", response_model=list[ProductOut])
def list_products(db: Session = Depends(get_db), _=Depends(require_roles(*VIEWERS))):
    return ProductService(db).list()


@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db), _=Depends(require_roles(*VIEWERS))):
    return ProductService(db).get(product_id)