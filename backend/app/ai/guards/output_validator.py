import json

from pydantic import ValidationError

from app.exceptions import AISchemaException
from app.schemas.agent import FinalAnswerStep, ToolCallStep
from app.schemas.ai import ExtractedOrderData


def _strip_json_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:]
        text = text.strip()
    return text


def _parse_json(raw_response: str) -> dict:
    try:
        return json.loads(_strip_json_fences(raw_response))
    except json.JSONDecodeError as exc:
        raise AISchemaException(f"Response was not valid JSON: {exc}")


def validate_extraction(raw_response: str) -> ExtractedOrderData:
    payload = _parse_json(raw_response)
    try:
        return ExtractedOrderData.model_validate(payload)
    except ValidationError as exc:
        raise AISchemaException(f"Response did not match the expected schema: {exc}")


def parse_agent_step(raw_response: str) -> ToolCallStep | FinalAnswerStep:
    payload = _parse_json(raw_response)
    step_type = payload.get("type")

    try:
        if step_type == "tool_call":
            return ToolCallStep.model_validate(payload)
        if step_type == "final_answer":
            return FinalAnswerStep.model_validate(payload)
    except ValidationError as exc:
        raise AISchemaException(f"Response did not match the expected step schema: {exc}")

    raise AISchemaException(f"Unknown or missing 'type' field: {step_type!r}")