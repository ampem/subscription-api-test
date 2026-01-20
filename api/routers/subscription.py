from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database import get_db
from schemas.subscription import (
    SubscriptionCreate,
    SubscriptionUpdate,
    SubscriptionResponse,
    SubscriptionDetailResponse,
)
from services.subscription import SubscriptionService

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


@router.get("", response_model=list[SubscriptionDetailResponse])
def get_subscriptions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    service = SubscriptionService(db)
    return service.get_subscriptions(skip=skip, limit=limit)


@router.get("/{subscription_id}", response_model=SubscriptionDetailResponse)
def get_subscription(subscription_id: int, db: Session = Depends(get_db)):
    service = SubscriptionService(db)
    return service.get_subscription(subscription_id)


@router.get("/user/{user_id}", response_model=list[SubscriptionResponse])
def get_user_subscriptions(user_id: int, db: Session = Depends(get_db)):
    service = SubscriptionService(db)
    return service.get_user_subscriptions(user_id)


@router.get("/user/{user_id}/active", response_model=SubscriptionResponse | None)
def get_active_subscription(user_id: int, db: Session = Depends(get_db)):
    service = SubscriptionService(db)
    return service.get_active_subscription(user_id)


@router.post("", response_model=SubscriptionResponse, status_code=status.HTTP_201_CREATED)
def create_subscription(subscription_data: SubscriptionCreate, db: Session = Depends(get_db)):
    service = SubscriptionService(db)
    return service.create_subscription(subscription_data)


@router.patch("/{subscription_id}", response_model=SubscriptionResponse)
def update_subscription(
    subscription_id: int,
    subscription_data: SubscriptionUpdate,
    db: Session = Depends(get_db),
):
    service = SubscriptionService(db)
    return service.update_subscription(subscription_id, subscription_data)


@router.post("/{subscription_id}/cancel", response_model=SubscriptionResponse)
def cancel_subscription(subscription_id: int, db: Session = Depends(get_db)):
    service = SubscriptionService(db)
    return service.cancel_subscription(subscription_id)


@router.delete("/{subscription_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subscription(subscription_id: int, db: Session = Depends(get_db)):
    service = SubscriptionService(db)
    service.delete_subscription(subscription_id)
