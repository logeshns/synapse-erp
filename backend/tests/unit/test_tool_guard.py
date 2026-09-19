from app.ai.guards.tool_guard import execute_tool
from app.models.inventory import Inventory
from app.models.product import Product


def test_execute_tool_returns_result_for_allowed_tool(db_session):
    product = Product(sku="TG-1", name="Tool Guard Widget", unit_price=10)
    db_session.add(product); db_session.flush()
    db_session.add(Inventory(product_id=product.id, quantity_on_hand=15, reorder_point=3))
    db_session.commit()

    result = execute_tool(db_session, "get_inventory", {"product_id": product.id}, allowed_tools=["get_inventory"])
    assert result["success"] is True
    assert result["result"]["quantity_on_hand"] == 15


def test_execute_tool_rejects_tool_outside_allow_list(db_session):
    result = execute_tool(db_session, "get_inventory_value", {}, allowed_tools=["get_inventory"])
    assert result["success"] is False
    assert result["error_code"] == "UNAUTHORIZED_TOOL"


def test_execute_tool_handles_invalid_arguments(db_session):
    result = execute_tool(db_session, "get_inventory", {"product_id": "nope"}, allowed_tools=["get_inventory"])
    assert result["success"] is False
    assert result["error_code"] == "INVALID_ARGUMENTS"


def test_execute_tool_handles_missing_product(db_session):
    result = execute_tool(db_session, "get_inventory", {"product_id": 999999}, allowed_tools=["get_inventory"])
    assert result["success"] is False
    assert result["error_code"] == "PRODUCT_NOT_FOUND"