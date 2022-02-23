from domain.schemas.command_schemas.command_base import CommandBase


class Command(CommandBase):
    id: int

    class Config:
        orm_mode = True
