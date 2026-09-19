from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.permissions import require_roles
from app.db.session import get_db
from app.models.user import UserRole
from app.schemas.analytics import (
    InventorySummaryOut, LostRevenueOut, OnlineOfflineOut, OrdersSummaryOut,
    OutstandingPaymentsOut, RevenueOut, SalesByProductOut, SummaryOut,
)
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["analytics"])
VIEWERS = (UserRole.OWNER, UserRole.MANAGER)


@router.get("/summary", response_model=SummaryOut)
def summary(days: int = 30, db: Session = Depends(get_db), _=Depends(require_roles(*VIEWERS))):
    return AnalyticsService(db).summary(days=days)


@router.get("/revenue", response_model=RevenueOut)
def revenue(days: int = 30, db: Session = Depends(get_db), _=Depends(require_roles(*VIEWERS))):
    return AnalyticsService(db).revenue(days=days)


@router.get("/sales-by-product", response_model=list[SalesByProductOut])
def sales_by_product(days: int = 30, db: Session = Depends(get_db), _=Depends(require_roles(*VIEWERS))):
    return AnalyticsService(db).sales_by_product(days=days)


@router.get("/inventory", response_model=InventorySummaryOut)
def inventory(db: Session = Depends(get_db), _=Depends(require_roles(*VIEWERS))):
    return AnalyticsService(db).inventory_summary()


@router.get("/orders", response_model=OrdersSummaryOut)
def orders(days: int = 30, db: Session = Depends(get_db), _=Depends(require_roles(*VIEWERS))):
    return AnalyticsService(db).orders_summary(days=days)


@router.get("/payments", response_model=OutstandingPaymentsOut)
def payments(db: Session = Depends(get_db), _=Depends(require_roles(*VIEWERS))):
    return AnalyticsService(db).outstanding_payments()


@router.get("/online-offline", response_model=OnlineOfflineOut)
def online_offline(days: int = 30, db: Session = Depends(get_db), _=Depends(require_roles(*VIEWERS))):
    return AnalyticsService(db).online_vs_offline(days=days)


@router.get("/lost-revenue", response_model=LostRevenueOut)
def lost_revenue(days: int = 30, db: Session = Depends(get_db), _=Depends(require_roles(*VIEWERS))):
    return AnalyticsService(db).lost_revenue(days=days)