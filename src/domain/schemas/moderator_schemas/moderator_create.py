from datetime import datetime
from domain.schemas.moderator_schemas.moderator_base import ModeratorBase


class ModeratorCreate(ModeratorBase):
    created_on: datetime
