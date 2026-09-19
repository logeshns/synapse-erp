import time
from dataclasses import dataclass

from app.ai.prompts.rejection_explanation import SYSTEM_PROMPT
from app.ai.provider import AIProvider
from app.exceptions import AIProviderException, AITimeoutException
from app.models.order import Order
from app.models.order_rejection import OrderRejection


@dataclass
class ExplanationResult:
    status: str  # SUCCESS | FAILED
    explanation: str
    error: str | None
    latency_ms: int


class RejectionExplanationAgent:
    """Rephrases a decision the deterministic backend already made — it
    does not decide anything. On any AI failure it falls back to the
    deterministic `details` string itself, which is already human-readable,
    so /reject never has to return an error just because the LLM is down."""

    def __init__(self, provider: AIProvider):
        self.provider = provider

    def explain(self, order: Order, rejection: OrderRejection) -> ExplanationResult:
        start = time.monotonic()
        fallback = rejection.details
        prompt = f"Order number: {order.order_number}\nReason code: {rejection.reason_code}\nDetails: {rejection.details}"

        try:
            text = self.provider.complete(SYSTEM_PROMPT, prompt, timeout_seconds=10.0).strip()
            if not text:
                raise ValueError("Empty response from AI provider.")
            return ExplanationResult("SUCCESS", text, None, int((time.monotonic() - start) * 1000))
        except (AIProviderException, AITimeoutException, ValueError) as exc:
            return ExplanationResult("FAILED", fallback, str(exc), int((time.monotonic() - start) * 1000))