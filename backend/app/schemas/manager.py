from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TeamMemberMetrics(BaseModel):
    user_id: int
    name: str
    role: str
    period_days: int
    order_requests_submitted: int | None = None
    orders_created: int | None = None
    orders_confirmed: int | None = None
    orders_rejected: int | None = None
    receipts_generated: int | None = None


class ManagerRatingCreate(BaseModel):
    employee_id: int
    period: str = Field(min_length=4, max_length=20)
    communication: int = Field(ge=1, le=5)
    accuracy: int = Field(ge=1, le=5)
    order_processing: int = Field(ge=1, le=5)
    customer_handling: int = Field(ge=1, le=5)
    overall: int = Field(ge=1, le=5)
    comments: str | None = Field(default=None, max_length=1000)


class ManagerRatingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    employee_id: int
    manager_id: int
    period: str
    communication: int
    accuracy: int
    order_processing: int
    customer_handling: int
    overall: int
    comments: str | None
    created_at: datetime