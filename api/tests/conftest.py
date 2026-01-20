from datetime import UTC as datetime_UTC
from datetime import datetime, timedelta
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base
from models.user import User, UserMode
from models.plan import Plan, PlanTier
from models.subscription import Subscription, SubscriptionStatus


@pytest.fixture
def engine():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(engine):
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def sample_user(db_session):
    user = User(
        email="test@example.com",
        name="Test User",
        mode=UserMode.LIVE.value,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def simulation_user(db_session):
    user = User(
        email="sim@example.com",
        name="Simulation User",
        mode=UserMode.SIMULATION.value,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def sample_plan(db_session):
    plan = Plan(
        name="Basic Monthly",
        tier=PlanTier.BASIC.value,
        description="Basic monthly plan",
        price=Decimal("9.99"),
        billing_period="monthly",
        active_from=datetime.now(datetime_UTC) - timedelta(days=30),
        active_to=None,
        simulation=False,
    )
    db_session.add(plan)
    db_session.commit()
    db_session.refresh(plan)
    return plan


@pytest.fixture
def expired_plan(db_session):
    plan = Plan(
        name="Old Plan",
        tier=PlanTier.FREE.value,
        description="Expired plan",
        price=Decimal("0.00"),
        billing_period="monthly",
        active_from=datetime.now(datetime_UTC) - timedelta(days=365),
        active_to=datetime.now(datetime_UTC) - timedelta(days=30),
        simulation=False,
    )
    db_session.add(plan)
    db_session.commit()
    db_session.refresh(plan)
    return plan


@pytest.fixture
def future_plan(db_session):
    plan = Plan(
        name="Future Plan",
        tier=PlanTier.PRO.value,
        description="Not yet active",
        price=Decimal("29.99"),
        billing_period="monthly",
        active_from=datetime.now(datetime_UTC) + timedelta(days=30),
        active_to=None,
        simulation=False,
    )
    db_session.add(plan)
    db_session.commit()
    db_session.refresh(plan)
    return plan


@pytest.fixture
def sample_subscription(db_session, sample_user, sample_plan):
    subscription = Subscription(
        user_id=sample_user.id,
        plan_id=sample_plan.id,
        status=SubscriptionStatus.ACTIVE.value,
        start_date=datetime.now(datetime_UTC) - timedelta(days=15),
        end_date=datetime.now(datetime_UTC) + timedelta(days=15),
    )
    db_session.add(subscription)
    db_session.commit()
    db_session.refresh(subscription)
    return subscription
