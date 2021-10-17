from pydantic import BaseModel
from datetime import datetime


class KeywordBase(BaseModel):
    user_id: int
    keyword: str


class KeywordCreate(KeywordBase):
    created_on: datetime


class Keyword(KeywordBase):
    class Config:
        orm_mode = True
        validate_assignment = True