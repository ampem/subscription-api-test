from datetime import datetime
from decimal import Decimal
from enum import Enum

from sqlalchemy import String, DateTime, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class PlanTier(str, Enum):
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"


class Plan(Base):
    __tablename__ = "plans"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    tier: Mapped[str] = mapped_column(String(50), nullable=False)  # free, basic, pro
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    billing_period: Mapped[str] = mapped_column(String(50), nullable=False)  # monthly, yearly
    active_from: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    active_to: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    subscriptions: Mapped[list["Subscription"]] = relationship(back_populates="plan")

    def is_active(self, current_time: datetime | None = None) -> bool:
        if current_time is None:
            current_time = datetime.utcnow()
        if self.active_to is None:
            return current_time >= self.active_from
        return self.active_from <= current_time <= self.active_to
