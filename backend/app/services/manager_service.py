from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.exceptions import BusinessRuleException
from app.models.manager_rating import ManagerRating
from app.models.order import Order, OrderStatus
from app.models.order_request import OrderRequest
from app.models.payment_receipt import PaymentReceipt
from app.models.user import User, UserRole
from app.repositories.manager_rating_repository import ManagerRatingRepository
from app.schemas.manager import ManagerRatingCreate

STAFF_ROLES = [UserRole.SALES.value, UserRole.WAREHOUSE.value, UserRole.ACCOUNTANT.value]


class ManagerService:
    def __init__(self, db: Session):
        self.db = db
        self.rating_repo = ManagerRatingRepository(db)

    def team_overview(self, days: int = 30) -> list[dict]:
        since = datetime.now(timezone.utc) - timedelta(days=days)
        staff = self.db.query(User).filter(User.role.in_(STAFF_ROLES), User.is_active.is_(True)).order_by(User.role, User.name).all()

        overview = []
        for user in staff:
            metrics = {"user_id": user.id, "name": user.name, "role": user.role, "period_days": days}

            if user.role == UserRole.SALES.value:
                metrics["order_requests_submitted"] = (
                    self.db.query(OrderRequest)
                    .filter(OrderRequest.submitted_by_sales_user_id == user.id, OrderRequest.created_at >= since)
                    .count()
                )
                metrics["orders_created"] = (
                    self.db.query(Order).filter(Order.created_by_user_id == user.id, Order.created_at >= since).count()
                )
            elif user.role == UserRole.WAREHOUSE.value:
                metrics["orders_confirmed"] = (
                    self.db.query(Order)
                    .filter(Order.warehouse_handled_by_user_id == user.id, Order.status == OrderStatus.CONFIRMED.value, Order.created_at >= since)
                    .count()
                )
                metrics["orders_rejected"] = (
                    self.db.query(Order)
                    .filter(Order.warehouse_handled_by_user_id == user.id, Order.status == OrderStatus.REJECTED.value, Order.created_at >= since)
                    .count()
                )
            elif user.role == UserRole.ACCOUNTANT.value:
                metrics["receipts_generated"] = (
                    self.db.query(PaymentReceipt)
                    .filter(PaymentReceipt.generated_by_user_id == user.id, PaymentReceipt.created_at >= since)
                    .count()
                )

            overview.append(metrics)
        return overview

    def add_rating(self, payload: ManagerRatingCreate, manager: User) -> ManagerRating:
        employee = self.db.get(User, payload.employee_id)
        if not employee or employee.role not in STAFF_ROLES:
            raise BusinessRuleException(f"Employee {payload.employee_id} not found or not ratable.", code="INVALID_EMPLOYEE")

        rating = ManagerRating(
            employee_id=payload.employee_id, manager_id=manager.id, period=payload.period,
            communication=payload.communication, accuracy=payload.accuracy,
            order_processing=payload.order_processing, customer_handling=payload.customer_handling,
            overall=payload.overall, comments=payload.comments,
        )
        self.rating_repo.create(rating)
        self.db.commit()
        self.db.refresh(rating)
        return rating

    def list_ratings(self, employee_id: int | None = None) -> list[ManagerRating]:
        return self.rating_repo.list(employee_id=employee_id)