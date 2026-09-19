from app.ai.agents.inventory_agent import InventoryAgent
from app.models.inventory import Inventory
from app.models.product import Product


class ScriptedProvider:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = 0

    def complete(self, system_prompt, user_prompt, timeout_seconds=20.0):
        self.calls += 1
        return self.responses.pop(0)


def test_agent_calls_tool_then_answers(db_session):
    product = Product(sku="AGT-1", name="Agent Test Widget", unit_price=100)
    db_session.add(product); db_session.flush()
    db_session.add(Inventory(product_id=product.id, quantity_on_hand=42, reorder_point=5))
    db_session.commit()

    provider = ScriptedProvider([
        f'{{"type": "tool_call", "tool_name": "get_inventory", "arguments": {{"product_id": {product.id}}}}}',
        '{"type": "final_answer", "answer": "There are 42 units in stock."}',
    ])
    result = InventoryAgent(provider, db_session).ask("How many units are in stock?")

    assert result.status == "SUCCESS"
    assert "42" in result.answer
    assert len(result.trace) == 1
    assert result.trace[0].result["success"] is True


def test_agent_refuses_unauthorized_tool_but_keeps_going(db_session):
    provider = ScriptedProvider([
        '{"type": "tool_call", "tool_name": "get_rejected_orders", "arguments": {}}',
        '{"type": "final_answer", "answer": "I do not have access to rejection data here."}',
    ])
    result = InventoryAgent(provider, db_session).ask("How many orders were rejected?")

    assert result.status == "SUCCESS"
    assert result.trace[0].result["success"] is False
    assert result.trace[0].result["error_code"] == "UNAUTHORIZED_TOOL"


def test_agent_stops_after_max_tool_calls(db_session):
    product = Product(sku="AGT-2", name="Loop Widget", unit_price=50)
    db_session.add(product); db_session.flush()
    db_session.add(Inventory(product_id=product.id, quantity_on_hand=10, reorder_point=1))
    db_session.commit()

    loop_call = f'{{"type": "tool_call", "tool_name": "get_inventory", "arguments": {{"product_id": {product.id}}}}}'
    provider = ScriptedProvider([loop_call] * 10)  # never gives a final_answer

    result = InventoryAgent(provider, db_session).ask("Keep checking stock forever")

    assert result.status == "FAILED"
    assert len(result.trace) == InventoryAgent.MAX_TOOL_CALLS
    assert "maximum" in result.error.lower()


def test_agent_recovers_from_one_malformed_step(db_session):
    provider = ScriptedProvider(["not json at all", '{"type": "final_answer", "answer": "Recovered."}'])
    result = InventoryAgent(provider, db_session).ask("test")

    assert result.status == "SUCCESS"
    assert result.answer == "Recovered."
    assert provider.calls == 2