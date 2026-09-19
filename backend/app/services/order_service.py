from decimal import Decimal

from sqlalchemy.orm import Session

from app.ai.agents.rejection_explanation_agent import RejectionExplanationAgent
from app.ai.audit import log_ai_action
from app.ai.provider import AIProvider
from app.core.config import settings
from app.exceptions import BusinessRuleException, NotFoundException
from app.models.order import Order, OrderStatus
from app.models.order_item import OrderItem
from app.models.order_rejection import OrderRejection
from app.models.order_request import OrderRequest
from app.models.user import User
from app.repositories.customer_repository import CustomerRepository
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.order import OrderRejectRequest
from app.schemas.order_request import OrderRequestApprove
from app.utils.numbering import generate_number


class OrderService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = OrderRepository(db)
        self.product_repo = ProductRepository(db)
        self.customer_repo = CustomerRepository(db)
        self.inventory_repo = InventoryRepository(db)

    def create_from_request(self, order_request: OrderRequest, payload: OrderRequestApprove, created_by_user_id: int) -> Order:
        existing = self.repo.get_by_order_request_id(order_request.id)
        if existing:
            return self.repo.get_by_id(existing.id)

        customer = self.customer_repo.get_by_id(payload.customer_id)
        if not customer or not customer.is_active:
            raise BusinessRuleException(f"Customer {payload.customer_id} not found or inactive.", code="INVALID_CUSTOMER")

        try:
            order = Order(
                order_number=generate_number("ORD", self.repo.count()), order_request_id=order_request.id,
                customer_id=customer.id, created_by_user_id=created_by_user_id, source=order_request.source,
                status=OrderStatus.PENDING_WAREHOUSE.value,
            )
            self.repo.create(order)

            subtotal = tax_total = discount_total = Decimal("0.00")
            for item in payload.items:
                product = self.product_repo.get_by_id(item.product_id)
                if not product or not product.is_active:
                    raise BusinessRuleException(f"Product {item.product_id} not found or inactive.", code="INVALID_PRODUCT")

                discount = Decimal(str(item.discount))
                line_subtotal = product.unit_price * item.quantity - discount
                line_tax = line_subtotal * product.tax_rate
                self.db.add(OrderItem(
                    order_id=order.id, product_id=product.id, quantity=item.quantity,
                    unit_price_snapshot=product.unit_price, tax_rate_snapshot=product.tax_rate,
                    discount=discount, line_total=line_subtotal + line_tax,
                ))
                subtotal += line_subtotal
                tax_total += line_tax
                discount_total += discount

            order.subtotal, order.tax_total, order.discount_total = subtotal, tax_total, discount_total
            order.total = subtotal + tax_total

            self.db.commit()
            return self.repo.get_by_id(order.id)
        except BusinessRuleException:
            self.db.rollback()
            raise

    def get(self, order_id: int) -> Order:
        order = self.repo.get_by_id(order_id)
        if not order:
            raise NotFoundException(f"Order {order_id} not found.")
        return order

    def list(self, status: str | None = None) -> list[Order]:
        return self.repo.list(status=status)

    def stock_check(self, order_id: int) -> dict:
        order = self.get(order_id)
        items, sufficient = [], True
        for item in order.items:
            inv = self.inventory_repo.get_by_product_id(item.product_id)
            available = inv.quantity_on_hand if inv else 0
            shortage = max(0, item.quantity - available)
            if shortage > 0:
                sufficient = False
            items.append({"product_id": item.product_id, "product_name": item.product.name,
                          "requested": item.quantity, "available": available, "shortage": shortage})
        return {"order_id": order.id, "sufficient": sufficient, "items": items}

    def confirm(self, order_id: int, current_user: User) -> Order:
        order = self.get(order_id)

        if order.status == OrderStatus.CONFIRMED.value:
            return order  # idempotent — never deduct stock twice

        if order.status != OrderStatus.PENDING_WAREHOUSE.value:
            raise BusinessRuleException(f"Order cannot be confirmed from state '{order.status}'.", code="INVALID_ORDER_STATE")

        shortages, locked = [], {}
        for item in order.items:
            inv = self.inventory_repo.get_by_product_id_for_update(item.product_id)
            available = inv.quantity_on_hand if inv else 0
            if available < item.quantity:
                shortages.append({"product_id": item.product_id, "requested": item.quantity, "available": available})
            else:
                locked[item.product_id] = inv

        if shortages:
            self.db.rollback()
            raise BusinessRuleException("Insufficient stock for one or more items — use Reject instead.", code="INSUFFICIENT_STOCK")

        for item in order.items:
            locked[item.product_id].quantity_on_hand -= item.quantity

        order.status = OrderStatus.CONFIRMED.value
        order.warehouse_handled_by_user_id = current_user.id
        self.db.commit()
        self.db.refresh(order)
        return order

    def reject(self, order_id: int, payload: OrderRejectRequest, current_user: User, ai_provider: AIProvider) -> Order:
        order = self.get(order_id)

        if order.status == OrderStatus.REJECTED.value:
            return order  # idempotent

        if order.status != OrderStatus.PENDING_WAREHOUSE.value:
            raise BusinessRuleException(f"Order cannot be rejected from state '{order.status}'.", code="INVALID_ORDER_STATE")

        if payload.reason_code == "INSUFFICIENT_STOCK":
            details = self._compute_shortage_narrative(order)
        else:
            if not payload.details:
                raise BusinessRuleException("Details are required when the reason is not INSUFFICIENT_STOCK.", code="MISSING_DETAILS")
            details = payload.details

        order.status = OrderStatus.REJECTED.value
        order.warehouse_handled_by_user_id = current_user.id
        rejection = OrderRejection(order_id=order.id, reason_code=payload.reason_code, details=details)
        self.db.add(rejection)
        self.db.flush()

        explanation = RejectionExplanationAgent(ai_provider).explain(order, rejection)
        rejection.ai_explanation = explanation.explanation

        log_ai_action(
            self.db, user_id=current_user.id, agent_name="RejectionExplanationAgent", model_name=settings.AI_MODEL,
            request_text=details, structured_output={"explanation": explanation.explanation},
            status=explanation.status, error=explanation.error, latency_ms=explanation.latency_ms,
        )

        self.db.commit()
        self.db.refresh(order)
        return order

    def _compute_shortage_narrative(self, order: Order) -> str:
        check = self.stock_check(order.id)
        lines = [
            f"{i['requested']} units of {i['product_name']} requested, {i['available']} available (shortage of {i['shortage']})."
            for i in check["items"] if i["shortage"] > 0
        ]
        if not lines:
            raise BusinessRuleException(
                "Reason INSUFFICIENT_STOCK given but stock is actually sufficient — confirm the order instead.",
                code="STOCK_ACTUALLY_SUFFICIENT",
            )
        return " ".join(lines)