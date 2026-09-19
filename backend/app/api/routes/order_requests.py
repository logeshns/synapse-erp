from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.ai.provider import AIProvider, get_ai_provider
from app.core.permissions import require_roles
from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.order import OrderOut
from app.schemas.order_request import (
    OrderRequestApprove,
    OrderRequestCreate,
    OrderRequestOut,
    OrderRequestReject,
)
from app.services.order_request_service import OrderRequestService

router = APIRouter(prefix="/order-requests", tags=["order-requests"])

REVIEWERS = (UserRole.SALES, UserRole.OWNER)
VIEWERS = (UserRole.SALES, UserRole.WAREHOUSE, UserRole.OWNER)


@router.post("", response_model=OrderRequestOut, status_code=201)
def create_order_request(
    payload: OrderRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(*REVIEWERS)),
):
    return OrderRequestService(db).create(payload, current_user)


@router.get("", response_model=list[OrderRequestOut])
def list_order_requests(
    review_status: str | None = None,
    source: str | None = None,
    db: Session = Depends(get_db),
    _=Depends(require_roles(*VIEWERS)),
):
    return OrderRequestService(db).list(review_status=review_status, source=source)


@router.get("/{order_request_id}", response_model=OrderRequestOut)
def get_order_request(order_request_id: int, db: Session = Depends(get_db), _=Depends(require_roles(*VIEWERS))):
    return OrderRequestService(db).get(order_request_id)


@router.post("/{order_request_id}/extract", response_model=OrderRequestOut)
def extract_order_request(
    order_request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(*REVIEWERS)),
    ai_provider: AIProvider = Depends(get_ai_provider),
):
    return OrderRequestService(db).extract(order_request_id, current_user, ai_provider)


@router.post("/{order_request_id}/approve", response_model=OrderOut)
def approve_order_request(
    order_request_id: int,
    payload: OrderRequestApprove,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(*REVIEWERS)),
):
    return OrderRequestService(db).approve(order_request_id, payload, current_user)


@router.post("/{order_request_id}/reject", response_model=OrderRequestOut)
def reject_order_request(
    order_request_id: int,
    payload: OrderRequestReject,
    db: Session = Depends(get_db),
    _=Depends(require_roles(*REVIEWERS)),
):
    return OrderRequestService(db).reject(order_request_id, payload)