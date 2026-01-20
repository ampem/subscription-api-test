from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.plan import Plan
from repositories.plan import PlanRepository
from schemas.plan import PlanCreate, PlanUpdate


class PlanService:
    def __init__(self, db: Session):
        self.repository = PlanRepository(db)

    def get_plan(self, plan_id: int) -> Plan:
        plan = self.repository.get_by_id(plan_id)
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plan not found"
            )
        return plan

    def get_plans(self, skip: int = 0, limit: int = 100) -> list[Plan]:
        return self.repository.get_all(skip=skip, limit=limit)

    def get_active_plans(self, current_time: datetime | None = None) -> list[Plan]:
        return self.repository.get_active_plans(current_time=current_time)

    def create_plan(self, plan_data: PlanCreate) -> Plan:
        return self.repository.create(plan_data)

    def update_plan(self, plan_id: int, plan_data: PlanUpdate) -> Plan:
        plan = self.get_plan(plan_id)
        return self.repository.update(plan, plan_data)

    def delete_plan(self, plan_id: int) -> None:
        plan = self.get_plan(plan_id)
        self.repository.delete(plan)
