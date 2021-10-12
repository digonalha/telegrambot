from sqlalchemy import func
from src.schemas import custom_command_schema
from src.repositories.database import database
from src.repositories.models.custom_command_model import CustomCommand

local_session = database.get()


def add(custom_command: custom_command_schema.CustomCommandCreate):
    new_custom_command = CustomCommand(**custom_command.dict())

    local_session.add(new_custom_command)
    local_session.commit()
    local_session.refresh(new_custom_command)

    return new_custom_command


def delete(command: str, chat_id: int):
    local_session.query(CustomCommand).filter(
        func.lower(CustomCommand.command) == command.lower(),
        CustomCommand.chat_id == chat_id,
    ).delete(synchronize_session="fetch")

    local_session.commit()


def get_all():
    return local_session.query(CustomCommand).all()


def get(command: str, chat_id: int):
    return (
        local_session.query(CustomCommand)
        .filter(
            func.lower(CustomCommand.command) == command.lower(),
            CustomCommand.chat_id == chat_id,
        )
        .first()
    )
