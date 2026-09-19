from sqlalchemy.orm import Session

from app.models.payment_receipt import PaymentReceipt


class PaymentReceiptRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, receipt: PaymentReceipt) -> PaymentReceipt:
        self.db.add(receipt)
        self.db.flush()
        return receipt

    def get_by_id(self, receipt_id: int) -> PaymentReceipt | None:
        return self.db.get(PaymentReceipt, receipt_id)

    def get_by_payment_id(self, payment_id: int) -> PaymentReceipt | None:
        return self.db.query(PaymentReceipt).filter(PaymentReceipt.payment_id == payment_id).first()

    def count(self) -> int:
        return self.db.query(PaymentReceipt).count()