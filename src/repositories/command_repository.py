from sqlalchemy import func, text
from schemas.command_schemas.command_create import CommandCreate
from database import database
from models.command import Command

local_session = database.get()


def add(command: CommandCreate):
    new_command = Command(**command.dict())

    local_session.add(new_command)
    local_session.commit()
    local_session.refresh(new_command)

    return new_command


def delete(command: str, chat_id: int):
    local_session.query(Command).filter(
        func.lower(Command.command) == command.lower(),
        Command.chat_id == chat_id,
    ).delete(synchronize_session="fetch")

    local_session.commit()


def get_all():
    return local_session.query(Command).all()


def get(command: str, chat_id: int):
    return (
        local_session.query(Command)
        .filter(
            func.lower(Command.command) == command.lower(),
            Command.chat_id == chat_id,
        )
        .first()
    )


def count_by_chat_id(chat_id: int) -> int:
    result = local_session.execute(
        text("SELECT COUNT(*) FROM command WHERE chat_id = :id"),
        {"id": chat_id},
    ).scalar()

    return result
