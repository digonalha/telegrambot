from datetime import datetime
from domain.schemas.user_schemas.user_base import UserBase


class UserUpdate(UserBase):
    modified_on: datetime
