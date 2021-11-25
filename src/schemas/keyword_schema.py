from pydantic import BaseModel
from datetime import datetime


class KeywordBase(BaseModel):
    user_id: int
    keyword: str
    max_price: int = None


class KeywordCreate(KeywordBase):
    created_on: datetime
    modified_on: datetime


class KeywordUpdate(KeywordBase):
    modified_on: datetime


class Keyword(KeywordBase):
    class Config:
        orm_mode = True
        validate_assignment = True
