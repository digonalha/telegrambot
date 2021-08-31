from pydantic import BaseModel
from datetime import datetime


class ModeratorBase(BaseModel):
    telegram_user_id: int
    chat_id: int


class ModeratorCreate(ModeratorBase):
    created_on: datetime


class Moderator(ModeratorBase):
    class Config:
        orm_mode = True
