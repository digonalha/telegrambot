from datetime import datetime
from schemas.user_schemas.user_base import UserBase


class UserUpdate(UserBase):
    modified_on: datetime
