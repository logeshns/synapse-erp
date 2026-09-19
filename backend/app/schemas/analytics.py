from pydantic import BaseModel


class RevenueOut(BaseModel):
    period_days: int
    total_revenue: str


class OrdersSummaryOut(BaseModel):
    period_days: int
    counts: dict[str, int]
    total: int


class SalesByProductOut(BaseModel):
    product_id: int
    product_name: str
    units_sold: int
    revenue: str


class InventorySummaryOut(BaseModel):
    total_value: str
    product_count: int
    low_stock_count: int


class SourceBreakdown(BaseModel):
    orders: int
    revenue: str


class OnlineOfflineOut(BaseModel):
    period_days: int
    by_source: dict[str, SourceBreakdown]


class OutstandingPaymentsOut(BaseModel):
    UNPAID: str
    OVERDUE: str


class LostRevenueOut(BaseModel):
    period_days: int
    order_count: int
    total_lost_value: str
    top_affected_product: str | None


class SummaryOut(BaseModel):
    revenue: RevenueOut
    orders: OrdersSummaryOut
    inventory: InventorySummaryOut
    outstanding_payments: OutstandingPaymentsOut
    lost_revenue: LostRevenueOut
    customer_count: int