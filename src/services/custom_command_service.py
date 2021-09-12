from datetime import datetime

from sqlalchemy.sql.expression import desc
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
                    "file_id": command.file_id,
                    "media_type": command.media_type,
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
                "file_id": db_custom_command.file_id,
                "media_type": db_custom_command.media_type,
            }
        )
        return True

    return False


def insert_command(
    chat_id: int,
    message_text: str,
    send_by_user_id: int,
    file_id: str = None,
    media_type: str = None,
):
    try:
        using_pipe = False
        word_list = []
        command, new_custom_command, answer, description = "", "", "", ""

        if " -c " in message_text:
            word_list = message_text.split("-")
        else:
            word_list = message_text.split("|")
            using_pipe = True

        stripped_list = [w.strip() for w in word_list]

        if using_pipe:
            command, new_custom_command = stripped_list[0].split()
            answer = stripped_list[1]
            description = stripped_list[2]
        else:
            command = stripped_list[0]

            sl_command = next((x for x in stripped_list if x.startswith("c ")), None)
            sl_answer = next((x for x in stripped_list if x.startswith("a ")), None)
            sl_desc = next((x for x in stripped_list if x.startswith("d ")), None)

            if sl_command != None:
                new_custom_command = sl_command.split("c ", 1)[1]
            if sl_answer != None:
                answer = sl_answer.split("a ", 1)[1]
            if sl_desc != None:
                description = sl_desc.split("d ", 1)[1]

        new_custom_command = new_custom_command.replace('!', '')

        if command != "!add":
            raise Exception("unknow command: " + command)
        elif len(new_custom_command) < 3 or len(new_custom_command) > 15:
            message_service.send_message(
                chat_id,
                "O novo comando deve ter entre 2 e 15 caracteres",
            )
            return
        elif media_type == None and (len(answer) < 5 or len(answer) > 1000):
            message_service.send_message(
                chat_id,
                "A resposta deve ter entre 5 e 1000 caracteres",
            )
            return
        elif len(description) < 5 or len(description) > 150:
            message_service.send_message(
                chat_id,
                "A descrição deve ter entre 5 e 150 caracteres",
            )
            return
    except Exception as ex:
        message_service.send_message(
            chat_id,
            "Para criar um novo comando, utilize:\n*!add <comando> | <resposta> | <descrição>*\nou\n*!add -c <comando> -a <resposta> -d <descrição>*",
        )
        syslog.create_warning("insert_command", ex)
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

        if file_id != None and media_type != None:
            new_custom_command_obj["file_id"] = file_id
            new_custom_command_obj["media_type"] = media_type

        if add_custom_command(new_custom_command_obj):
            message = f"Novo comando *!{new_custom_command}* criado!"
        else:
            message = f"O comando *!{new_custom_command}* já existe"
    except Exception as ex:
        syslog.create_warning("insert_command", ex)
    finally:
        message_service.send_message(chat_id, message)
