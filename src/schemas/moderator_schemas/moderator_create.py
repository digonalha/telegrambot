from datetime import datetime
from schemas.moderator_schemas.moderator_base import ModeratorBase


class ModeratorCreate(ModeratorBase):
    created_on: datetime
