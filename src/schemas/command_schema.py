from pydantic import BaseModel
from datetime import datetime
from models.command import MediaType


class CommandBase(BaseModel):
    command: str
    description: str
    file_id: str = None
    media_type: int = int(MediaType.NONE)
    text: str = None
    chat_id: int
    created_by_user_id: int
    created_by_user_name: str


class CommandCreate(CommandBase):
    created_on: datetime
    modified_on: datetime


class Command(CommandBase):
    class Config:
        orm_mode = True
