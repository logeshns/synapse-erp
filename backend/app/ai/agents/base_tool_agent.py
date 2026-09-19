import time
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.ai.guards.output_validator import parse_agent_step
from app.ai.guards.tool_guard import execute_tool
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


class ToolCallingAgent:
    """Shared bounded tool-calling loop. Subclasses set AGENT_NAME,
    ALLOWED_TOOLS, SYSTEM_PROMPT, and build_user_prompt(); the loop
    mechanics (call, parse, execute, retry-on-malformed, cap tool calls)
    live here once. Not LangGraph: a single linear conversation with a
    hard call cap, no branching, no multi-agent hand-off, no persistent
    graph state — a plain loop correctly models that shape."""

    AGENT_NAME: str = "ToolCallingAgent"
    ALLOWED_TOOLS: list[str] = []
    SYSTEM_PROMPT: str = ""
    MAX_TOOL_CALLS: int = 5

    def __init__(self, provider: AIProvider, db: Session):
        self.provider = provider
        self.db = db

    def build_user_prompt(self, question: str, transcript: list[dict], correction_hint: str | None) -> str:
        raise NotImplementedError

    def ask(self, question: str) -> AgentRunResult:
        start = time.monotonic()
        transcript: list[dict] = []
        trace: list[ToolTraceEntry] = []
        tool_calls_made = 0
        correction_hint: str | None = None

        while True:
            prompt = self.build_user_prompt(question, transcript, correction_hint)
            correction_hint = None

            try:
                raw = self.provider.complete(self.SYSTEM_PROMPT, prompt, timeout_seconds=20.0)
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