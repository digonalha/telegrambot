from pydantic import BaseModel
from datetime import datetime


class SaleTrackerKeywordBase(BaseModel):
    user_id: int
    user_name: str
    chat_id: int
    keyword: str


class SaleTrackerKeywordCreate(SaleTrackerKeywordBase):
    created_on: datetime
    modified_on: datetime


class SaleTrackerKeyword(SaleTrackerKeywordBase):
    id: int

    class Config:
        orm_mode = True
        validate_assignment = True
