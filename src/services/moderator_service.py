from datetime import datetime
from src.helpers.logging_helper import SystemLogging
from src.repositories import moderator_repository
from src.schemas import moderator_schema
from src.services import user_service, message_service

moderators = []
syslog = SystemLogging(__name__)


def get_all():
    global moderators
    try:
        mods = moderator_repository.get_all()
        moderators = []

        for mod in mods:
            moderators.append(
                {
                    "user_id": mod.telegram_user_id,
                    "chat_id": mod.chat_id,
                }
            )
    except:
        return moderators


def add_moderator(user_id: int, chat_id: int):
    if len(moderators) > 0 and next(
        (m for m in moderators if m["user_id"] == user_id and m["chat_id"] == chat_id),
        None,
    ):
        return False

    if not moderator_repository.get(user_id, chat_id):
        db_moderator = moderator_repository.add(
            moderator_schema.ModeratorCreate(
                telegram_user_id=user_id,
                chat_id=chat_id,
                created_on=datetime.now(),
            )
        )

        if db_moderator:
            moderators.append(
                {
                    "user_id": db_moderator.telegram_user_id,
                    "chat_id": db_moderator.chat_id,
                }
            )
            return True

    return False


def insert_moderator(chat_id: int, message_text: str, send_by_user_id: int):
    try:
        command, username = message_text.split()

        if command != "!mod":
            raise Exception("unknow command: " + command)

        username = username.replace("@", "")
    except Exception as ex:
        message_service.send_message(
            chat_id,
            "Para tornar um usuário moderador, utilize *!mod <username>*",
        )
        syslog.create_warning("insert_moderator", ex)
        return

    message = "Não foi possível cadastrar o novo moderador :("

    try:
        if not user_service.validate_user_permission(chat_id, send_by_user_id):
            return

        user = user_service.validate_username_exists(chat_id, username)

        if not user:
            return

        if add_moderator(user["user_id"], chat_id):
            message = f"*@{username}* agora é um moderador"
        else:
            message = f"*@{username}* já é um moderador"
    except Exception as ex:
        syslog.create_warning("insert_moderator", ex)
    finally:
        message_service.send_message(chat_id, message)


def delete_moderator(user_id: int, chat_id: int):
    if len(moderators) == 0 or not (
        next(
            (
                m
                for m in moderators
                if m["user_id"] == user_id and m["chat_id"] == chat_id
            ),
            None,
        )
    ):
        return False

    if moderator_repository.get(user_id, chat_id):
        moderator_repository.delete(user_id, chat_id)
        get_all()
        return True

    return False


def remove_moderator(chat_id: int, message_text: str, send_by_user_id: int):
    try:
        command, username = message_text.split()

        if command != "!unmod":
            raise Exception("unknow command: " + command)

        username = username.replace("@", "")
    except Exception as ex:
        message_service.send_message(
            chat_id,
            "Para remover o status de moderador de um usuário, utilize *!unmod <username>*",
        )
        syslog.create_warning("remove_moderator", ex)
        return

    message = "Não foi possível remover o moderador :("

    try:
        if not user_service.validate_user_permission(chat_id, send_by_user_id):
            return

        user = user_service.validate_username_exists(chat_id, username)

        if not user:
            return

        if delete_moderator(user["user_id"], chat_id):
            message = f"*@{username}* não é mais um moderador"
        else:
            message = f"*@{username}* não é um moderador"
    except Exception as ex:
        syslog.create_warning("remove_moderator", ex)
    finally:
        message_service.send_message(chat_id, message)
