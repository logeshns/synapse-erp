from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.permissions import require_roles
from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.manager import ManagerRatingCreate, ManagerRatingOut, TeamMemberMetrics
from app.services.manager_service import ManagerService

router = APIRouter(prefix="/manager", tags=["manager"])
MANAGERS = (UserRole.MANAGER, UserRole.OWNER)


@router.get("/team", response_model=list[TeamMemberMetrics])
def team_overview(days: int = 30, db: Session = Depends(get_db), _=Depends(require_roles(*MANAGERS))):
    return ManagerService(db).team_overview(days=days)


@router.post("/ratings", response_model=ManagerRatingOut, status_code=201)
def add_rating(payload: ManagerRatingCreate, db: Session = Depends(get_db), current_user: User = Depends(require_roles(*MANAGERS))):
    return ManagerService(db).add_rating(payload, current_user)


@router.get("/ratings", response_model=list[ManagerRatingOut])
def list_ratings(employee_id: int | None = None, db: Session = Depends(get_db), _=Depends(require_roles(*MANAGERS))):
    return ManagerService(db).list_ratings(employee_id=employee_id)