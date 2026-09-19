import pytest

from app.ai.agents.order_extraction_agent import OrderExtractionAgent
from app.ai.resolution import resolve_extraction
from tests.ai_eval.cases import CASES


class ScriptedProvider:
    def __init__(self, response: str):
        self.response = response

    def complete(self, system_prompt, user_prompt, timeout_seconds=20.0):
        return self.response


def _run_case(db_session, case: dict) -> dict:
    case["setup"](db_session)
    provider = ScriptedProvider(case["llm_response"])
    result = OrderExtractionAgent(provider).run(case["raw_text"])

    if result.status == "FAILED":
        return {"ai_status": "FAILED", "resolution": None}

    resolved = resolve_extraction(db_session, result.extracted_data)
    ai_status = "NEEDS_REVIEW" if resolved["needs_review"] else "SUCCESS"
    return {"ai_status": ai_status, "resolution": {"resolution": resolved["resolution"]}}


@pytest.mark.parametrize("case", CASES, ids=[c["name"] for c in CASES])
def test_extraction_case(db_session, case):
    outcome = _run_case(db_session, case)
    assert case["assert_fn"](outcome), f"Case '{case['name']}' failed. Got: {outcome}"


def test_extraction_eval_summary(db_session, capsys):
    """Prints the interview-ready 'X/Y cases passed' summary. Cases share
    one session here (unlike the isolated parametrized run above) — safe
    because every case's seed data uses unique emails/SKUs."""
    passed, failed = [], []
    for case in CASES:
        outcome = _run_case(db_session, case)
        (passed if case["assert_fn"](outcome) else failed).append(case["name"])

    print(f"\nExtraction Evaluation: {len(passed)}/{len(CASES)} cases passed")
    if failed:
        print(f"Failed: {', '.join(failed)}")

    assert len(passed) == len(CASES), f"{len(failed)} case(s) failed: {failed}"