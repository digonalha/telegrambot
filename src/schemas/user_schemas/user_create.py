from datetime import datetime
from schemas.user_schemas.user_base import UserBase


class UserCreate(UserBase):
    is_admin: bool
    created_on: datetime
    modified_on: datetime
