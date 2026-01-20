from datetime import datetime

from pydantic import BaseModel

from models.subscription import SubscriptionStatus
from schemas.user import UserResponse
from schemas.plan import PlanResponse


class SubscriptionBase(BaseModel):
    user_id: int
    plan_id: int
    start_date: datetime
    end_date: datetime | None = None


class SubscriptionCreate(SubscriptionBase):
    pass


class SubscriptionUpdate(BaseModel):
    plan_id: int | None = None
    status: SubscriptionStatus | None = None
    end_date: datetime | None = None


class SubscriptionResponse(SubscriptionBase):
    id: int
    status: SubscriptionStatus
    cancelled_at: datetime | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SubscriptionDetailResponse(SubscriptionResponse):
    user: UserResponse
    plan: PlanResponse
