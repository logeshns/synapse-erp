import enum
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class RejectionReasonCode(str, enum.Enum):
    INSUFFICIENT_STOCK = "INSUFFICIENT_STOCK"
    CUSTOMER_REQUEST = "CUSTOMER_REQUEST"
    PRICING_ISSUE = "PRICING_ISSUE"
    OTHER = "OTHER"


class OrderRejection(Base):
    __tablename__ = "order_rejections"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), unique=True, nullable=False)
    reason_code: Mapped[str] = mapped_column(String(30), nullable=False)
    details: Mapped[str] = mapped_column(Text, nullable=False)
    ai_explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    order: Mapped["Order"] = relationship(back_populates="rejection")