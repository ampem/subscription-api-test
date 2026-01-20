from datetime import datetime
from datetime import UTC as datetime_UTC

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.subscription import Subscription, SubscriptionStatus
from models.user import UserMode
from repositories.subscription import SubscriptionRepository
from repositories.user import UserRepository
from repositories.plan import PlanRepository
from schemas.subscription import SubscriptionCreate, SubscriptionUpdate


class SubscriptionService:
    def __init__(self, db: Session):
        self.repository = SubscriptionRepository(db)
        self.user_repository = UserRepository(db)
        self.plan_repository = PlanRepository(db)

    def get_subscription(self, subscription_id: int) -> Subscription:
        subscription = self.repository.get_by_id(subscription_id)
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subscription not found"
            )
        return subscription

    def get_subscriptions(self, skip: int = 0, limit: int = 100) -> list[Subscription]:
        return self.repository.get_all(skip=skip, limit=limit)

    def get_user_subscriptions(self, user_id: int) -> list[Subscription]:
        return self.repository.get_by_user_id(user_id)

    def get_active_subscription(self, user_id: int) -> Subscription | None:
        return self.repository.get_active_by_user_id(user_id)

    def create_subscription(self, subscription_data: SubscriptionCreate) -> Subscription:
        user = self.user_repository.get_by_id(subscription_data.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        if user.mode == UserMode.SIMULATION.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Users in simulation mode cannot have subscriptions"
            )

        existing_active = self.repository.get_active_by_user_id(subscription_data.user_id)
        if existing_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already has an active subscription"
            )

        plan = self.plan_repository.get_by_id(subscription_data.plan_id)
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plan not found"
            )

        if not plan.is_active():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Plan is not currently active"
            )

        return self.repository.create(subscription_data)

    def update_subscription(self, subscription_id: int, subscription_data: SubscriptionUpdate) -> Subscription:
        subscription = self.get_subscription(subscription_id)

        if subscription_data.plan_id:
            plan = self.plan_repository.get_by_id(subscription_data.plan_id)
            if not plan:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Plan not found"
                )
            if not plan.is_active():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Plan is not currently active"
                )

        return self.repository.update(subscription, subscription_data)

    def cancel_subscription(self, subscription_id: int) -> Subscription:
        subscription = self.get_subscription(subscription_id)

        if subscription.status != SubscriptionStatus.ACTIVE.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only active subscriptions can be cancelled"
            )

        update_data = SubscriptionUpdate(
            status=SubscriptionStatus.CANCELLED
        )
        subscription.cancelled_at = datetime.now(datetime_UTC)
        return self.repository.update(subscription, update_data)

    def delete_subscription(self, subscription_id: int) -> None:
        subscription = self.get_subscription(subscription_id)
        self.repository.delete(subscription)
