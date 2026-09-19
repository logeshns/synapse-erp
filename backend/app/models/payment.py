from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True)
    invoice_id: Mapped[int] = mapped_column(ForeignKey("invoices.id"), nullable=False)
    provider: Mapped[str] = mapped_column(String(30), nullable=False, default="stripe")
    provider_reference: Mapped[str | None] = mapped_column(String(255), nullable=True)
    stripe_event_id: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    invoice: Mapped["Invoice"] = relationship(back_populates="payments")
    receipt: Mapped["PaymentReceipt"] = relationship(back_populates="payment", uselist=False)