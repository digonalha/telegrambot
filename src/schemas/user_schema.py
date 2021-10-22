from pydantic import BaseModel
from datetime import datetime


class UserBase(BaseModel):
    user_id: int
    user_name: str
    first_name: str


class UserCreate(UserBase):
    is_admin: bool
    created_on: datetime
    modified_on: datetime


class UserUpdate(UserBase):
    modified_on: datetime


class User(UserBase):
    class Config:
        orm_mode = True
        validate_assignment = True
