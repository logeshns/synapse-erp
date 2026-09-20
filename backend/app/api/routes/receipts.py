from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.permissions import require_roles
from app.db.session import get_db
from app.documents.pdf.renderer import render_receipt_pdf
from app.models.customer import Customer
from app.models.user import User, UserRole
from app.schemas.receipt import PaymentReceiptOut
from app.services.receipt_service import ReceiptService

router = APIRouter(prefix="/receipts", tags=["receipts"])
ACCOUNTING = (UserRole.ACCOUNTANT, UserRole.OWNER)


@router.post("/generate/{payment_id}", response_model=PaymentReceiptOut, status_code=201)
def generate_receipt(payment_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_roles(*ACCOUNTING))):
    return ReceiptService(db).generate(payment_id, user_id=current_user.id)


@router.get("/{receipt_id}/pdf")
def get_receipt_pdf(receipt_id: int, db: Session = Depends(get_db), _=Depends(require_roles(*ACCOUNTING))):
    receipt = ReceiptService(db).get(receipt_id)
    payment = receipt.payment
    invoice = payment.invoice
    customer = db.get(Customer, invoice.order.customer_id)
    
    pdf_bytes = render_receipt_pdf(receipt, payment, invoice, customer)
    return Response(
        content=pdf_bytes, 
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{receipt.receipt_number}.pdf"'}
    )