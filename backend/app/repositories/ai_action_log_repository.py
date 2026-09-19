from sqlalchemy.orm import Session

from app.models.ai_action_log import AIActionLog


class AIActionLogRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, log: AIActionLog) -> AIActionLog:
        self.db.add(log)
        self.db.flush()
        return log

    def get_by_id(self, log_id: int) -> AIActionLog | None:
        return self.db.get(AIActionLog, log_id)

    def list(self, agent_name: str | None = None, status: str | None = None, limit: int = 50) -> list[AIActionLog]:
        query = self.db.query(AIActionLog)
        if agent_name:
            query = query.filter(AIActionLog.agent_name == agent_name)
        if status:
            query = query.filter(AIActionLog.status == status)
        return query.order_by(AIActionLog.created_at.desc()).limit(limit).all()