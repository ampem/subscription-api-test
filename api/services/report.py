from sqlalchemy.orm import Session

from repositories.subscription import SubscriptionRepository
from schemas.report import (
    SubscriptionReportResponse,
    SubscriptionsByStatusReport,
    SubscriptionsByPlanReport,
)


class ReportService:
    def __init__(self, db: Session):
        self.subscription_repository = SubscriptionRepository(db)

    def get_subscription_report(self) -> SubscriptionReportResponse:
        total = self.subscription_repository.count_total()

        by_status_raw = self.subscription_repository.count_by_status()
        by_status = [
            SubscriptionsByStatusReport(status=status, count=count)
            for status, count in by_status_raw
        ]

        by_plan_raw = self.subscription_repository.count_by_plan()
        by_plan = [
            SubscriptionsByPlanReport(plan_name=name, tier=tier, count=count)
            for name, tier, count in by_plan_raw
        ]

        return SubscriptionReportResponse(
            total_subscriptions=total,
            by_status=by_status,
            by_plan=by_plan,
        )
