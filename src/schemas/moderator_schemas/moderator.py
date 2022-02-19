from schemas.moderator_schemas.moderator_base import ModeratorBase


class Moderator(ModeratorBase):
    class Config:
        orm_mode = True
