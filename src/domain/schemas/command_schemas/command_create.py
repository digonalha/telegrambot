from datetime import datetime
from domain.schemas.command_schemas.command_base import CommandBase


class CommandCreate(CommandBase):
    created_on: datetime
    modified_on: datetime
