from sqlalchemy.orm import Session

from app.exceptions import BusinessRuleException, NotFoundException
from app.models.payment_receipt import PaymentReceipt
from app.repositories.payment_receipt_repository import PaymentReceiptRepository
from app.repositories.payment_repository import PaymentRepository
from app.utils.numbering import generate_number


class ReceiptService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = PaymentReceiptRepository(db)
        self.payment_repo = PaymentRepository(db)

    def generate(self, payment_id: int, user_id: int) -> PaymentReceipt:
        payment = self.payment_repo.get_by_id(payment_id)
        if not payment:
            raise NotFoundException(f"Payment {payment_id} not found.")
        if payment.status != "SUCCEEDED":
            raise BusinessRuleException("A receipt can only be generated for a succeeded payment.", code="PAYMENT_NOT_SUCCEEDED")

        existing = self.repo.get_by_payment_id(payment_id)
        if existing:
            return existing

        receipt = PaymentReceipt(
            payment_id=payment.id, 
            receipt_number=generate_number("RCPT", self.repo.count()),
            generated_by_user_id=user_id
        )
        self.repo.create(receipt)
        self.db.commit()
        self.db.refresh(receipt)
        return receipt

    def get(self, receipt_id: int) -> PaymentReceipt:
        receipt = self.repo.get_by_id(receipt_id)
        if not receipt:
            raise NotFoundException(f"Receipt {receipt_id} not found.")
        return receipt