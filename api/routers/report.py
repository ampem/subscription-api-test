from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from schemas.report import SubscriptionReportResponse
from services.report import ReportService

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/subscriptions", response_model=SubscriptionReportResponse)
def get_subscription_report(db: Session = Depends(get_db)):
    service = ReportService(db)
    return service.get_subscription_report()
