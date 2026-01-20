#!/usr/bin/env python3
"""
Generate seed data SQL for users, plans, and subscriptions.

Usage:
    python scripts/generate_seed_data.py [--users N] [--output FILE]

Options:
    --users N       Number of users to generate (default: 50)
    --output FILE   Output SQL file (default: seed_data.sql)
"""

import argparse
from datetime import datetime, timedelta
from decimal import Decimal
from faker import Faker
import random

fake = Faker()


def escape_sql_string(value: str) -> str:
    """Escape single quotes for SQL strings."""
    return value.replace("'", "''")


def format_datetime(dt: datetime) -> str:
    """Format datetime for SQL."""
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def format_decimal(value: Decimal) -> str:
    """Format decimal for SQL."""
    return f"{value:.2f}"


def generate_plans() -> list[dict]:
    """Generate plan data for current year and next year."""
    plans = []
    now = datetime.utcnow()
    current_year = now.year
    next_year = current_year + 1

    # Base prices for each tier
    base_prices = {
        "free": Decimal("0.00"),
        "basic": Decimal("9.99"),
        "pro": Decimal("29.99"),
    }

    plan_descriptions = {
        "free": "Basic access with limited features",
        "basic": "Standard features for individual users",
        "pro": "Full access with premium features and priority support",
    }

    plan_id = 1

    # Current year plans (active for entire year)
    current_year_start = datetime(current_year, 1, 1, 0, 0, 0)
    current_year_end = datetime(current_year, 12, 31, 23, 59, 59)

    for tier in ["free", "basic", "pro"]:
        for billing_period in ["monthly", "yearly"]:
            price = base_prices[tier]
            if billing_period == "yearly":
                price = price * 10  # 2 months free for yearly

            plans.append({
                "id": plan_id,
                "name": f"{tier.capitalize()} {billing_period.capitalize()} {current_year}",
                "tier": tier,
                "description": plan_descriptions[tier],
                "price": price,
                "billing_period": billing_period,
                "active_from": current_year_start,
                "active_to": current_year_end,
                "simulation": False,
            })
            plan_id += 1

    # Next year plans (10% higher price)
    next_year_start = datetime(next_year, 1, 1, 0, 0, 0)
    next_year_end = datetime(next_year, 12, 31, 23, 59, 59)

    for tier in ["free", "basic", "pro"]:
        for billing_period in ["monthly", "yearly"]:
            price = base_prices[tier] * Decimal("1.10")  # 10% increase
            if billing_period == "yearly":
                price = price * 10

            plans.append({
                "id": plan_id,
                "name": f"{tier.capitalize()} {billing_period.capitalize()} {next_year}",
                "tier": tier,
                "description": plan_descriptions[tier],
                "price": price,
                "billing_period": billing_period,
                "active_from": next_year_start,
                "active_to": next_year_end,
                "simulation": False,
            })
            plan_id += 1

    # Simulation plans (for testing)
    for tier in ["free", "basic", "pro"]:
        plans.append({
            "id": plan_id,
            "name": f"{tier.capitalize()} Simulation",
            "tier": tier,
            "description": f"Simulation plan for {tier} tier testing",
            "price": base_prices[tier],
            "billing_period": "monthly",
            "active_from": current_year_start,
            "active_to": None,
            "simulation": True,
        })
        plan_id += 1

    return plans


def generate_users_and_subscriptions(num_users: int, plans: list[dict]) -> tuple[list[dict], list[dict]]:
    """Generate users with various subscription states."""
    users = []
    subscriptions = []
    now = datetime.utcnow()

    # Get plan IDs by category
    current_year_plans = [p for p in plans if not p["simulation"] and p["active_from"].year == now.year]
    simulation_plans = [p for p in plans if p["simulation"]]

    # Distribution of user types
    # Roughly: 15% no subscription, 10% simulation, 40% active, 20% lapsed, 15% future
    user_types = (
        ["no_subscription"] * 15 +
        ["simulation"] * 10 +
        ["active_free"] * 15 +
        ["active_basic"] * 15 +
        ["active_pro"] * 10 +
        ["lapsed"] * 20 +
        ["future"] * 15
    )

    user_id = 1
    subscription_id = 1

    for i in range(num_users):
        user_type = random.choice(user_types)

        # Create user
        is_simulation = user_type == "simulation"
        user = {
            "id": user_id,
            "email": fake.unique.email(),
            "name": fake.name(),
            "mode": "simulation" if is_simulation else "live",
        }
        users.append(user)

        # Create subscription based on user type
        if user_type == "no_subscription":
            pass  # No subscription for this user

        elif user_type == "simulation":
            # Simulation user with simulation plan
            plan = random.choice(simulation_plans)
            start_date = now - timedelta(days=random.randint(1, 30))
            subscriptions.append({
                "id": subscription_id,
                "user_id": user_id,
                "plan_id": plan["id"],
                "status": "active",
                "start_date": start_date,
                "end_date": None,
                "cancelled_at": None,
            })
            subscription_id += 1

        elif user_type.startswith("active_"):
            # Active subscription
            tier = user_type.replace("active_", "")
            tier_plans = [p for p in current_year_plans if p["tier"] == tier]
            plan = random.choice(tier_plans)

            start_date = now - timedelta(days=random.randint(1, 180))
            end_date = start_date + timedelta(days=365 if plan["billing_period"] == "yearly" else 30)

            subscriptions.append({
                "id": subscription_id,
                "user_id": user_id,
                "plan_id": plan["id"],
                "status": "active",
                "start_date": start_date,
                "end_date": end_date,
                "cancelled_at": None,
            })
            subscription_id += 1

        elif user_type == "lapsed":
            # Lapsed subscription (end_date in the past)
            plan = random.choice(current_year_plans)
            days_ago = random.randint(30, 365)
            start_date = now - timedelta(days=days_ago + 30)
            end_date = now - timedelta(days=random.randint(1, 29))

            status = random.choice(["expired", "cancelled"])
            cancelled_at = end_date - timedelta(days=random.randint(1, 5)) if status == "cancelled" else None

            subscriptions.append({
                "id": subscription_id,
                "user_id": user_id,
                "plan_id": plan["id"],
                "status": status,
                "start_date": start_date,
                "end_date": end_date,
                "cancelled_at": cancelled_at,
            })
            subscription_id += 1

        elif user_type == "future":
            # Future subscription (start_date in the future)
            plan = random.choice(current_year_plans)
            start_date = now + timedelta(days=random.randint(1, 60))
            end_date = start_date + timedelta(days=365 if plan["billing_period"] == "yearly" else 30)

            subscriptions.append({
                "id": subscription_id,
                "user_id": user_id,
                "plan_id": plan["id"],
                "status": "active",
                "start_date": start_date,
                "end_date": end_date,
                "cancelled_at": None,
            })
            subscription_id += 1

        user_id += 1

    return users, subscriptions


def generate_sql(plans: list[dict], users: list[dict], subscriptions: list[dict]) -> str:
    """Generate SQL statements for all data."""
    now = datetime.utcnow()
    sql_lines = [
        "-- Seed data generated at " + format_datetime(now),
        "-- This script clears existing data and repopulates the database",
        "",
        "-- Disable foreign key checks for truncation",
        "SET FOREIGN_KEY_CHECKS = 0;",
        "",
        "-- Clear existing data",
        "TRUNCATE TABLE subscriptions;",
        "TRUNCATE TABLE users;",
        "TRUNCATE TABLE plans;",
        "",
        "SET FOREIGN_KEY_CHECKS = 1;",
        "",
        "-- ============================================",
        "-- Plans",
        "-- ============================================",
        "",
    ]

    # Generate plan inserts
    for plan in plans:
        active_to = f"'{format_datetime(plan['active_to'])}'" if plan["active_to"] else "NULL"
        simulation = 1 if plan["simulation"] else 0
        sql_lines.append(
            f"INSERT INTO plans (id, name, tier, description, price, billing_period, active_from, active_to, simulation, created_at, updated_at) VALUES ("
            f"{plan['id']}, "
            f"'{escape_sql_string(plan['name'])}', "
            f"'{plan['tier']}', "
            f"'{escape_sql_string(plan['description'])}', "
            f"{format_decimal(plan['price'])}, "
            f"'{plan['billing_period']}', "
            f"'{format_datetime(plan['active_from'])}', "
            f"{active_to}, "
            f"{simulation}, "
            f"'{format_datetime(now)}', "
            f"'{format_datetime(now)}'"
            f");"
        )

    sql_lines.extend([
        "",
        "-- ============================================",
        "-- Users",
        "-- ============================================",
        "",
    ])

    # Generate user inserts
    for user in users:
        sql_lines.append(
            f"INSERT INTO users (id, email, name, mode, created_at, updated_at) VALUES ("
            f"{user['id']}, "
            f"'{escape_sql_string(user['email'])}', "
            f"'{escape_sql_string(user['name'])}', "
            f"'{user['mode']}', "
            f"'{format_datetime(now)}', "
            f"'{format_datetime(now)}'"
            f");"
        )

    sql_lines.extend([
        "",
        "-- ============================================",
        "-- Subscriptions",
        "-- ============================================",
        "",
    ])

    # Generate subscription inserts
    for sub in subscriptions:
        end_date = f"'{format_datetime(sub['end_date'])}'" if sub["end_date"] else "NULL"
        cancelled_at = f"'{format_datetime(sub['cancelled_at'])}'" if sub["cancelled_at"] else "NULL"
        sql_lines.append(
            f"INSERT INTO subscriptions (id, user_id, plan_id, status, start_date, end_date, cancelled_at, created_at, updated_at) VALUES ("
            f"{sub['id']}, "
            f"{sub['user_id']}, "
            f"{sub['plan_id']}, "
            f"'{sub['status']}', "
            f"'{format_datetime(sub['start_date'])}', "
            f"{end_date}, "
            f"{cancelled_at}, "
            f"'{format_datetime(now)}', "
            f"'{format_datetime(now)}'"
            f");"
        )

    sql_lines.extend([
        "",
        "-- ============================================",
        "-- Summary",
        "-- ============================================",
        f"-- Plans: {len(plans)}",
        f"-- Users: {len(users)}",
        f"-- Subscriptions: {len(subscriptions)}",
        "",
    ])

    return "\n".join(sql_lines)


def main():
    parser = argparse.ArgumentParser(description="Generate seed data SQL for the subscription API")
    parser.add_argument("--users", type=int, default=50, help="Number of users to generate (default: 50)")
    parser.add_argument("--output", type=str, default="seed_data.sql", help="Output SQL file (default: seed_data.sql)")
    args = parser.parse_args()

    print(f"Generating seed data with {args.users} users...")

    plans = generate_plans()
    print(f"  Generated {len(plans)} plans")

    users, subscriptions = generate_users_and_subscriptions(args.users, plans)
    print(f"  Generated {len(users)} users")
    print(f"  Generated {len(subscriptions)} subscriptions")

    sql = generate_sql(plans, users, subscriptions)

    with open(args.output, "w") as f:
        f.write(sql)

    print(f"Seed data written to {args.output}")


if __name__ == "__main__":
    main()
