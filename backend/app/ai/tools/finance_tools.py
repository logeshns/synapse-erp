from app.ai.tool_errors import ToolExecutionError
from app.services.analytics_service import AnalyticsService


def get_revenue(db, args: dict) -> dict:
    days = args.get("days", 30)
    if not isinstance(days, int) or days <= 0:
        raise ToolExecutionError("INVALID_ARGUMENTS", "days must be a positive integer.")
    return AnalyticsService(db).revenue(days)


def get_sales_by_product(db, args: dict) -> dict:
    days = args.get("days", 30)
    return {"period_days": days, "products": AnalyticsService(db).sales_by_product(days)}


def get_online_offline_sales(db, args: dict) -> dict:
    days = args.get("days", 30)
    return AnalyticsService(db).online_vs_offline(days)


def get_outstanding_invoices(db, args: dict) -> dict:
    return AnalyticsService(db).outstanding_payments()


def calculate_lost_revenue(db, args: dict) -> dict:
    days = args.get("days", 30)
    return AnalyticsService(db).lost_revenue(days)