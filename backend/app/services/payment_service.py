from datetime import datetime, timezone
from decimal import Decimal

import stripe
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.exceptions import BusinessRuleException, NotFoundException, PaymentProviderException, PaymentWebhookException
from app.models.invoice import InvoiceStatus
from app.models.order import OrderStatus
from app.models.payment import Payment
from app.repositories.invoice_repository import InvoiceRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.payment_repository import PaymentRepository


class PaymentService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = PaymentRepository(db)
        self.invoice_repo = InvoiceRepository(db)
        self.order_repo = OrderRepository(db)

    def create_checkout_session(self, invoice_id: int) -> dict:
        invoice = self.invoice_repo.get_by_id(invoice_id)
        if not invoice:
            raise NotFoundException(f"Invoice {invoice_id} not found.")
        if invoice.status == InvoiceStatus.PAID.value:
            raise BusinessRuleException("This invoice is already paid.", code="ALREADY_PAID")
        if not settings.STRIPE_SECRET_KEY:
            raise PaymentProviderException("Stripe is not configured (STRIPE_SECRET_KEY missing).")

        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            session = stripe.checkout.Session.create(
                mode="payment",
                line_items=[{
                    "price_data": {"currency": "inr", "product_data": {"name": f"Invoice {invoice.invoice_number}"},
                                   "unit_amount": int(invoice.total * 100)},
                    "quantity": 1,
                }],
                # Routes directly to your new React UI pages with the database ID
                success_url=f"{settings.FRONTEND_URL}/payment-success?invoice_id={invoice.id}",
                cancel_url=f"{settings.FRONTEND_URL}/payment-failure",
                metadata={"invoice_id": str(invoice.id)},
            )
        except stripe.error.StripeError as exc:
            raise PaymentProviderException(f"Stripe checkout session creation failed: {exc}")

        return {"checkout_url": session.url, "session_id": session.id}

    def handle_webhook(self, payload: bytes, sig_header: str) -> None:
        try:
            event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
        except (stripe.error.SignatureVerificationError, ValueError) as exc:
            raise PaymentWebhookException(f"Invalid webhook signature or payload: {exc}")

        if event["type"] != "checkout.session.completed":
            return  # ignore every other event type — not an error

        if self.repo.get_by_stripe_event_id(event["id"]):
            return  # already processed — idempotent no-op

        session_obj = event["data"]["object"]
        try:
            invoice_id = int(session_obj["metadata"]["invoice_id"])
        except (KeyError, TypeError, ValueError):
            raise PaymentWebhookException("Webhook event is missing a valid invoice_id in metadata.")

        invoice = self.invoice_repo.get_by_id(invoice_id)
        if not invoice:
            raise PaymentWebhookException(f"Webhook references unknown invoice {invoice_id}.")

        payment = Payment(
            invoice_id=invoice.id, provider="stripe",
            provider_reference=session_obj.get("payment_intent") or session_obj.get("id"),
            stripe_event_id=event["id"], amount=Decimal(str(session_obj["amount_total"] / 100)),
            status="SUCCEEDED", paid_at=datetime.now(timezone.utc),
        )

        try:
            self.db.add(payment)
            invoice.status = InvoiceStatus.PAID.value
            order = self.order_repo.get_by_id(invoice.order_id)
            if order:
                order.status = OrderStatus.COMPLETED.value
            self.db.commit()
        except IntegrityError:
            # A concurrent delivery of the same event raced past the
            # get_by_stripe_event_id check — the unique constraint on
            # stripe_event_id is the real guarantee; this is defense in
            # depth, not the primary idempotency mechanism.
            self.db.rollback()

    def get(self, payment_id: int) -> Payment:
        payment = self.repo.get_by_id(payment_id)
        if not payment:
            raise NotFoundException(f"Payment {payment_id} not found.")
        return payment

    def list(self, status: str | None = None) -> list[Payment]:
        return self.repo.list(status=status)