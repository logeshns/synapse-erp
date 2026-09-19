from typing import Literal, Union

from pydantic import BaseModel, Field


class ToolCallStep(BaseModel):
    type: Literal["tool_call"]
    tool_name: str
    arguments: dict = Field(default_factory=dict)


class FinalAnswerStep(BaseModel):
    type: Literal["final_answer"]
    answer: str


AgentStep = Union[ToolCallStep, FinalAnswerStep]


class ToolTraceEntry(BaseModel):
    tool: str
    arguments: dict
    result: dict
    latency_ms: int


class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=1000)


class AskResponse(BaseModel):
    status: str
    answer: str | None
    trace: list[ToolTraceEntry]
    error: str | None
    latency_ms: int