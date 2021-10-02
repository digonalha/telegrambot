from pydantic import BaseModel
from datetime import datetime


class CustomCommandBase(BaseModel):
    command: str
    description: str
    file_id: str = None
    media_type: str = None
    text: str = None
    chat_id: int
    created_by_user_id: int
    created_by_user_name: str


class CustomCommandCreate(CustomCommandBase):
    created_on: datetime
    modified_on: datetime


class CustomCommand(CustomCommandBase):
    class Config:
        orm_mode = True
