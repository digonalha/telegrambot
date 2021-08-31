from pydantic import BaseModel
from datetime import datetime


class CustomCommandBase(BaseModel):
    telegram_user_id: int
    chat_id: int


class CustomCommandCreate(CustomCommandBase):
    created_on: datetime


class CustomCommand(CustomCommandBase):
    class Config:
        orm_mode = True
