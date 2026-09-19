from app.ai.agents.business_analyst_agent import BusinessAnalystAgent


class ScriptedProvider:
    def __init__(self, responses):
        self.responses = list(responses)

    def complete(self, system_prompt, user_prompt, timeout_seconds=20.0):
        return self.responses.pop(0)


def test_business_analyst_calls_revenue_tool_then_answers(db_session):
    provider = ScriptedProvider([
        '{"type": "tool_call", "tool_name": "get_revenue", "arguments": {"days": 30}}',
        '{"type": "final_answer", "answer": "Revenue so far is zero since no payments exist yet."}',
    ])
    result = BusinessAnalystAgent(provider, db_session).ask("How much revenue this month?")

    assert result.status == "SUCCESS"
    assert result.trace[0].tool == "get_revenue"
    assert result.trace[0].result["success"] is True


def test_business_analyst_rejects_inventory_only_tool(db_session):
    provider = ScriptedProvider([
        '{"type": "tool_call", "tool_name": "get_inventory", "arguments": {"product_id": 1}}',
        '{"type": "final_answer", "answer": "I cannot check raw inventory levels from here."}',
    ])
    result = BusinessAnalystAgent(provider, db_session).ask("How many laptops in stock?")

    assert result.status == "SUCCESS"
    assert result.trace[0].result["success"] is False
    assert result.trace[0].result["error_code"] == "UNAUTHORIZED_TOOL"