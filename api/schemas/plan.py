from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from models.plan import PlanTier


class PlanBase(BaseModel):
    name: str
    tier: PlanTier
    description: str | None = None
    price: Decimal
    billing_period: str
    active_from: datetime
    active_to: datetime | None = None


class PlanCreate(PlanBase):
    pass


class PlanUpdate(BaseModel):
    name: str | None = None
    tier: PlanTier | None = None
    description: str | None = None
    price: Decimal | None = None
    billing_period: str | None = None
    active_from: datetime | None = None
    active_to: datetime | None = None


class PlanResponse(PlanBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
