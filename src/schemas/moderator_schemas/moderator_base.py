from pydantic import BaseModel


class ModeratorBase(BaseModel):
    user_id: int
    chat_id: int
