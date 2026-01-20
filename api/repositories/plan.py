from datetime import datetime

from sqlalchemy.orm import Session

from models.plan import Plan
from schemas.plan import PlanCreate, PlanUpdate


class PlanRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, plan_id: int) -> Plan | None:
        return self.db.query(Plan).filter(Plan.id == plan_id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> list[Plan]:
        return self.db.query(Plan).offset(skip).limit(limit).all()

    def get_active_plans(self, current_time: datetime | None = None) -> list[Plan]:
        if current_time is None:
            current_time = datetime.utcnow()
        return (
            self.db.query(Plan)
            .filter(Plan.active_from <= current_time)
            .filter((Plan.active_to.is_(None)) | (Plan.active_to >= current_time))
            .all()
        )

    def create(self, plan_data: PlanCreate) -> Plan:
        plan = Plan(**plan_data.model_dump())
        self.db.add(plan)
        self.db.commit()
        self.db.refresh(plan)
        return plan

    def update(self, plan: Plan, plan_data: PlanUpdate) -> Plan:
        update_data = plan_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(plan, field, value)
        self.db.commit()
        self.db.refresh(plan)
        return plan

    def delete(self, plan: Plan) -> None:
        self.db.delete(plan)
        self.db.commit()
