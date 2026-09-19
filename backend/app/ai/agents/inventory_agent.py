import time
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.ai.guards.output_validator import parse_agent_step
from app.ai.guards.tool_guard import execute_tool
from app.ai.prompts.inventory_agent import SYSTEM_PROMPT, build_user_prompt
from app.ai.provider import AIProvider
from app.exceptions import AIProviderException, AISchemaException, AITimeoutException
from app.schemas.agent import FinalAnswerStep, ToolCallStep, ToolTraceEntry


@dataclass
class AgentRunResult:
    status: str  # SUCCESS | FAILED
    answer: str | None
    trace: list[ToolTraceEntry]
    error: str | None
    latency_ms: int


class InventoryAgent:
    """Bounded tool-calling loop, not LangGraph: a single linear
    conversation with a hard call cap, no branching, no multi-agent
    hand-off, no persistent graph state — a plain loop is the simplest
    thing that correctly models that shape."""

    AGENT_NAME = "InventoryAgent"
    ALLOWED_TOOLS = ["get_inventory", "get_low_stock_products", "get_sales_history", "get_inventory_value"]
    MAX_TOOL_CALLS = 5

    def __init__(self, provider: AIProvider, db: Session):
        self.provider = provider
        self.db = db

    def ask(self, question: str) -> AgentRunResult:
        start = time.monotonic()
        transcript: list[dict] = []
        trace: list[ToolTraceEntry] = []
        tool_calls_made = 0
        correction_hint: str | None = None

        while True:
            prompt = build_user_prompt(question, transcript, correction_hint)
            correction_hint = None

            try:
                raw = self.provider.complete(SYSTEM_PROMPT, prompt, timeout_seconds=20.0)
            except (AIProviderException, AITimeoutException) as exc:
                return AgentRunResult("FAILED", None, trace, str(exc), int((time.monotonic() - start) * 1000))

            try:
                step = parse_agent_step(raw)
            except AISchemaException as exc:
                correction_hint = str(exc)
                continue

            if isinstance(step, FinalAnswerStep):
                return AgentRunResult("SUCCESS", step.answer, trace, None, int((time.monotonic() - start) * 1000))

            assert isinstance(step, ToolCallStep)

            if tool_calls_made >= self.MAX_TOOL_CALLS:
                error = f"Exceeded the maximum of {self.MAX_TOOL_CALLS} tool calls without a final answer."
                return AgentRunResult("FAILED", None, trace, error, int((time.monotonic() - start) * 1000))

            tool_calls_made += 1
            result = execute_tool(self.db, step.tool_name, step.arguments, self.ALLOWED_TOOLS)
            trace.append(ToolTraceEntry(tool=step.tool_name, arguments=step.arguments, result=result, latency_ms=result["latency_ms"]))
            transcript.append({"tool_name": step.tool_name, "arguments": step.arguments, "result": result})