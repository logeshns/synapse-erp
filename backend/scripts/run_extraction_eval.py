"""Standalone runner for the Order Extraction evaluation suite — no
pytest, no running Postgres required. Good for a quick interview demo:

    python -m scripts.run_extraction_eval
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app.models  # noqa: F401 — registers models on Base.metadata
from app.ai.agents.order_extraction_agent import OrderExtractionAgent
from app.ai.resolution import resolve_extraction
from app.db.base import Base
from tests.ai_eval.cases import CASES


class ScriptedProvider:
    def __init__(self, response: str):
        self.response = response

    def complete(self, system_prompt, user_prompt, timeout_seconds=20.0):
        return self.response


def run() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    db = sessionmaker(bind=engine)()

    passed, failed = [], []
    for case in CASES:
        case["setup"](db)
        provider = ScriptedProvider(case["llm_response"])
        result = OrderExtractionAgent(provider).run(case["raw_text"])

        if result.status == "FAILED":
            outcome = {"ai_status": "FAILED", "resolution": None}
        else:
            resolved = resolve_extraction(db, result.extracted_data)
            ai_status = "NEEDS_REVIEW" if resolved["needs_review"] else "SUCCESS"
            outcome = {"ai_status": ai_status, "resolution": {"resolution": resolved["resolution"]}}

        ok = case["assert_fn"](outcome)
        (passed if ok else failed).append(case["name"])
        print(f"  {'PASS' if ok else 'FAIL'}  {case['name']}  ->  {outcome['ai_status']}")

    print(f"\nExtraction Evaluation: {len(passed)}/{len(CASES)} cases passed")
    if failed:
        print(f"Failed cases: {', '.join(failed)}")
    print(
        "\nNote: this measures the deterministic pipeline (schema validation, "
        "retry/fallback, DB resolution) against pre-scripted LLM outputs — "
        "not a live model's NLU quality on messy input."
    )
    db.close()


if __name__ == "__main__":
    run()