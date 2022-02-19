from pydantic import BaseModel


class UserBase(BaseModel):
    user_id: int
    user_name: str
    first_name: str
