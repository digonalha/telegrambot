from datetime import datetime

from shared.helpers.logging_helper import SystemLogging
from domain.schemas.tracking_code_schemas.tracking_code_create import (
    TrackingCodeCreate,
)
from domain.services import message_service
from data.repositories import tracking_code_repository

syslog = SystemLogging(__name__)


def insert_tracking_code(user_id: int, message_text: str):
    """Logic and validations to add a new tracking code on database if not exists."""
    try:
        command, tracking_code = message_text.split(" ", 1)

        if command != "/addrastreio":
            return

        if add_tracking_code(user_id, tracking_code):
            message_service.send_message(
                user_id, f"Código de rastreio *{tracking_code}* adicionado"
            )
        else:
            message_service.send_message(
                user_id, f"Código de rastreio *{tracking_code}* já cadastrado"
            )
    except ValueError as ve:
        message_service.send_message(
            user_id,
            "Para tornar um usuário moderador, utilize `/mod username`",
        )
    except Exception as ex:
        syslog.create_warning("insert_tracking_code", ex, user_id, message_text)
        message_service.send_message(
            user_id, "Não foi possível cadastrar o código de rastreio"
        )


def add_tracking_code(user_id: int, code: str) -> bool:
    """Create a new tracking code on database if not exists."""

    if not tracking_code_repository.get(user_id, code):
        db_tracking_code = tracking_code_repository.add(
            TrackingCodeCreate(
                user_id=user_id,
                tracking_code=code,
                is_active=True,
                created_on=datetime.now(),
            )
        )

        if db_tracking_code:
            return True

    return False


def delete_tracking_code(user_id: int, code: str) -> bool:
    """Remove a tracking code from database if exists."""

    tracking_code_db = tracking_code_repository.get(user_id, code)

    if tracking_code_db:
        tracking_code_repository.delete(user_id, code)
        return True

    return False


def remove_tracking_code(chat_id: int, message_text: str) -> None:
    """Logic and validations to remove a tracking code from database if exists."""
    try:
        command, code = message_text.split(" ", 1)

        if command != "/delrastreio":
            return

        if delete_tracking_code(chat_id, code):
            message_service.send_message(
                chat_id, f"O código de rastreio *{code}* foi removido!"
            )
        else:
            message_service.send_message(
                chat_id,
                f"O código de rastreio *{code}* não existe",
            )
    except ValueError as ve:
        message_service.send_message(
            chat_id,
            "Para remover um código de rastreio, utilize `/delrastreio código`",
        )
    except Exception as ex:
        syslog.create_warning("remove_tracking_code", ex, chat_id, message_text)
        message_service.send_message(
            chat_id, f"Não foi possível remover o código de rastreio *{code}*"
        )
