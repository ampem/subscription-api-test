from datetime import datetime
from datetime import UTC as datetime_UTC

from enum import Enum

from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    plan_id: Mapped[int] = mapped_column(ForeignKey("plans.id"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default=SubscriptionStatus.ACTIVE.value)
    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(datetime_UTC))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(datetime_UTC), onupdate=lambda: datetime.now(datetime_UTC))

    user: Mapped["User"] = relationship(back_populates="subscriptions")
    plan: Mapped["Plan"] = relationship(back_populates="subscriptions")

    def is_active(self, current_time: datetime | None = None) -> bool:
        if current_time is None:
            current_time = datetime.now(datetime_UTC)
        if self.status != SubscriptionStatus.ACTIVE.value:
            return False
        if self.end_date and current_time > self.end_date.replace(tzinfo=datetime_UTC):
            return False
        return True
