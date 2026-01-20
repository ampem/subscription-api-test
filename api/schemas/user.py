from datetime import datetime

from pydantic import BaseModel, EmailStr

from models.user import UserMode


class UserBase(BaseModel):
    email: EmailStr
    name: str
    mode: UserMode = UserMode.LIVE


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    name: str | None = None
    mode: UserMode | None = None


class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
