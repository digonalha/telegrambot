from pydantic import BaseModel
from datetime import datetime

from src.repositories.models.custom_command_model import MediaType


class CustomCommandBase(BaseModel):
    command: str
    description: str
    file_id: str = None
    media_type: int = int(MediaType.NONE)
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
