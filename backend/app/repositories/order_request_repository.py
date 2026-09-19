from sqlalchemy.orm import Session

from app.models.order_request import OrderRequest


class OrderRequestRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, order_request: OrderRequest) -> OrderRequest:
        self.db.add(order_request)
        self.db.flush()
        return order_request

    def get_by_id(self, order_request_id: int) -> OrderRequest | None:
        return self.db.get(OrderRequest, order_request_id)

    def count(self) -> int:
        return self.db.query(OrderRequest).count()

    def list(self, review_status: str | None = None, source: str | None = None) -> list[OrderRequest]:
        query = self.db.query(OrderRequest)
        if review_status:
            query = query.filter(OrderRequest.review_status == review_status)
        if source:
            query = query.filter(OrderRequest.source == source)
        return query.order_by(OrderRequest.created_at.desc()).all()