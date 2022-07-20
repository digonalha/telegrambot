from sqlalchemy import func, text

from data.database import database
from domain.schemas.command_schemas.command_create import CommandCreate
from domain.models.command import Command


def add(command: CommandCreate):
    local_session = database.get()
    new_command = Command(**command.dict())

    local_session.add(new_command)
    local_session.commit()
    local_session.refresh(new_command)

    return new_command


def delete(command: str, chat_id: int):
    local_session = database.get()
    local_session.query(Command).filter(
        func.lower(Command.command) == command.lower(),
        Command.chat_id == chat_id,
    ).delete(synchronize_session="fetch")

    local_session.commit()


def get_all():
    return database.get().query(Command).all()


def get(command: str, chat_id: int):
    return (
        database.get()
        .query(Command)
        .filter(
            func.lower(Command.command) == command.lower(),
            Command.chat_id == chat_id,
        )
        .first()
    )


def count_by_chat_id(chat_id: int) -> int:
    result = (
        database.get()
        .execute(
            text("SELECT COUNT(*) FROM command WHERE chat_id = :id"),
            {"id": chat_id},
        )
        .scalar()
    )

    return result
