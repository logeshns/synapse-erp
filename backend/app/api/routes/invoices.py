from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.permissions import require_roles
from app.db.session import get_db
from app.documents.pdf.renderer import render_invoice_pdf
from app.models.customer import Customer
from app.models.user import UserRole
from app.schemas.invoice import InvoiceOut
from app.services.invoice_service import InvoiceService

router = APIRouter(prefix="/invoices", tags=["invoices"])

VIEWERS = (UserRole.SALES, UserRole.WAREHOUSE, UserRole.ACCOUNTANT, UserRole.OWNER)
GENERATORS = (UserRole.ACCOUNTANT, UserRole.WAREHOUSE, UserRole.OWNER)


@router.post("/generate/{order_id}", response_model=InvoiceOut, status_code=201)
def generate_invoice(order_id: int, db: Session = Depends(get_db), _=Depends(require_roles(*GENERATORS))):
    return InvoiceService(db).generate(order_id)


@router.get("", response_model=list[InvoiceOut])
def list_invoices(status: str | None = None, db: Session = Depends(get_db), _=Depends(require_roles(*VIEWERS))):
    return InvoiceService(db).list(status=status)


@router.get("/{invoice_id}", response_model=InvoiceOut)
def get_invoice(invoice_id: int, db: Session = Depends(get_db), _=Depends(require_roles(*VIEWERS))):
    return InvoiceService(db).get(invoice_id)


@router.get("/{invoice_id}/pdf")
def get_invoice_pdf(invoice_id: int, db: Session = Depends(get_db), _=Depends(require_roles(*VIEWERS))):
    invoice = InvoiceService(db).get(invoice_id)
    order = invoice.order
    customer = db.get(Customer, order.customer_id)
    pdf_bytes = render_invoice_pdf(invoice, order, customer)
    return Response(content=pdf_bytes, media_type="application/pdf",
                     headers={"Content-Disposition": f'inline; filename="{invoice.invoice_number}.pdf"'})