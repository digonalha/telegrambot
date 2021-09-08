from pydantic import BaseModel
from datetime import datetime


class CustomCommandBase(BaseModel):
    command: str
    description: str
    telegram_file_id: str = None
    text: str = None
    chat_id: int
    created_by_user_id: int
    created_by_username: str


class CustomCommandCreate(CustomCommandBase):
    created_on: datetime
    modified_on: datetime


class CustomCommand(CustomCommandBase):
    class Config:
        orm_mode = True
