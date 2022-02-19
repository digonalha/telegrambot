from schemas.user_schemas.user_base import UserBase


class User(UserBase):
    class Config:
        orm_mode = True
        validate_assignment = True
