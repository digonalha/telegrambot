from datetime import datetime
from src.helpers.logging_helper import SystemLogging
from src.repositories import custom_command_repository
from src.schemas import custom_command_schema
from src.services import user_service, message_service

custom_commands = []
syslog = SystemLogging(__name__)


def get_all():
    global custom_commands
    try:
        mods = custom_command_repository.get_all()
        custom_commands = []

        for mod in mods:
            custom_commands.append(
                {
                    "user_id": mod.telegram_user_id,
                    "chat_id": mod.chat_id,
                }
            )
    except:
        return custom_commands


def add_custom_command(custom_command: custom_command_schema.CustomCommandCreate):
    db_custom_command = None

    custom_command_already_in_db = custom_command_repository.get(
        custom_command.command, custom_command.chat_id
    )

    if not custom_command_already_in_db:
        db_custom_command = custom_command_repository.add(custom_command)

    return db_custom_command


def add_custom_command_if_not_exists(user_id, chat_id):
    result = False

    if len(custom_commands) > 0 and next(
        (
            m
            for m in custom_commands
            if m["user_id"] == user_id and m["chat_id"] == chat_id
        ),
        None,
    ):
        return True

    db_custom_command = add_custom_command(user_id, chat_id)

    if db_custom_command != None:
        custom_commands.append(
            {
                "user_id": db_custom_command.telegram_user_id,
                "chat_id": db_custom_command.chat_id,
            }
        )

    return result


def insert_custom_command(chat_id, message_text: str, send_by_user_id: int):
    try:
        command, username = message_text.split()

        if command != "!newcommand":
            raise Exception("unknow command: " + command)
    except Exception as ex:
        message_service.send_message(
            chat_id,
            "Para criar um novo comando, utilize *!newcommand <resposta> <descrição>*",
        )
        syslog.create_warning("insert_moderator", ex)
        return

    user = user_service.validate_user_command(chat_id, send_by_user_id, username)

    if not user:
        return

    if not add_custom_command(user["user_id"], chat_id):
        message_service.send_message(chat_id, f"Novo comando *!{command}* criado!")
    else:
        message_service.send_message(chat_id, f"O comando *!{command}* já existe")
