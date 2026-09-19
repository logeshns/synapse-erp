from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.permissions import require_roles
from app.db.session import get_db
from app.models.user import UserRole
from app.schemas.customer import CustomerCreate, CustomerOut
from app.services.customer_service import CustomerService

router = APIRouter(prefix="/customers", tags=["customers"])

VIEWERS = (UserRole.SALES, UserRole.WAREHOUSE, UserRole.ACCOUNTANT, UserRole.MANAGER, UserRole.OWNER)


@router.post("", response_model=CustomerOut, status_code=201)
def create_customer(
    payload: CustomerCreate, db: Session = Depends(get_db), _=Depends(require_roles(UserRole.SALES, UserRole.OWNER))
):
    return CustomerService(db).create(payload)


@router.get("", response_model=list[CustomerOut])
def list_customers(db: Session = Depends(get_db), _=Depends(require_roles(*VIEWERS))):
    return CustomerService(db).list()


@router.get("/{customer_id}", response_model=CustomerOut)
def get_customer(customer_id: int, db: Session = Depends(get_db), _=Depends(require_roles(*VIEWERS))):
    return CustomerService(db).get(customer_id)