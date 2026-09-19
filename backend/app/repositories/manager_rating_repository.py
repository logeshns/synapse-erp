from sqlalchemy.orm import Session

from app.models.manager_rating import ManagerRating


class ManagerRatingRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, rating: ManagerRating) -> ManagerRating:
        self.db.add(rating)
        self.db.flush()
        return rating

    def list(self, employee_id: int | None = None) -> list[ManagerRating]:
        query = self.db.query(ManagerRating)
        if employee_id:
            query = query.filter(ManagerRating.employee_id == employee_id)
        return query.order_by(ManagerRating.created_at.desc()).all()