from domain.schemas.command_schemas.command_base import CommandBase


class Command(CommandBase):
    class Config:
        orm_mode = True
