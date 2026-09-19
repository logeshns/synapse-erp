from sqlalchemy.orm import Session

from app.core.logging import request_id_ctx_var
from app.models.ai_action_log import AIActionLog
from app.repositories.ai_action_log_repository import AIActionLogRepository


def log_ai_action(
    db: Session, *, user_id: int | None, agent_name: str, model_name: str, request_text: str | None,
    structured_output: dict | None, status: str, error: str | None, latency_ms: int,
    tool_calls: dict | None = None,
) -> None:
    AIActionLogRepository(db).create(
        AIActionLog(
            user_id=user_id, agent_name=agent_name, model_name=model_name,
            request_text=(request_text or "")[:2000], tool_calls=tool_calls,
            structured_output=structured_output, status=status, error=error,
            latency_ms=latency_ms, request_id=request_id_ctx_var.get(),
        )
    )