from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.exceptions import BusinessRuleException, NotFoundException
from app.models.invoice import Invoice, InvoiceStatus
from app.models.order import OrderStatus
from app.repositories.invoice_repository import InvoiceRepository
from app.repositories.order_repository import OrderRepository
from app.utils.numbering import generate_number

DUE_IN_DAYS = 15


class InvoiceService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = InvoiceRepository(db)
        self.order_repo = OrderRepository(db)

    def generate(self, order_id: int, user_id: int) -> Invoice:
        order = self.order_repo.get_by_id(order_id)
        if not order:
            raise NotFoundException(f"Order {order_id} not found.")

        existing = self.repo.get_by_order_id(order_id)
        if existing:
            return existing  # idempotent — one invoice per order, ever

        if order.status != OrderStatus.CONFIRMED.value:
            raise BusinessRuleException(f"Cannot generate an invoice for an order in state '{order.status}'.", code="INVALID_ORDER_STATE")

        invoice = Invoice(
            invoice_number=generate_number("INV", self.repo.count()), order_id=order.id,
            created_by_user_id=user_id,
            subtotal=order.subtotal, tax_total=order.tax_total, discount_total=order.discount_total,
            total=order.total, due_date=date.today() + timedelta(days=DUE_IN_DAYS), status=InvoiceStatus.UNPAID.value,
        )
        self.repo.create(invoice)
        order.status = OrderStatus.INVOICED.value

        self.db.commit()
        self.db.refresh(invoice)
        return invoice

    def get(self, invoice_id: int) -> Invoice:
        invoice = self.repo.get_by_id(invoice_id)
        if not invoice:
            raise NotFoundException(f"Invoice {invoice_id} not found.")
        return invoice

    def list(self, status: str | None = None) -> list[Invoice]:
        return self.repo.list(status=status)