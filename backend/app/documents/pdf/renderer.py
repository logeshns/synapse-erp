from io import BytesIO
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from xhtml2pdf import pisa

from app.exceptions import PDFException
from app.models.customer import Customer
from app.models.invoice import Invoice
from app.models.order import Order
from app.models.payment import Payment
from app.models.payment_receipt import PaymentReceipt

TEMPLATE_DIR = Path(__file__).parent
_env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)), autoescape=select_autoescape(["html"]))

COMPANY = {"name": "Synapse ERP Pvt Ltd", "address": "42 Anna Salai, Chennai, TN 600002, India", "gstin": "33AAAAA0000A1Z5"}

def _render_pdf(html: str) -> bytes:
    result = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=result)
    if pisa_status.err:
        raise PDFException(f"Could not render PDF: {pisa_status.err}")
    return result.getvalue()

def render_invoice_pdf(invoice: Invoice, order: Order, customer: Customer) -> bytes:
    html = _env.get_template("invoice_template.html").render(invoice=invoice, order=order, customer=customer, company=COMPANY)
    return _render_pdf(html)

def render_receipt_pdf(receipt: PaymentReceipt, payment: Payment, invoice: Invoice, customer: Customer) -> bytes:
    html = _env.get_template("receipt_template.html").render(receipt=receipt, payment=payment, invoice=invoice, customer=customer, company=COMPANY)
    return _render_pdf(html)