from pydantic import BaseModel
from shared.enums.media_type import MediaType


class CommandBase(BaseModel):
    command: str
    description: str
    file_id: str = None
    media_type: int = int(MediaType.NONE)
    text: str = None
    chat_id: int
    created_by_user_id: int
    created_by_user_name: str
