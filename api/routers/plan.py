from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database import get_db
from schemas.plan import PlanCreate, PlanUpdate, PlanResponse
from services.plan import PlanService

router = APIRouter(prefix="/plans", tags=["plans"])


@router.get("", response_model=list[PlanResponse])
def get_plans(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    service = PlanService(db)
    return service.get_plans(skip=skip, limit=limit)


@router.get("/active", response_model=list[PlanResponse])
def get_active_plans(db: Session = Depends(get_db)):
    service = PlanService(db)
    return service.get_active_plans()


@router.get("/{plan_id}", response_model=PlanResponse)
def get_plan(plan_id: int, db: Session = Depends(get_db)):
    service = PlanService(db)
    return service.get_plan(plan_id)


@router.post("", response_model=PlanResponse, status_code=status.HTTP_201_CREATED)
def create_plan(plan_data: PlanCreate, db: Session = Depends(get_db)):
    service = PlanService(db)
    return service.create_plan(plan_data)


@router.patch("/{plan_id}", response_model=PlanResponse)
def update_plan(plan_id: int, plan_data: PlanUpdate, db: Session = Depends(get_db)):
    service = PlanService(db)
    return service.update_plan(plan_id, plan_data)


@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_plan(plan_id: int, db: Session = Depends(get_db)):
    service = PlanService(db)
    service.delete_plan(plan_id)
