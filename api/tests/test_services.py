from datetime import datetime, timedelta
from datetime import UTC as datetime_UTC
from decimal import Decimal

import pytest
from fastapi import HTTPException

from models.user import UserMode
from models.plan import PlanTier
from models.subscription import SubscriptionStatus
from schemas.user import UserCreate, UserUpdate
from schemas.plan import PlanCreate, PlanUpdate
from schemas.subscription import SubscriptionCreate, SubscriptionUpdate
from services.user import UserService
from services.plan import PlanService
from services.subscription import SubscriptionService
from services.report import ReportService


class TestUserService:
    def test_create_user(self, db_session):
        service = UserService(db_session)
        user_data = UserCreate(
            email="newuser@example.com",
            name="New User",
            mode=UserMode.LIVE,
        )

        user = service.create_user(user_data)

        assert user.id is not None
        assert user.email == "newuser@example.com"
        assert user.name == "New User"

    def test_create_user_duplicate_email_raises_error(self, db_session, sample_user):
        service = UserService(db_session)
        user_data = UserCreate(
            email=sample_user.email,
            name="Duplicate User",
            mode=UserMode.LIVE,
        )

        with pytest.raises(HTTPException) as exc_info:
            service.create_user(user_data)

        assert exc_info.value.status_code == 400
        assert "Email already registered" in str(exc_info.value.detail)

    def test_get_user(self, db_session, sample_user):
        service = UserService(db_session)

        user = service.get_user(sample_user.id)

        assert user.id == sample_user.id
        assert user.email == sample_user.email

    def test_get_user_not_found_raises_error(self, db_session):
        service = UserService(db_session)

        with pytest.raises(HTTPException) as exc_info:
            service.get_user(99999)

        assert exc_info.value.status_code == 404
        assert "User not found" in str(exc_info.value.detail)

    def test_update_user(self, db_session, sample_user):
        service = UserService(db_session)
        update_data = UserUpdate(name="Updated Name")

        user = service.update_user(sample_user.id, update_data)

        assert user.name == "Updated Name"
        assert user.email == sample_user.email

    def test_update_user_email_to_existing_raises_error(
        self, db_session, sample_user, simulation_user
    ):
        service = UserService(db_session)
        update_data = UserUpdate(email=simulation_user.email)

        with pytest.raises(HTTPException) as exc_info:
            service.update_user(sample_user.id, update_data)

        assert exc_info.value.status_code == 400

    def test_delete_user(self, db_session, sample_user):
        service = UserService(db_session)
        user_id = sample_user.id

        service.delete_user(user_id)

        with pytest.raises(HTTPException):
            service.get_user(user_id)

    def test_get_users(self, db_session, sample_user, simulation_user):
        service = UserService(db_session)

        users = service.get_users()

        assert len(users) >= 2


class TestPlanService:
    def test_create_plan(self, db_session):
        service = PlanService(db_session)
        plan_data = PlanCreate(
            name="New Plan",
            tier=PlanTier.PRO,
            price=Decimal("29.99"),
            billing_period="monthly",
            active_from=datetime.now(datetime_UTC),
        )

        plan = service.create_plan(plan_data)

        assert plan.id is not None
        assert plan.name == "New Plan"
        assert plan.tier == PlanTier.PRO.value

    def test_get_plan(self, db_session, sample_plan):
        service = PlanService(db_session)

        plan = service.get_plan(sample_plan.id)

        assert plan.id == sample_plan.id

    def test_get_plan_not_found_raises_error(self, db_session):
        service = PlanService(db_session)

        with pytest.raises(HTTPException) as exc_info:
            service.get_plan(99999)

        assert exc_info.value.status_code == 404

    def test_get_active_plans(self, db_session, sample_plan, expired_plan, future_plan):
        service = PlanService(db_session)

        active_plans = service.get_active_plans()

        plan_ids = [p.id for p in active_plans]
        assert sample_plan.id in plan_ids
        assert expired_plan.id not in plan_ids
        assert future_plan.id not in plan_ids

    def test_get_active_plans_with_custom_time(
        self, db_session, sample_plan, future_plan
    ):
        service = PlanService(db_session)
        future_time = datetime.now(datetime_UTC) + timedelta(days=60)

        active_plans = service.get_active_plans(current_time=future_time)

        plan_ids = [p.id for p in active_plans]
        assert future_plan.id in plan_ids

    def test_update_plan(self, db_session, sample_plan):
        service = PlanService(db_session)
        update_data = PlanUpdate(name="Updated Plan Name")

        plan = service.update_plan(sample_plan.id, update_data)

        assert plan.name == "Updated Plan Name"

    def test_delete_plan(self, db_session, sample_plan):
        service = PlanService(db_session)
        plan_id = sample_plan.id

        service.delete_plan(plan_id)

        with pytest.raises(HTTPException):
            service.get_plan(plan_id)


class TestSubscriptionService:
    def test_create_subscription(self, db_session, sample_user, sample_plan):
        service = SubscriptionService(db_session)
        subscription_data = SubscriptionCreate(
            user_id=sample_user.id,
            plan_id=sample_plan.id,
            start_date=datetime.now(datetime_UTC),
        )

        subscription = service.create_subscription(subscription_data)

        assert subscription.id is not None
        assert subscription.user_id == sample_user.id
        assert subscription.plan_id == sample_plan.id
        assert subscription.status == SubscriptionStatus.ACTIVE.value

    def test_create_subscription_for_simulation_user_raises_error(
        self, db_session, simulation_user, sample_plan
    ):
        service = SubscriptionService(db_session)
        subscription_data = SubscriptionCreate(
            user_id=simulation_user.id,
            plan_id=sample_plan.id,
            start_date=datetime.now(datetime_UTC),
        )

        with pytest.raises(HTTPException) as exc_info:
            service.create_subscription(subscription_data)

        assert exc_info.value.status_code == 400
        assert "simulation mode" in str(exc_info.value.detail).lower()

    def test_create_subscription_when_user_has_active_raises_error(
        self, db_session, sample_subscription, sample_user, sample_plan
    ):
        service = SubscriptionService(db_session)
        subscription_data = SubscriptionCreate(
            user_id=sample_user.id,
            plan_id=sample_plan.id,
            start_date=datetime.now(datetime_UTC),
        )

        with pytest.raises(HTTPException) as exc_info:
            service.create_subscription(subscription_data)

        assert exc_info.value.status_code == 400
        assert "already has an active subscription" in str(exc_info.value.detail).lower()

    def test_create_subscription_with_inactive_plan_raises_error(
        self, db_session, sample_user, expired_plan
    ):
        service = SubscriptionService(db_session)
        subscription_data = SubscriptionCreate(
            user_id=sample_user.id,
            plan_id=expired_plan.id,
            start_date=datetime.now(datetime_UTC),
        )

        with pytest.raises(HTTPException) as exc_info:
            service.create_subscription(subscription_data)

        assert exc_info.value.status_code == 400
        assert "not currently active" in str(exc_info.value.detail).lower()

    def test_create_subscription_user_not_found_raises_error(
        self, db_session, sample_plan
    ):
        service = SubscriptionService(db_session)
        subscription_data = SubscriptionCreate(
            user_id=99999,
            plan_id=sample_plan.id,
            start_date=datetime.now(datetime_UTC),
        )

        with pytest.raises(HTTPException) as exc_info:
            service.create_subscription(subscription_data)

        assert exc_info.value.status_code == 404
        assert "User not found" in str(exc_info.value.detail)

    def test_create_subscription_plan_not_found_raises_error(
        self, db_session, sample_user
    ):
        service = SubscriptionService(db_session)
        subscription_data = SubscriptionCreate(
            user_id=sample_user.id,
            plan_id=99999,
            start_date=datetime.now(datetime_UTC),
        )

        with pytest.raises(HTTPException) as exc_info:
            service.create_subscription(subscription_data)

        assert exc_info.value.status_code == 404
        assert "Plan not found" in str(exc_info.value.detail)

    def test_get_subscription(self, db_session, sample_subscription):
        service = SubscriptionService(db_session)

        subscription = service.get_subscription(sample_subscription.id)

        assert subscription.id == sample_subscription.id

    def test_get_subscription_not_found_raises_error(self, db_session):
        service = SubscriptionService(db_session)

        with pytest.raises(HTTPException) as exc_info:
            service.get_subscription(99999)

        assert exc_info.value.status_code == 404

    def test_cancel_subscription(self, db_session, sample_subscription):
        service = SubscriptionService(db_session)

        subscription = service.cancel_subscription(sample_subscription.id)

        assert subscription.status == SubscriptionStatus.CANCELLED.value
        assert subscription.cancelled_at is not None

    def test_cancel_already_cancelled_subscription_raises_error(
        self, db_session, sample_subscription
    ):
        service = SubscriptionService(db_session)
        service.cancel_subscription(sample_subscription.id)

        with pytest.raises(HTTPException) as exc_info:
            service.cancel_subscription(sample_subscription.id)

        assert exc_info.value.status_code == 400
        assert "Only active subscriptions" in str(exc_info.value.detail)

    def test_get_user_subscriptions(self, db_session, sample_subscription, sample_user):
        service = SubscriptionService(db_session)

        subscriptions = service.get_user_subscriptions(sample_user.id)

        assert len(subscriptions) >= 1
        assert subscriptions[0].user_id == sample_user.id

    def test_get_active_subscription(self, db_session, sample_subscription, sample_user):
        service = SubscriptionService(db_session)

        subscription = service.get_active_subscription(sample_user.id)

        assert subscription is not None
        assert subscription.id == sample_subscription.id

    def test_get_active_subscription_returns_none_when_no_active(
        self, db_session, sample_user
    ):
        service = SubscriptionService(db_session)

        subscription = service.get_active_subscription(sample_user.id)

        assert subscription is None


class TestReportService:
    def test_get_subscription_report(self, db_session, sample_subscription):
        service = ReportService(db_session)

        report = service.get_subscription_report()

        assert report.total_subscriptions >= 1
        assert len(report.by_status) >= 1
        assert len(report.by_plan) >= 1

    def test_get_subscription_report_empty(self, db_session):
        service = ReportService(db_session)

        report = service.get_subscription_report()

        assert report.total_subscriptions == 0
        assert report.by_status == []
        assert report.by_plan == []

    def test_get_subscription_report_counts_by_status(
        self, db_session, sample_user, sample_plan
    ):
        from models.subscription import Subscription

        active_sub = Subscription(
            user_id=sample_user.id,
            plan_id=sample_plan.id,
            status=SubscriptionStatus.ACTIVE.value,
            start_date=datetime.now(datetime_UTC),
        )
        db_session.add(active_sub)
        db_session.commit()

        service = ReportService(db_session)
        report = service.get_subscription_report()

        active_count = next(
            (s.count for s in report.by_status if s.status == "active"), 0
        )
        assert active_count >= 1
