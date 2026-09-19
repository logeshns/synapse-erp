import time
from dataclasses import dataclass

from app.ai.guards.output_validator import validate_extraction
from app.ai.prompts.order_extraction import SYSTEM_PROMPT, build_user_prompt
from app.ai.provider import AIProvider
from app.exceptions import AIProviderException, AISchemaException, AITimeoutException
from app.schemas.ai import ExtractedOrderData


@dataclass
class ExtractionResult:
    status: str  # "SUCCESS" | "FAILED"
    extracted_data: ExtractedOrderData | None
    raw_response: str | None
    error: str | None
    latency_ms: int
    attempts: int


class OrderExtractionAgent:
    """Single-shot structured extraction — not a tool-calling loop. One
    corrective retry on schema failure, then a hard fallback to FAILED so
    the caller routes the request to manual review instead of accepting
    bad data. Never raises — a failure is a normal, expected outcome here,
    not an exceptional one."""

    MAX_ATTEMPTS = 2

    def __init__(self, provider: AIProvider):
        self.provider = provider

    def run(self, raw_text: str) -> ExtractionResult:
        start = time.monotonic()
        last_error: str | None = None

        for attempt in range(1, self.MAX_ATTEMPTS + 1):
            user_prompt = build_user_prompt(raw_text, correction_hint=last_error)

            try:
                raw_response = self.provider.complete(SYSTEM_PROMPT, user_prompt)
            except (AIProviderException, AITimeoutException) as exc:
                return ExtractionResult(
                    status="FAILED",
                    extracted_data=None,
                    raw_response=None,
                    error=str(exc),
                    latency_ms=int((time.monotonic() - start) * 1000),
                    attempts=attempt,
                )

            try:
                data = validate_extraction(raw_response)
                return ExtractionResult(
                    status="SUCCESS",
                    extracted_data=data,
                    raw_response=raw_response,
                    error=None,
                    latency_ms=int((time.monotonic() - start) * 1000),
                    attempts=attempt,
                )
            except AISchemaException as exc:
                last_error = str(exc)
                continue  # one corrective retry, then give up

        return ExtractionResult(
            status="FAILED",
            extracted_data=None,
            raw_response=None,
            error=f"Invalid structured output after {self.MAX_ATTEMPTS} attempts: {last_error}",
            latency_ms=int((time.monotonic() - start) * 1000),
            attempts=self.MAX_ATTEMPTS,
        )