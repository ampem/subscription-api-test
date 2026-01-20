from datetime import UTC as datetime_UTC
from datetime import datetime, timedelta
from decimal import Decimal

import pytest

from models.user import User, UserMode
from models.plan import Plan, PlanTier
from models.subscription import Subscription, SubscriptionStatus


class TestUserModel:
    def test_user_creation(self, db_session):
        user = User(
            email="new@example.com",
            name="New User",
            mode=UserMode.LIVE.value,
        )
        db_session.add(user)
        db_session.commit()

        assert user.id is not None
        assert user.email == "new@example.com"
        assert user.name == "New User"
        assert user.mode == UserMode.LIVE.value

    def test_user_is_simulation_false_for_live_user(self, sample_user):
        assert sample_user.is_simulation is False

    def test_user_is_simulation_true_for_simulation_user(self, simulation_user):
        assert simulation_user.is_simulation is True

    def test_user_default_mode_is_live(self, db_session):
        user = User(email="default@example.com", name="Default Mode")
        db_session.add(user)
        db_session.commit()

        assert user.mode == UserMode.LIVE.value


class TestPlanModel:
    def test_plan_creation(self, db_session):
        plan = Plan(
            name="Test Plan",
            tier=PlanTier.PRO.value,
            price=Decimal("19.99"),
            billing_period="monthly",
            active_from=datetime.now(datetime_UTC),
        )
        db_session.add(plan)
        db_session.commit()

        assert plan.id is not None
        assert plan.name == "Test Plan"
        assert plan.tier == PlanTier.PRO.value

    def test_plan_is_active_when_within_date_range(self, sample_plan):
        current_time = datetime.now(datetime_UTC)
        assert sample_plan.is_active(current_time) is True

    def test_plan_is_active_when_no_end_date(self, db_session):
        plan = Plan(
            name="No End Date",
            tier=PlanTier.BASIC.value,
            price=Decimal("5.00"),
            billing_period="monthly",
            active_from=datetime.now(datetime_UTC) - timedelta(days=10),
            active_to=None,
        )
        db_session.add(plan)
        db_session.commit()

        assert plan.is_active() is True

    def test_plan_is_not_active_when_expired(self, expired_plan):
        current_time = datetime.now(datetime_UTC)
        assert expired_plan.is_active(current_time) is False

    def test_plan_is_not_active_when_future(self, future_plan):
        current_time = datetime.now(datetime_UTC)
        assert future_plan.is_active(current_time) is False

    def test_plan_is_active_with_custom_time(self, db_session):
        plan = Plan(
            name="Custom Time Test",
            tier=PlanTier.FREE.value,
            price=Decimal("0.00"),
            billing_period="monthly",
            active_from=datetime(2025, 1, 1, tzinfo=datetime_UTC),
            active_to=datetime(2025, 12, 31, tzinfo=datetime_UTC),
        )
        db_session.add(plan)
        db_session.commit()

        assert plan.is_active(datetime(2025, 6, 15, tzinfo=datetime_UTC)) is True
        assert plan.is_active(datetime(2024, 6, 15, tzinfo=datetime_UTC)) is False
        assert plan.is_active(datetime(2026, 6, 15, tzinfo=datetime_UTC)) is False

    def test_plan_tiers(self):
        assert PlanTier.FREE.value == "free"
        assert PlanTier.BASIC.value == "basic"
        assert PlanTier.PRO.value == "pro"


class TestSubscriptionModel:
    def test_subscription_creation(self, db_session, sample_user, sample_plan):
        subscription = Subscription(
            user_id=sample_user.id,
            plan_id=sample_plan.id,
            status=SubscriptionStatus.ACTIVE.value,
            start_date=datetime.now(datetime_UTC),
        )
        db_session.add(subscription)
        db_session.commit()

        assert subscription.id is not None
        assert subscription.user_id == sample_user.id
        assert subscription.plan_id == sample_plan.id

    def test_subscription_is_active_when_status_active_and_not_expired(
        self, sample_subscription
    ):
        current_time = datetime.now(datetime_UTC)
        assert sample_subscription.is_active(current_time) is True

    def test_subscription_is_not_active_when_status_cancelled(
        self, db_session, sample_user, sample_plan
    ):
        subscription = Subscription(
            user_id=sample_user.id,
            plan_id=sample_plan.id,
            status=SubscriptionStatus.CANCELLED.value,
            start_date=datetime.now(datetime_UTC) - timedelta(days=15),
            end_date=datetime.now(datetime_UTC) + timedelta(days=15),
        )
        db_session.add(subscription)
        db_session.commit()

        assert subscription.is_active() is False

    def test_subscription_is_not_active_when_expired(
        self, db_session, sample_user, sample_plan
    ):
        subscription = Subscription(
            user_id=sample_user.id,
            plan_id=sample_plan.id,
            status=SubscriptionStatus.ACTIVE.value,
            start_date=datetime.now(datetime_UTC) - timedelta(days=60),
            end_date=datetime.now(datetime_UTC) - timedelta(days=30),
        )
        db_session.add(subscription)
        db_session.commit()

        assert subscription.is_active() is False

    def test_subscription_is_active_with_custom_time(
        self, db_session, sample_user, sample_plan
    ):
        subscription = Subscription(
            user_id=sample_user.id,
            plan_id=sample_plan.id,
            status=SubscriptionStatus.ACTIVE.value,
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 12, 31),
        )
        db_session.add(subscription)
        db_session.commit()

        assert subscription.is_active(datetime(2025, 6, 15, tzinfo=datetime_UTC)) is True
        assert subscription.is_active(datetime(2026, 6, 15, tzinfo=datetime_UTC)) is False

    def test_subscription_is_active_when_no_end_date(
        self, db_session, sample_user, sample_plan
    ):
        subscription = Subscription(
            user_id=sample_user.id,
            plan_id=sample_plan.id,
            status=SubscriptionStatus.ACTIVE.value,
            start_date=datetime.now(datetime_UTC) - timedelta(days=30),
            end_date=None,
        )
        db_session.add(subscription)
        db_session.commit()

        assert subscription.is_active() is True

    def test_subscription_statuses(self):
        assert SubscriptionStatus.ACTIVE.value == "active"
        assert SubscriptionStatus.CANCELLED.value == "cancelled"
        assert SubscriptionStatus.EXPIRED.value == "expired"

    def test_subscription_relationships(self, sample_subscription, sample_user, sample_plan):
        assert sample_subscription.user.id == sample_user.id
        assert sample_subscription.plan.id == sample_plan.id
