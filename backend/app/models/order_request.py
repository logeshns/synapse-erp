import enum
from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class OrderRequestSource(str, enum.Enum):
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"


class OrderRequestReviewStatus(str, enum.Enum):
    PENDING_REVIEW = "PENDING_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class OrderRequest(Base):
    __tablename__ = "order_requests"

    id: Mapped[int] = mapped_column(primary_key=True)
    request_number: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    source: Mapped[str] = mapped_column(String(10), nullable=False)
    customer_id: Mapped[int | None] = mapped_column(ForeignKey("customers.id"), nullable=True)
    submitted_by_sales_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Declared now, used starting Phase 4 — schema doesn't change when AI lands.
    ai_status: Mapped[str] = mapped_column(String(20), default="NOT_STARTED", nullable=False)
    # Generic JSON (not Postgres JSONB) — keeps SQLite test runs working
    # without a Postgres test fixture; we don't need JSONB's containment
    # queries for this project's scope.
    extracted_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    review_status: Mapped[str] = mapped_column(
        String(20), default=OrderRequestReviewStatus.PENDING_REVIEW.value, nullable=False
    )
    rejection_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    order: Mapped["Order"] = relationship(back_populates="order_request", uselist=False)