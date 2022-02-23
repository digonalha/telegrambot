from datetime import datetime

from app.configs import settings
from domain.services import message_service
from data.repositories import moderator_repository
from shared.helpers.logging_helper import SystemLogging
from domain.schemas.moderator_schemas.moderator_create import ModeratorCreate
from domain.services import user_service

moderators = []
syslog = SystemLogging(__name__)


def get_all_moderators() -> None:
    """Fill the global variable moderators with all moderators found in database."""
    global moderators
    moderators = moderator_repository.get_all()


def add_moderator(user_id: int, chat_id: int) -> bool:
    """Create a new moderator on database if not exists."""
    if len(moderators) > 0 and next(
        (m for m in moderators if m.user_id == user_id and m.chat_id == chat_id),
        None,
    ):
        return False

    if not moderator_repository.get(user_id, chat_id):
        db_moderator = moderator_repository.add(
            ModeratorCreate(
                user_id=user_id,
                chat_id=chat_id,
                created_on=datetime.now(),
            )
        )

        if db_moderator:
            moderators.append(db_moderator)
            return True

    return False


def insert_moderator(chat_id: int, message_text: str, send_by_user_id: int):
    """Logic and validations to add a new moderator on database if not exists."""
    try:
        command, username = message_text.split(" ", 1)

        if command != "/mod" and command != f"/mod@{settings.bot_name}":
            return

        username = username.replace("@", "")

        if not user_service.validate_user_permission(
            chat_id, send_by_user_id, validate_admin_only=True
        ):
            return

        user = user_service.get_user_by_username_if_exists(chat_id, username)

        if not user:
            return

        if add_moderator(user.user_id, chat_id):
            message_service.send_message(chat_id, f"*@{username}* agora é um moderador")
        else:
            message_service.send_message(chat_id, f"*@{username}* já é um moderador")
    except ValueError as ve:
        message_service.send_message(
            chat_id,
            "Para tornar um usuário moderador, utilize `/mod username`",
        )
    except Exception as ex:
        syslog.create_warning("insert_moderator", ex, send_by_user_id, message_text)
        message_service.send_message(
            chat_id, "Não foi possível cadastrar o novo moderador"
        )


def delete_moderator(user_id: int, chat_id: int) -> bool:
    """Remove a moderator from database if exists."""
    if len(moderators) == 0 or not (
        next(
            (m for m in moderators if m.user_id == user_id and m.chat_id == chat_id),
            None,
        )
    ):
        return False

    user_mod = moderator_repository.get(user_id, chat_id)

    if user_mod:
        moderator_repository.delete(user_id, chat_id)
        moderators.remove(user_mod)
        return True

    return False


def remove_moderator(chat_id: int, message_text: str, send_by_user_id: int) -> None:
    """Logic and validations to remove a moderator from database if exists."""
    try:
        command, username = message_text.split(" ", 1)

        if command != "/unmod" and command != f"/unmod@{settings.bot_name}":
            return

        username = username.replace("@", "")

        if not user_service.validate_user_permission(
            chat_id, send_by_user_id, validate_admin_only=True
        ):
            return

        user_to_unmod = user_service.get_user_by_username_if_exists(chat_id, username)

        if not user_to_unmod:
            return

        if delete_moderator(user_to_unmod.user_id, chat_id):
            message_service.send_message(
                chat_id, f"*@{username}* não é mais um moderador"
            )
        else:
            message_service.send_message(chat_id, f"*@{username}* não é um moderador")
    except ValueError as ve:
        message_service.send_message(
            chat_id,
            "Para remover o status de moderador de um usuário, utilize `/unmod username`",
        )
    except Exception as ex:
        syslog.create_warning("remove_moderator", ex, send_by_user_id, message_text)
        message_service.send_message(chat_id, "Não foi possível remover o moderador")
