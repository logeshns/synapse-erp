from sqlalchemy.orm import Session

from app.models.customer import Customer


class CustomerRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, customer: Customer) -> Customer:
        self.db.add(customer)
        self.db.flush()
        return customer

    def get_by_id(self, customer_id: int) -> Customer | None:
        return self.db.get(Customer, customer_id)

    def get_by_email(self, email: str) -> Customer | None:
        return self.db.query(Customer).filter(Customer.email == email).first()

    def list_active(self) -> list[Customer]:
        return self.db.query(Customer).filter(Customer.is_active.is_(True)).order_by(Customer.name).all()