from sqlalchemy.orm import Session

from app.exceptions import BusinessRuleException, NotFoundException
from app.models.customer import Customer
from app.repositories.customer_repository import CustomerRepository
from app.schemas.customer import CustomerCreate


class CustomerService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = CustomerRepository(db)

    def create(self, payload: CustomerCreate) -> Customer:
        if payload.email and self.repo.get_by_email(payload.email):
            raise BusinessRuleException(
                f"A customer with email '{payload.email}' already exists.", code="DUPLICATE_CUSTOMER"
            )

        customer = Customer(**payload.model_dump())
        self.repo.create(customer)
        self.db.commit()
        self.db.refresh(customer)
        return customer

    def get(self, customer_id: int) -> Customer:
        customer = self.repo.get_by_id(customer_id)
        if not customer:
            raise NotFoundException(f"Customer {customer_id} not found.")
        return customer

    def list(self) -> list[Customer]:
        return self.repo.list_active()