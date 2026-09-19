import time

from sqlalchemy.orm import Session

from app.ai.tool_errors import ToolExecutionError
from app.ai.tools import finance_tools, inventory_tools

TOOL_REGISTRY = {
    "get_inventory": inventory_tools.get_inventory,
    "get_low_stock_products": inventory_tools.get_low_stock_products,
    "get_sales_history": inventory_tools.get_sales_history,
    "get_inventory_value": inventory_tools.get_inventory_value,
    "get_rejected_orders": inventory_tools.get_rejected_orders,
    "get_revenue": finance_tools.get_revenue,
    "get_sales_by_product": finance_tools.get_sales_by_product,
    "get_online_offline_sales": finance_tools.get_online_offline_sales,
    "get_outstanding_invoices": finance_tools.get_outstanding_invoices,
    "calculate_lost_revenue": finance_tools.calculate_lost_revenue,
}


def execute_tool(db: Session, tool_name: str, arguments: dict, allowed_tools: list[str]) -> dict:
    start = time.monotonic()

    if tool_name not in allowed_tools:
        return _error(tool_name, "UNAUTHORIZED_TOOL", f"'{tool_name}' is not permitted for this agent.", start)

    handler = TOOL_REGISTRY.get(tool_name)
    if handler is None:
        return _error(tool_name, "UNKNOWN_TOOL", f"'{tool_name}' does not exist.", start)

    try:
        result = handler(db, arguments)
        return {"success": True, "tool": tool_name, "result": result, "latency_ms": int((time.monotonic() - start) * 1000)}
    except ToolExecutionError as exc:
        return _error(tool_name, exc.error_code, exc.message, start)
    except Exception as exc:
        return _error(tool_name, "TOOL_EXECUTION_FAILED", str(exc), start)


def _error(tool_name: str, code: str, message: str, start: float) -> dict:
    return {"success": False, "tool": tool_name, "error_code": code, "message": message,
            "latency_ms": int((time.monotonic() - start) * 1000)}