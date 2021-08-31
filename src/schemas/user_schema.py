from pydantic import BaseModel
from datetime import datetime


class UserBase(BaseModel):
    telegram_user_id: int
    telegram_username: str


class UserCreate(UserBase):
    is_admin: bool
    created_on: datetime
    modified_on: datetime


class User(UserBase):
    class Config:
        orm_mode = True
        validate_assignment = True
