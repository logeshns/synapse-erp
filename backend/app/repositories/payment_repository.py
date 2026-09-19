from sqlalchemy.orm import Session

from app.models.payment import Payment


class PaymentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, payment: Payment) -> Payment:
        self.db.add(payment)
        self.db.flush()
        return payment

    def get_by_id(self, payment_id: int) -> Payment | None:
        return self.db.get(Payment, payment_id)

    def get_by_stripe_event_id(self, stripe_event_id: str) -> Payment | None:
        return self.db.query(Payment).filter(Payment.stripe_event_id == stripe_event_id).first()

    def list(self, status: str | None = None) -> list[Payment]:
        query = self.db.query(Payment)
        if status:
            query = query.filter(Payment.status == status)
        return query.order_by(Payment.created_at.desc()).all()