from sqlalchemy.orm import Session, joinedload

from app.models.order import Order


class OrderRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, order: Order) -> Order:
        self.db.add(order)
        self.db.flush()
        return order

    def get_by_id(self, order_id: int) -> Order | None:
        return (
            self.db.query(Order)
            .options(joinedload(Order.items), joinedload(Order.rejection))
            .filter(Order.id == order_id)
            .first()
        )

    def get_by_order_request_id(self, order_request_id: int) -> Order | None:
        return self.db.query(Order).filter(Order.order_request_id == order_request_id).first()

    def count(self) -> int:
        return self.db.query(Order).count()

    def list(self, status: str | None = None) -> list[Order]:
        query = self.db.query(Order).options(joinedload(Order.items), joinedload(Order.rejection))
        if status:
            query = query.filter(Order.status == status)
        return query.order_by(Order.created_at.desc()).all()