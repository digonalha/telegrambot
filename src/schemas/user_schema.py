from pydantic import BaseModel
from datetime import datetime


class UserBase(BaseModel):
    user_id: int


class UserCreate(UserBase):
    user_name: str
    first_name: str
    is_admin: bool
    table_width: int = None
    created_on: datetime
    modified_on: datetime


class UserUpdate(UserBase):
    user_name: str
    first_name: str
    modified_on: datetime


class UserUpdateWidth(UserBase):
    table_width: int
    modified_on: datetime


class User(UserBase):
    class Config:
        orm_mode = True
        validate_assignment = True
