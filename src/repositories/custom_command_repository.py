from src.schemas import custom_command_schema
from src.repositories.database import database
from src.repositories.models import custom_command_model

local_session = database.get()


def add(custom_command: custom_command_schema.CustomCommandCreate):
    new_custom_command = custom_command_model.CustomCommand(**custom_command.dict())

    local_session.add(new_custom_command)
    local_session.commit()
    local_session.refresh(new_custom_command)

    return new_custom_command


def delete(command_name: str, chat_id: int):
    local_session.query(custom_command_model.CustomCommand).filter(
        custom_command_model.CustomCommand.telegram_user_id == command_name
        and custom_command_model.CustomCommand.chat_id == chat_id
    ).delete()

    local_session.commit()


def get_all():
    return local_session.query(custom_command_model.CustomCommand).all()


def get(command_name: str, chat_id: int):
    return (
        local_session.query(custom_command_model.CustomCommand)
        .filter(
            custom_command_model.CustomCommand.telegram_user_id == command_name
            and custom_command_model.CustomCommand.chat_id == chat_id
        )
        .first()
    )
