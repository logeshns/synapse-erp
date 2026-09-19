from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.ai.agents.business_analyst_agent import BusinessAnalystAgent
from app.ai.agents.inventory_agent import InventoryAgent
from app.ai.audit import log_ai_action
from app.ai.provider import AIProvider, get_ai_provider
from app.core.config import settings
from app.core.permissions import require_roles
from app.db.session import get_db
from app.exceptions import NotFoundException
from app.models.user import User, UserRole
from app.repositories.ai_action_log_repository import AIActionLogRepository
from app.schemas.agent import AskRequest, AskResponse
from app.schemas.ai import AIActionLogDetailOut, AIActionLogOut

router = APIRouter(prefix="/ai", tags=["ai"])
INVENTORY_ASKERS = (UserRole.WAREHOUSE, UserRole.OWNER)
ANALYST_ASKERS = (UserRole.OWNER, UserRole.MANAGER)
AUDIT_VIEWERS = (UserRole.OWNER,)


@router.post("/inventory/ask", response_model=AskResponse)
def ask_inventory_assistant(
    payload: AskRequest, db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(*INVENTORY_ASKERS)),
    ai_provider: AIProvider = Depends(get_ai_provider),
):
    result = InventoryAgent(ai_provider, db).ask(payload.question)
    log_ai_action(
        db, user_id=current_user.id, agent_name="InventoryAgent", model_name=settings.AI_MODEL,
        request_text=payload.question, structured_output={"answer": result.answer},
        tool_calls={"trace": [t.model_dump() for t in result.trace]},
        status=result.status, error=result.error, latency_ms=result.latency_ms,
    )
    db.commit()
    return AskResponse(status=result.status, answer=result.answer, trace=result.trace, error=result.error, latency_ms=result.latency_ms)


@router.post("/business-analyst/ask", response_model=AskResponse)
def ask_business_analyst(
    payload: AskRequest, db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(*ANALYST_ASKERS)),
    ai_provider: AIProvider = Depends(get_ai_provider),
):
    result = BusinessAnalystAgent(ai_provider, db).ask(payload.question)
    log_ai_action(
        db, user_id=current_user.id, agent_name="BusinessAnalystAgent", model_name=settings.AI_MODEL,
        request_text=payload.question, structured_output={"answer": result.answer},
        tool_calls={"trace": [t.model_dump() for t in result.trace]},
        status=result.status, error=result.error, latency_ms=result.latency_ms,
    )
    db.commit()
    return AskResponse(status=result.status, answer=result.answer, trace=result.trace, error=result.error, latency_ms=result.latency_ms)


@router.get("/audit-log", response_model=list[AIActionLogOut])
def list_audit_log(
    agent_name: str | None = None, status: str | None = None, limit: int = 50,
    db: Session = Depends(get_db), _=Depends(require_roles(*AUDIT_VIEWERS)),
):
    return AIActionLogRepository(db).list(agent_name=agent_name, status=status, limit=min(limit, 200))


@router.get("/audit-log/{log_id}", response_model=AIActionLogDetailOut)
def get_audit_log_entry(log_id: int, db: Session = Depends(get_db), _=Depends(require_roles(*AUDIT_VIEWERS))):
    log = AIActionLogRepository(db).get_by_id(log_id)
    if not log:
        raise NotFoundException(f"AI action log entry {log_id} not found.")
    return log