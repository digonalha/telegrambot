from datetime import datetime

from src.helpers.logging_helper import SystemLogging
from src.repositories import sale_tracker_keyword_repository
from src.schemas import sale_tracker_keyword_schema
from src.services import message_service, user_service

sale_tracker_keywords = []
syslog = SystemLogging(__name__)


def get_all_sale_tracker_keyword() -> None:
    """Fill the global variable sale_tracker_keyword with all sale_tracker_keywords found in database."""
    global sale_tracker_keywords
    sale_tracker_keywords = sale_tracker_keyword_repository.get_all()


def add_sale_tracker_keyword(sale_tracker_keyword: dict) -> bool:
    """Create a new sale_tracker_keyword on database if not exists."""
    if len(sale_tracker_keywords) > 0 and next(
        (
            stk
            for stk in sale_tracker_keywords
            if stk.user_id == sale_tracker_keyword["user_id"]
            and stk.keyword == sale_tracker_keyword["keyword"]
        ),
        None,
    ):
        return False

    if not sale_tracker_keyword_repository.get(
        sale_tracker_keyword["user_id"],
        sale_tracker_keyword["chat_id"],
        sale_tracker_keyword["keyword"],
    ):
        db_sale_tracker_keyword = sale_tracker_keyword_repository.add(
            sale_tracker_keyword_schema.SaleTrackerKeywordCreate(**sale_tracker_keyword)
        )

        if db_sale_tracker_keyword:
            sale_tracker_keywords.append(db_sale_tracker_keyword)
            return True

    return False


def insert_sale_tracker_keyword(chat_id: int, message_text: str, send_by_user_id: int):
    """Logic and validations to add a new sale_tracker_keyword on database if not exists."""
    try:
        command, keyword = message_text.split(" ", 1)

        if command != "!track":
            raise Exception("unknow command: " + command)

    except Exception as ex:
        message_service.send_message(
            chat_id,
            "Para monitorar uma palavra-chave nas promoções, utilize *!track palavra-chave*",
        )
        syslog.create_warning("insert_sale_tracker_keyword", ex)
        return

    try:
        if not user_service.validate_user_permission(
            chat_id, send_by_user_id, validate_admin_only=False
        ):
            return

        now = datetime.now()

        send_by_user = user_service.get_user_by_id_if_exists(send_by_user_id)

        if not send_by_user:
            raise Exception("user not found. id: " + send_by_user_id)

        tracker_keyword = {
            "user_id": send_by_user.user_id,
            "user_name": send_by_user.user_name,
            "chat_id": chat_id,
            "keyword": keyword,
            "created_on": now,
            "modified_on": now,
        }

        if add_sale_tracker_keyword(tracker_keyword):
            message_service.send_message(
                chat_id, f'A palavra-chave *"{keyword}"* agora está sendo monitorada'
            )
        else:
            message_service.send_message(
                chat_id, f'A palavra-chave *"{keyword}"* já está sendo monitorada'
            )
    except Exception as ex:
        syslog.create_warning("insert_sale_tracker_keyword", ex)
        message_service.send_message(
            chat_id, f'Não foi possível adicionar a palavra-chave *"{keyword}"*'
        )


def delete_sale_tracker_keyword(user_id: int, chat_id: int, keyword: str) -> bool:
    """Remove a sale_tracker_keyword from database if exists."""
    if len(sale_tracker_keywords) == 0 or not (
        next(
            (
                stk
                for stk in sale_tracker_keywords
                if stk.user_id == user_id
                and stk.chat_id == chat_id
                and stk.keyword == keyword
            ),
            None,
        )
    ):
        return False

    sale_tracker_keyword_db = sale_tracker_keyword_repository.get(
        user_id, chat_id, keyword
    )

    if sale_tracker_keyword_db:
        sale_tracker_keyword_repository.delete(user_id, chat_id, keyword)
        sale_tracker_keywords.remove(sale_tracker_keyword_db)
        return True

    return False


def remove_sale_tracker_keyword(
    chat_id: int, message_text: str, send_by_user_id: int
) -> None:
    """Logic and validations to remove a sale_tracker_keyword from database if exists."""
    try:
        command, keyword = message_text.split(" ", 1)

        if command != "!untrack":
            raise Exception("unknow command: " + command)

    except Exception as ex:
        message_service.send_message(
            chat_id,
            "Para parar de monitorar uma palavra-chave nas promoções, utilize *!untrack palavra-chave*",
        )
        syslog.create_warning("remove_sale_tracker_keyword", ex)
        return

    try:
        if not user_service.validate_user_permission(
            chat_id, send_by_user_id, validate_admin_only=False
        ):
            return

        if delete_sale_tracker_keyword(send_by_user_id, chat_id, keyword):
            message_service.send_message(
                chat_id,
                f'A palavra-chave *"{keyword}"* foi removida da lista de monitoramento',
            )
        else:
            message_service.send_message(
                chat_id, f'A palavra-chave *"{keyword}"* não está sendo monitorada'
            )
    except Exception as ex:
        syslog.create_warning("remove_sale_tracker_keyword", ex)
        message_service.send_message(
            chat_id, f'Não foi possível remover a palavra-chave *"{keyword}"*'
        )
