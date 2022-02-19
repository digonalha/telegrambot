from datetime import datetime
from schemas.command_schemas.command_base import CommandBase


class CommandCreate(CommandBase):
    created_on: datetime
    modified_on: datetime
