from pydantic import BaseModel
from datetime import datetime


class CustomCommandBase(BaseModel):
    command: str
    description: str
    telegram_file_id: str
    text: str
    chat_id: int


class CustomCommandCreate(CustomCommandBase):
    created_by_user_id: int
    created_by_username: str
    created_on: datetime
    modified_on: datetime


class CustomCommand(CustomCommandBase):
    class Config:
        orm_mode = True
