from datetime import datetime
from src.helpers.logging_helper import SystemLogging
from src.repositories import custom_command_repository
from src.schemas import custom_command_schema
from src.services import user_service, message_service

custom_commands = []
syslog = SystemLogging(__name__)


def get_command(command: str, chat_id: int):
    return next(
        (
            cc
            for cc in custom_commands
            if cc["command"] == command and cc["chat_id"] == chat_id
        ),
        None,
    )


def get_all():
    global custom_commands
    try:
        commands = custom_command_repository.get_all()
        custom_commands = []

        for command in commands:
            custom_commands.append(
                {
                    "command": command.command,
                    "text": command.text,
                    "description": command.description,
                    "chat_id": command.chat_id,
                }
            )
    except:
        return custom_commands


def add_custom_command(new_command):
    if len(custom_commands) > 0 and next(
        (
            cc
            for cc in custom_commands
            if cc["command"] == new_command["command"]
            and cc["chat_id"] == new_command["chat_id"]
        ),
        None,
    ):
        return False

    db_custom_command = None

    custom_command_already_in_db = custom_command_repository.get(
        new_command["command"], new_command["chat_id"]
    )

    custom_command = custom_command_schema.CustomCommandCreate(**new_command)

    if not custom_command_already_in_db:
        db_custom_command = custom_command_repository.add(custom_command)
        custom_commands.append(
            {
                "command": db_custom_command.command,
                "text": db_custom_command.text,
                "description": db_custom_command.description,
                "chat_id": db_custom_command.chat_id,
            }
        )
        return True

    return False


def insert_custom_command(chat_id: int, message_text: str, send_by_user_id: int):
    try:
        command, answer, description = message_text.split("|")
        command, new_custom_command = command.split()

        command.strip()
        new_custom_command.strip()

        if command != "!newcommand":
            raise Exception("unknow command: " + command)
        elif len(new_custom_command) < 3:
            raise Exception("error creating custom command: " + new_custom_command)
    except Exception as ex:
        message_service.send_message(
            chat_id,
            "Para criar um novo comando, utilize *!newcommand <comando> | <resposta> | <descrição>*",
        )
        syslog.create_warning("insert_custom_command", ex)
        return

    message = "Não foi possível cadastrar o novo comando :("

    try:
        if not user_service.validate_user_permission(chat_id, send_by_user_id):
            return

        user = user_service.get_user(send_by_user_id)
        now = datetime.now()

        new_custom_command_obj = {
            "command": new_custom_command,
            "text": answer.strip(),
            "description": description.strip(),
            "chat_id": chat_id,
            "created_by_user_id": user["user_id"],
            "created_by_username": user["username"],
            "created_on": now,
            "modified_on": now,
        }

        if add_custom_command(new_custom_command_obj):
            message = f"Novo comando *!{new_custom_command}* criado!"
        else:
            message = f"O comando *!{new_custom_command}* já existe"
    except Exception as ex:
        syslog.create_warning("insert_custom_command", ex)
    finally:
        message_service.send_message(chat_id, message)
