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
    db_moderator = None

    moderator_already_in_db = moderator_repository.get(user_id, chat_id)

    if not moderator_already_in_db:
        db_moderator = moderator_repository.add(
            moderator_schema.ModeratorCreate(
                telegram_user_id=user_id,
                chat_id=chat_id,
                created_on=datetime.now(),
            )
        )

    return db_moderator


def add_moderator_if_not_exists(user_id, chat_id):
    result = False

    if len(moderators) > 0 and next(
        (m for m in moderators if m["user_id"] == user_id and m["chat_id"] == chat_id),
        None,
    ):
        return True

    db_moderator = add_moderator(user_id, chat_id)

    if db_moderator != None:
        moderators.append(
            {
                "user_id": db_moderator.telegram_user_id,
                "chat_id": db_moderator.chat_id,
            }
        )

    return result


def delete_moderator(user_id: int, chat_id: int):
    moderator_exists_in_db = moderator_repository.get(user_id, chat_id)

    if moderator_exists_in_db:
        moderator_repository.delete(user_id, chat_id)
        get_all()
        return True

    return False


def delete_moderator_if_exists(user_id, chat_id):
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

    return delete_moderator(user_id, chat_id)


def insert_moderator(chat_id, message_text: str, send_by_user_id: int):
    try:
        command, username = message_text.split()

        if command != "!mod":
            raise Exception("unknow command: " + command)
    except Exception as ex:
        message_service.send_message(
            chat_id,
            "Para tornar um usuário moderador, utilize *!mod username*",
        )
        syslog.create_warning("insert_moderator", ex)
        return

    user = user_service.validate_user_command(chat_id, send_by_user_id, username)

    if not user:
        return

    if not add_moderator_if_not_exists(user["user_id"], chat_id):
        message_service.send_message(chat_id, f"*{username}* agora é um moderador")
    else:
        message_service.send_message(chat_id, f"*{username}* já é um moderador")


def remove_moderator(chat_id, message_text: str, send_by_user_id: int):
    try:
        command, username = message_text.split()

        if command != "!unmod":
            raise Exception("unknow command: " + command)
    except Exception as ex:
        message_service.send_message(
            chat_id,
            "Para remover o status de moderador de um usuário, utilize *!unmod username*",
        )
        syslog.create_warning("remove_moderator", ex)
        return

    user = user_service.validate_user_command(chat_id, send_by_user_id, username)

    if not user:
        return

    if delete_moderator_if_exists(user["user_id"], chat_id):
        message_service.send_message(chat_id, f"*{username}* não é mais um moderador")
    else:
        message_service.send_message(chat_id, f"*{username}* não é um moderador")
