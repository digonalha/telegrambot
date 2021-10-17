from datetime import datetime
from src.repositories.models.custom_command_model import CustomCommand, MediaType
from src.helpers.logging_helper import SystemLogging
from src.helpers import string_helper
from src.repositories import custom_command_repository
from src.schemas import custom_command_schema
from src.services import user_service, message_service
from src.configs import settings

custom_commands = []
syslog = SystemLogging(__name__)


default_commands = [
    "help",
    "mod",
    "unmod",
    "mute",
    "unmute",
    "cmd",
    "addcmd",
    "delcmd",
    "promo",
    "addpromo",
    "delpromo",
    "clearpromo",
]


def get_command(command: str, chat_id: int) -> CustomCommand:
    """Get command if exists on global users variable."""
    return next(
        (
            cc
            for cc in custom_commands
            if cc.command.lower() == command and cc.chat_id == chat_id
        ),
        None,
    )


def get_all_commands() -> None:
    """Fill the global variable commands with all commands found in database."""
    global custom_commands
    custom_commands = custom_command_repository.get_all()


def add_custom_command(new_command: dict) -> bool:
    """Create a new custom_command on database if not exists."""
    if len(custom_commands) > 0 and next(
        (
            cc
            for cc in custom_commands
            if cc.command == new_command["command"]
            and cc.chat_id == new_command["chat_id"]
        ),
        None,
    ):
        return False

    custom_command_already_in_db = custom_command_repository.get(
        new_command["command"], new_command["chat_id"]
    )

    if not custom_command_already_in_db:
        db_custom_command = custom_command_repository.add(
            custom_command_schema.CustomCommandCreate(**new_command)
        )
        custom_commands.append(db_custom_command)
        return True

    return False


def insert_command(
    chat_id: int,
    message_text: str,
    send_by_user_id: int,
    file_id: str = None,
    media_type: MediaType = MediaType.NONE,
) -> None:
    """Logic and validations to add a new command on database if not exists."""
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

        new_custom_command = new_custom_command.replace("/", "")

        if command != "/addcmd":
            raise Exception("unknow command: " + command)
        elif len(new_custom_command) < 2 or len(new_custom_command) > 15:
            message_service.send_message(
                chat_id,
                "O novo comando deve ter entre 2 e 15 caracteres",
            )
            return
        elif not media_type and (len(answer) < 5 or len(answer) > 1000):
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
        elif next((dc for dc in default_commands if dc == new_custom_command), None):
            message_service.send_message(
                chat_id,
                "Já existe um comando com esse nome",
            )
            return
        elif not string_helper.random_number_validation(answer):
            message_service.send_message(
                chat_id,
                "Verifique a função $random_number. Sintaxe: *$random_number\[min,máx]* (máx. 2 números)",
            )
            return
        elif not string_helper.random_word_validation(answer):
            message_service.send_message(
                chat_id,
                "Verifique a função *$random_word*. Sintaxe: *$random_word*\[word1,word2,...,word10] (máx. 10 palavras)",
            )
            return

    except Exception as ex:
        message_service.send_message(
            chat_id,
            "Para criar um novo comando, utilize:\n*/addcmd <comando> | <resposta> | <descrição>*\nou\n*/addcmd -c <comando> -a <resposta> -d <descrição>*",
        )
        syslog.create_warning("insert_command", ex)
        return

    try:
        if not user_service.validate_user_permission(chat_id, send_by_user_id):
            return

        total_commands = custom_command_repository.count_by_chat_id(chat_id)

        if total_commands >= settings.max_commands:
            message_service.send_message(
                chat_id,
                f"O grupo atingiu o limite de {settings.max_commands} comandos customizados. Remova comandos utilizando */delcmd <comando>*",
            )
            return

        user = user_service.get_user_by_id_if_exists(send_by_user_id)
        now = datetime.now()

        new_custom_command_obj = {
            "command": new_custom_command.lower(),
            "text": answer.strip(),
            "description": description.strip(),
            "chat_id": chat_id,
            "created_by_user_id": user.user_id,
            "created_by_user_name": user.user_name,
            "created_on": now,
            "modified_on": now,
        }

        if file_id and media_type:
            new_custom_command_obj["file_id"] = file_id
            new_custom_command_obj["media_type"] = int(media_type)

        if add_custom_command(new_custom_command_obj):
            message_service.send_message(
                chat_id, f"Novo comando */{new_custom_command}* criado!"
            )
        else:
            message_service.send_message(
                chat_id, f"O comando */{new_custom_command}* já existe"
            )
    except Exception as ex:
        syslog.create_warning("insert_command", ex)
        message_service.send_message(
            chat_id, "Não foi possível cadastrar o novo comando"
        )


def delete_custom_command(command_name: str, chat_id: int) -> bool:
    """Remove a command from database if exists."""
    db_custom_command = next(
        (
            cc
            for cc in custom_commands
            if cc.chat_id == chat_id and cc.command == command_name
        ),
        None,
    )

    if not db_custom_command:
        return False

    if custom_command_repository.get(command_name, chat_id):
        custom_command_repository.delete(command_name, chat_id)
        custom_commands.remove(db_custom_command)
        return True

    return False


def remove_command(chat_id: int, message_text: str, send_by_user_id: int) -> None:
    """Logic and validations to remove a command from database if exists."""
    try:
        command, custom_command_name = message_text.split(" ", 1)

        if command != "/delcmd":
            raise Exception("unknow command: " + command)

        custom_command_name = custom_command_name.replace("/", "")

    except Exception as ex:
        message_service.send_message(
            chat_id,
            "Para remover um comando customizado, utilize */delcmd <comando>*",
        )
        syslog.create_warning("remove_command", ex)
        return

    try:
        if not user_service.validate_user_permission(
            chat_id, send_by_user_id, validate_admin_only=True
        ):
            return

        if delete_custom_command(custom_command_name, chat_id):
            message_service.send_message(
                chat_id, f"Comando */{custom_command_name}* foi removido!"
            )
        else:
            message_service.send_message(
                chat_id,
                f"O comando */{custom_command_name}* não existe",
            )
    except Exception as ex:
        syslog.create_warning("remove_command", ex)
        message_service.send_message(
            chat_id, f"Não foi possível remover o comando */{custom_command_name}*"
        )
