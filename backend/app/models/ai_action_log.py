from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AIActionLog(Base):
    __tablename__ = "ai_action_log"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    agent_name: Mapped[str] = mapped_column(String(50), nullable=False)
    request_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    tool_calls: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # populated from Phase 6
    structured_output: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    human_decision: Mapped[str | None] = mapped_column(String(20), nullable=True)  # wired up at Phase 13
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    error: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    request_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))