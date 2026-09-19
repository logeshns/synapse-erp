from sqlalchemy.orm import Session

from app.models.invoice import Invoice


class InvoiceRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, invoice: Invoice) -> Invoice:
        self.db.add(invoice)
        self.db.flush()
        return invoice

    def get_by_id(self, invoice_id: int) -> Invoice | None:
        return self.db.get(Invoice, invoice_id)

    def get_by_order_id(self, order_id: int) -> Invoice | None:
        return self.db.query(Invoice).filter(Invoice.order_id == order_id).first()

    def count(self) -> int:
        return self.db.query(Invoice).count()

    def list(self, status: str | None = None) -> list[Invoice]:
        query = self.db.query(Invoice)
        if status:
            query = query.filter(Invoice.status == status)
        return query.order_by(Invoice.created_at.desc()).all()