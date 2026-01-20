from pydantic import BaseModel


class SubscriptionsByStatusReport(BaseModel):
    status: str
    count: int


class SubscriptionsByPlanReport(BaseModel):
    plan_name: str
    tier: str
    count: int


class SubscriptionReportResponse(BaseModel):
    total_subscriptions: int
    by_status: list[SubscriptionsByStatusReport]
    by_plan: list[SubscriptionsByPlanReport]
