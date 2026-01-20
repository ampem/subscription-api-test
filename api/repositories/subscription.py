from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from models.subscription import Subscription, SubscriptionStatus
from models.plan import Plan
from schemas.subscription import SubscriptionCreate, SubscriptionUpdate


class SubscriptionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, subscription_id: int) -> Subscription | None:
        return (
            self.db.query(Subscription)
            .options(joinedload(Subscription.user), joinedload(Subscription.plan))
            .filter(Subscription.id == subscription_id)
            .first()
        )

    def get_all(self, skip: int = 0, limit: int = 100) -> list[Subscription]:
        return (
            self.db.query(Subscription)
            .options(joinedload(Subscription.user), joinedload(Subscription.plan))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_user_id(self, user_id: int) -> list[Subscription]:
        return (
            self.db.query(Subscription)
            .options(joinedload(Subscription.plan))
            .filter(Subscription.user_id == user_id)
            .all()
        )

    def get_active_by_user_id(self, user_id: int) -> Subscription | None:
        return (
            self.db.query(Subscription)
            .options(joinedload(Subscription.plan))
            .filter(Subscription.user_id == user_id)
            .filter(Subscription.status == SubscriptionStatus.ACTIVE.value)
            .first()
        )

    def create(self, subscription_data: SubscriptionCreate) -> Subscription:
        subscription = Subscription(**subscription_data.model_dump())
        self.db.add(subscription)
        self.db.commit()
        self.db.refresh(subscription)
        return subscription

    def update(self, subscription: Subscription, subscription_data: SubscriptionUpdate) -> Subscription:
        update_data = subscription_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(subscription, field, value)
        self.db.commit()
        self.db.refresh(subscription)
        return subscription

    def delete(self, subscription: Subscription) -> None:
        self.db.delete(subscription)
        self.db.commit()

    def count_by_status(self) -> list[tuple[str, int]]:
        return (
            self.db.query(Subscription.status, func.count(Subscription.id))
            .group_by(Subscription.status)
            .all()
        )

    def count_by_plan(self) -> list[tuple[str, str, int]]:
        return (
            self.db.query(Plan.name, Plan.tier, func.count(Subscription.id))
            .join(Subscription, Subscription.plan_id == Plan.id)
            .group_by(Plan.id, Plan.name, Plan.tier)
            .all()
        )

    def count_total(self) -> int:
        return self.db.query(func.count(Subscription.id)).scalar()
