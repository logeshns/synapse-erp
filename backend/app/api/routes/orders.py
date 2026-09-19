from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.ai.provider import AIProvider, get_ai_provider
from app.core.permissions import require_roles
from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.order import OrderOut, OrderRejectRequest, StockCheckResponse
from app.services.order_service import OrderService

router = APIRouter(prefix="/orders", tags=["orders"])
VIEWERS = (UserRole.SALES, UserRole.WAREHOUSE, UserRole.OWNER)
WAREHOUSE_STAFF = (UserRole.WAREHOUSE, UserRole.OWNER)


@router.get("", response_model=list[OrderOut])
def list_orders(status: str | None = None, db: Session = Depends(get_db), _=Depends(require_roles(*VIEWERS))):
    return OrderService(db).list(status=status)


@router.get("/{order_id}", response_model=OrderOut)
def get_order(order_id: int, db: Session = Depends(get_db), _=Depends(require_roles(*VIEWERS))):
    return OrderService(db).get(order_id)


@router.get("/{order_id}/stock-check", response_model=StockCheckResponse)
def stock_check(order_id: int, db: Session = Depends(get_db), _=Depends(require_roles(*WAREHOUSE_STAFF))):
    return OrderService(db).stock_check(order_id)


@router.post("/{order_id}/confirm", response_model=OrderOut)
def confirm_order(order_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_roles(*WAREHOUSE_STAFF))):
    return OrderService(db).confirm(order_id, current_user)


@router.post("/{order_id}/reject", response_model=OrderOut)
def reject_order(
    order_id: int, payload: OrderRejectRequest, db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(*WAREHOUSE_STAFF)),
    ai_provider: AIProvider = Depends(get_ai_provider),
):
    return OrderService(db).reject(order_id, payload, current_user, ai_provider)