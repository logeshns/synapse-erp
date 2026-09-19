from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.models.inventory import Inventory
from app.models.invoice import Invoice
from app.models.order import Order, OrderStatus
from app.models.order_item import OrderItem
from app.models.order_rejection import OrderRejection
from app.models.payment import Payment
from app.models.product import Product

_SOLD_STATUSES = [OrderStatus.CONFIRMED.value, OrderStatus.INVOICED.value, OrderStatus.COMPLETED.value]


def _since(days: int) -> datetime:
    return datetime.now(timezone.utc) - timedelta(days=days)


class AnalyticsService:
    """Every method here is the single source of truth for its numbers —
    both the /analytics/* routes and the Business Analyst Agent's tools
    call these same methods, so the API and the AI can never disagree
    about what a number means."""

    def __init__(self, db: Session):
        self.db = db

    def revenue(self, days: int = 30) -> dict:
        total = (
            self.db.query(func.coalesce(func.sum(Payment.amount), 0))
            .filter(Payment.status == "SUCCEEDED", Payment.paid_at >= _since(days))
            .scalar()
        )
        return {"period_days": days, "total_revenue": str(Decimal(total))}

    def orders_summary(self, days: int = 30) -> dict:
        rows = (
            self.db.query(Order.status, func.count(Order.id))
            .filter(Order.created_at >= _since(days))
            .group_by(Order.status)
            .all()
        )
        counts = {status.value: 0 for status in OrderStatus}
        for status, count in rows:
            counts[status] = count
        return {"period_days": days, "counts": counts, "total": sum(counts.values())}

    def sales_by_product(self, days: int = 30) -> list[dict]:
        rows = (
            self.db.query(Product.id, Product.name, func.sum(OrderItem.quantity), func.sum(OrderItem.line_total))
            .join(OrderItem, OrderItem.product_id == Product.id)
            .join(Order, OrderItem.order_id == Order.id)
            .filter(Order.status.in_(_SOLD_STATUSES), Order.created_at >= _since(days))
            .group_by(Product.id, Product.name)
            .order_by(func.sum(OrderItem.line_total).desc())
            .all()
        )
        return [
            {"product_id": pid, "product_name": name, "units_sold": int(qty or 0), "revenue": str(Decimal(rev or 0))}
            for pid, name, qty, rev in rows
        ]

    def inventory_summary(self) -> dict:
        rows = self.db.query(Inventory, Product).join(Product, Inventory.product_id == Product.id).all()
        total_value = sum((Decimal(i.quantity_on_hand) * p.unit_price for i, p in rows), Decimal("0.00"))
        low_stock_count = sum(1 for i, _ in rows if i.quantity_on_hand <= i.reorder_point)
        return {"total_value": str(total_value), "product_count": len(rows), "low_stock_count": low_stock_count}

    def online_vs_offline(self, days: int = 30) -> dict:
        rows = (
            self.db.query(Order.source, func.count(Order.id), func.coalesce(func.sum(Order.total), 0))
            .filter(Order.created_at >= _since(days), Order.status.in_(_SOLD_STATUSES))
            .group_by(Order.source)
            .all()
        )
        by_source = {"ONLINE": {"orders": 0, "revenue": "0.00"}, "OFFLINE": {"orders": 0, "revenue": "0.00"}}
        for source, count, revenue in rows:
            by_source[source] = {"orders": count, "revenue": str(Decimal(revenue))}
        return {"period_days": days, "by_source": by_source}

    def outstanding_payments(self) -> dict:
        rows = (
            self.db.query(Invoice.status, func.coalesce(func.sum(Invoice.total), 0))
            .filter(Invoice.status.in_(["UNPAID", "OVERDUE"]))
            .group_by(Invoice.status)
            .all()
        )
        result = {"UNPAID": "0.00", "OVERDUE": "0.00"}
        for status, total in rows:
            result[status] = str(Decimal(total))
        return result

    def lost_revenue(self, days: int = 30) -> dict:
        rows = (
            self.db.query(Order, OrderRejection)
            .join(OrderRejection, OrderRejection.order_id == Order.id)
            .filter(OrderRejection.reason_code == "INSUFFICIENT_STOCK", OrderRejection.created_at >= _since(days))
            .all()
        )
        total_lost = sum((o.total for o, _ in rows), Decimal("0.00"))

        product_qty: dict[int, int] = {}
        product_names: dict[int, str] = {}
        for o, _ in rows:
            for item in o.items:
                product_qty[item.product_id] = product_qty.get(item.product_id, 0) + item.quantity
                product_names[item.product_id] = item.product.name

        top_product = None
        if product_qty:
            top_id = max(product_qty, key=product_qty.get)
            top_product = product_names[top_id]

        return {"period_days": days, "order_count": len(rows), "total_lost_value": str(total_lost), "top_affected_product": top_product}

    def customer_count(self) -> int:
        return self.db.query(Customer).filter(Customer.is_active.is_(True)).count()

    def summary(self, days: int = 30) -> dict:
        return {
            "revenue": self.revenue(days),
            "orders": self.orders_summary(days),
            "inventory": self.inventory_summary(),
            "outstanding_payments": self.outstanding_payments(),
            "lost_revenue": self.lost_revenue(days),
            "customer_count": self.customer_count(),
        }