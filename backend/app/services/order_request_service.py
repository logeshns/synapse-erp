from sqlalchemy.orm import Session

from app.ai.agents.order_extraction_agent import OrderExtractionAgent
from app.ai.audit import log_ai_action
from app.ai.provider import AIProvider
from app.ai.resolution import resolve_extraction
from app.core.config import settings
from app.exceptions import BusinessRuleException, NotFoundException
from app.models.order_request import OrderRequest, OrderRequestReviewStatus
from app.models.user import User
from app.repositories.order_request_repository import OrderRequestRepository
from app.schemas.order_request import OrderRequestApprove, OrderRequestCreate, OrderRequestReject
from app.services.order_service import OrderService
from app.utils.numbering import generate_number


class OrderRequestService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = OrderRequestRepository(db)
        self.order_service = OrderService(db)

    def create(self, payload: OrderRequestCreate, current_user: User) -> OrderRequest:
        if payload.source == "OFFLINE" and not payload.raw_text and not payload.customer_id:
            raise BusinessRuleException(
                "An offline order request needs either raw text or a known customer.",
                code="INCOMPLETE_ORDER_REQUEST",
            )

        order_request = OrderRequest(
            request_number=generate_number("REQ", self.repo.count()),
            source=payload.source,
            customer_id=payload.customer_id,
            submitted_by_sales_user_id=current_user.id if payload.source == "OFFLINE" else None,
            raw_text=payload.raw_text,
            ai_status="NOT_STARTED",
            review_status=OrderRequestReviewStatus.PENDING_REVIEW.value,
        )
        self.repo.create(order_request)
        self.db.commit()
        self.db.refresh(order_request)
        return order_request

    def get(self, order_request_id: int) -> OrderRequest:
        order_request = self.repo.get_by_id(order_request_id)
        if not order_request:
            raise NotFoundException(f"Order request {order_request_id} not found.")
        return order_request

    def list(self, review_status: str | None = None, source: str | None = None) -> list[OrderRequest]:
        return self.repo.list(review_status=review_status, source=source)

    def extract(self, order_request_id: int, current_user: User, ai_provider: AIProvider) -> OrderRequest:
        order_request = self.get(order_request_id)

        if order_request.review_status != OrderRequestReviewStatus.PENDING_REVIEW.value:
            raise BusinessRuleException(
                "Only a pending order request can be (re-)extracted.", code="INVALID_STATE_FOR_EXTRACTION"
            )
        if not order_request.raw_text:
            raise BusinessRuleException("This order request has no raw text to extract from.", code="NO_RAW_TEXT")

        result = OrderExtractionAgent(ai_provider).run(order_request.raw_text)

        if result.status == "FAILED":
            order_request.ai_status = "FAILED"
            order_request.extracted_data = {"error": result.error}
            structured_output_for_log = None
        else:
            resolved = resolve_extraction(self.db, result.extracted_data)
            order_request.extracted_data = resolved
            order_request.ai_status = "NEEDS_REVIEW" if resolved["needs_review"] else "SUCCESS"
            structured_output_for_log = resolved

        log_ai_action(
            self.db,
            user_id=current_user.id,
            agent_name="OrderExtractionAgent",
            model_name=settings.AI_MODEL,
            request_text=order_request.raw_text,
            structured_output=structured_output_for_log,
            status=result.status,
            error=result.error,
            latency_ms=result.latency_ms,
        )

        self.db.commit()
        self.db.refresh(order_request)
        return order_request

    def approve(self, order_request_id: int, payload: OrderRequestApprove, current_user: User):
        order_request = self.get(order_request_id)

        if order_request.review_status == OrderRequestReviewStatus.REJECTED.value:
            raise BusinessRuleException("A rejected order request cannot be approved.", code="ALREADY_REJECTED")

        order = self.order_service.create_from_request(order_request, payload, created_by_user_id=current_user.id)

        if order_request.review_status != OrderRequestReviewStatus.APPROVED.value:
            order_request.customer_id = payload.customer_id
            order_request.review_status = OrderRequestReviewStatus.APPROVED.value
            order_request.ai_status = "SUCCESS"  # Updates AI status badge to green SUCCESS upon human approval
            self.db.commit()
            self.db.refresh(order_request)

        return order

    def reject(self, order_request_id: int, payload: OrderRequestReject) -> OrderRequest:
        order_request = self.get(order_request_id)

        if order_request.review_status == OrderRequestReviewStatus.APPROVED.value:
            raise BusinessRuleException("An approved order request cannot be rejected.", code="ALREADY_APPROVED")

        order_request.review_status = OrderRequestReviewStatus.REJECTED.value
        order_request.rejection_reason = payload.reason
        self.db.commit()
        self.db.refresh(order_request)
        return order_request