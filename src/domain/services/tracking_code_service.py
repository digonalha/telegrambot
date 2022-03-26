from datetime import datetime

from app.configs import settings
from shared.helpers.logging_helper import SystemLogging
from domain.schemas.tracking_code_schemas.tracking_code_create import (
    TrackingCodeCreate,
)
from domain.services import message_service, user_service
from data.repositories import tracking_code_repository

syslog = SystemLogging(__name__)


def insert_tracking_code(user_id: int, message_text: str):
    """Logic and validations to add a new tracking code on database if not exists."""
    try:
        command, parameters = message_text.split(" ", 1)

        try:
            code, name = parameters.split("|", 1)
            code = code.strip()
            name = name.strip()
        except ValueError as ve:
            code = parameters

        if command != "/addrastreio":
            return

        if add_tracking_code(user_id, code, name):
            message_service.send_message(
                user_id, f"Código de rastreio *{code}* adicionado"
            )
        else:
            message_service.send_message(
                user_id, f"Código de rastreio *{code}* já cadastrado"
            )
    except ValueError as ve:
        message_service.send_message(
            user_id,
            "Para adicionar um código de rastreio, utilize `/addrastreio código-rastreio | nome`",
        )
    except Exception as ex:
        syslog.create_warning("insert_tracking_code", ex, user_id, message_text)
        message_service.send_message(
            user_id, "Não foi possível cadastrar o código de rastreio"
        )


def add_tracking_code(user_id: int, code: str, name: str = None) -> bool:
    """Create a new tracking code on database if not exists."""

    if not tracking_code_repository.get(user_id, code):
        db_tracking_code = tracking_code_repository.add(
            TrackingCodeCreate(
                user_id=user_id,
                tracking_code=code,
                name=name,
                is_active=True,
                created_on=datetime.now(),
            )
        )

        if db_tracking_code:
            return True

    return False


def get_all_active() -> list:
    """Get  all ative tracking codes commands found in database."""
    return tracking_code_repository.get_all_active()


def get_by_user_id(user_id: int) -> list:
    """Get  all ative tracking codes commands found in database."""
    return tracking_code_repository.get_by_user_id(user_id)


def get_user_trackings(user_id: int) -> list:
    try:
        tracking_codes = get_by_user_id(user_id)

        user = user_service.get_user_by_id_if_exists(user_id)

        if not user:
            raise Exception("user not found. id: " + user_id)

        message = f"Nenhum código de rastreio encontrado. Você pode adicionar códigos de rastreio utilizando: \n\n`/addrastreio código-rastreio | nome`\n\n_parâmetro nome opcional_"

        if tracking_codes and len(tracking_codes) > 0:
            message = (
                f"Aqui está uma lista com seus códigos de rastreio monitorados.\n\n"
            )
            message += "<u><b>[Nome] Código de Rastreio</b></u>\n"

            str_max_keywords = f"/{settings.max_keywords}" if not user.is_admin else ""

            message += f"<b>Total: {len(tracking_codes)}{str_max_keywords}</b>\n"

            for tc in tracking_codes:
                message += f"\n<b>•</b>  {'' if not tc.name else ' [' + tc.name + ']'} <code>{tc.tracking_code}</code>"

            message += f"\n\n<i>Clique no código de rastreio para copiá-lo</i>\n\n<i>/addrastreio  /delrastreio</i>"

            message_service.send_message(user_id, message, parse_mode="HTML")
        else:
            message_service.send_message(user_id, message)
    except Exception as ex:
        syslog.create_warning("get_user_trackings", ex, user_id, "")
        message_service.send_message(
            user_id,
            f"Ocorreu um erro ao buscar os códigos de rastreio",
        )


def delete_tracking_code(user_id: int, code: str) -> bool:
    """Remove a tracking code from database if exists."""

    tracking_code_db = tracking_code_repository.get(user_id, code)

    if tracking_code_db:
        tracking_code_repository.delete(user_id, code)
        return True

    return False


def delete_tracking_code_by_id(tracking_code_id: int) -> bool:
    """Remove a tracking code from database if exists."""

    tracking_code_db = tracking_code_repository.get_by_id(tracking_code_id)

    if tracking_code_db:
        tracking_code_repository.delete(tracking_code_id)
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
