from datetime import datetime

from src.helpers.logging_helper import SystemLogging
from src.repositories import keyword_repository
from src.schemas import keyword_schema
from src.services import message_service, user_service

keywords = []
syslog = SystemLogging(__name__)


def get_all_keywords() -> None:
    """Fill the global variable keyword with all keywords found in database."""
    global keywords
    keywords = keyword_repository.get_all()


def get_user_keywords(chat_id: int, user_id: int, message_id: int) -> list:
    try:
        keywords = keyword_repository.get_by_user_id(user_id)

        user = user_service.get_user_by_id_if_exists(user_id)

        if not user:
            raise Exception("user not found. id: " + user_id)

        message = f"Nenhuma palavra-chave encontrada para o usuário *@{user.user_name}*"

        if keywords and len(keywords) > 0:
            message = "As palavras-chave abaixo foram encontradas: \n"
            for stk in keywords:
                message += f"\n• {stk.keyword}"

            message += f"\n\n*Total: {len(keywords)}*"

        message_service.send_message(user_id, message)
    except Exception as ex:
        syslog.create_warning("get_user_keywords", ex)
        message_service.send_message(
            user_id,
            f"Ocorreu um erro ao buscar as palavras-chave",
        )
    finally:
        if chat_id != user_id:
            message_service.delete_message(chat_id, message_id)


def add_keyword(keyword: dict) -> bool:
    """Create a new keyword on database if not exists."""
    if len(keywords) > 0 and next(
        (
            stk
            for stk in keywords
            if stk.user_id == keyword["user_id"] and stk.keyword == keyword["keyword"]
        ),
        None,
    ):
        return False

    if not keyword_repository.get(
        keyword["user_id"],
        keyword["keyword"],
    ):
        db_keyword = keyword_repository.add(keyword_schema.KeywordCreate(**keyword))

        if db_keyword:
            keywords.append(db_keyword)
            return True

    return False


def insert_keyword(
    chat_id: int, message_text: str, send_by_user_id: int, message_id: int
):
    """Logic and validations to add a new keyword on database if not exists."""
    try:
        command, keyword = message_text.split(" ", 1)

        if command != "!addkeyword":
            raise Exception("unknow command: " + command)

    except ValueError as ve:
        command = message_text.split(" ", 1)[0]

        if command == "!addkeyword":
            message_service.send_message(
                send_by_user_id,
                "Para monitorar uma palavra-chave nas promoções, utilize *!addkeyword <palavra-chave>*",
            )
            syslog.create_warning("insert_keyword", ve)

            if chat_id != send_by_user_id:
                message_service.delete_message(chat_id, message_id)
        return
    except Exception as ex:
        message_service.send_message(
            send_by_user_id,
            "Para monitorar uma palavra-chave nas promoções, utilize *!addkeyword <palavra-chave>*",
        )
        syslog.create_warning("insert_keyword", ex)
        return

    try:
        now = datetime.now()

        send_by_user = user_service.get_user_by_id_if_exists(send_by_user_id)

        if not send_by_user:
            raise Exception("user not found. id: " + send_by_user_id)

        user_keywords = keyword_repository.get_by_user_id(send_by_user.user_id)

        if len(user_keywords) >= 10 and not send_by_user.is_admin:
            message = f"Você atingiu o seu limite de 10 palavras-chave. Para remover, utilize *!untrack palavra-chave*"
            message_service.send_message(send_by_user.user_id, message)
            return

        tracker_keyword = {
            "user_id": send_by_user.user_id,
            "user_name": send_by_user.user_name,
            "keyword": keyword,
            "created_on": now,
            "modified_on": now,
        }

        if add_keyword(tracker_keyword):
            message_service.send_message(
                send_by_user.user_id,
                f'A palavra-chave *"{keyword}"* agora está sendo monitorada',
            )
        else:
            message_service.send_message(
                send_by_user.user_id,
                f'A palavra-chave *"{keyword}"* já está sendo monitorada',
            )
    except Exception as ex:
        syslog.create_warning("insert_keyword", ex)
        message_service.send_message(
            send_by_user.user_id,
            f'Não foi possível adicionar a palavra-chave *"{keyword}"*',
        )
    finally:
        if chat_id != send_by_user_id:
            message_service.delete_message(chat_id, message_id)


def delete_keyword(user_id: int, keyword: str) -> bool:
    """Remove a keyword from database if exists."""
    if len(keywords) == 0 or not (
        next(
            (
                stk
                for stk in keywords
                if stk.user_id == user_id and stk.keyword == keyword
            ),
            None,
        )
    ):
        return False

    keyword_db = keyword_repository.get(user_id, keyword)

    if keyword_db:
        keyword_repository.delete(user_id, keyword)
        keywords.remove(keyword_db)
        return True

    return False


def remove_keyword(
    chat_id: int, message_text: str, send_by_user_id: int, message_id: int
) -> None:
    """Logic and validations to remove a keyword from database if exists."""
    try:
        command, keyword = message_text.split(" ", 1)

        if command != "!delkeyword":
            raise Exception("unknow command: " + command)
    except ValueError as ve:
        command = message_text.split(" ", 1)[0]

        if command == "!delkeyword":
            message_service.send_message(
                send_by_user_id,
                "Para remover uma palavra-chave, utilize *!delkeyword <palavra-chave>*",
            )
            syslog.create_warning("remove_keyword", ve)

            if chat_id != send_by_user_id:
                message_service.delete_message(chat_id, message_id)
        return
    except Exception as ex:
        message_service.send_message(
            send_by_user_id,
            "Para remover uma palavra-chave, utilize *!delkeyword <palavra-chave>*",
        )
        syslog.create_warning("remove_keyword", ex)
        return

    try:
        if delete_keyword(send_by_user_id, keyword):
            message_service.send_message(
                send_by_user_id,
                f'A palavra-chave *"{keyword}"* foi removida da lista de monitoramento',
            )
        else:
            message_service.send_message(
                send_by_user_id,
                f'A palavra-chave *"{keyword}"* não está sendo monitorada',
            )
    except Exception as ex:
        syslog.create_warning("remove_keyword", ex)
        message_service.send_message(
            send_by_user_id, f'Não foi possível remover a palavra-chave *"{keyword}"*'
        )
    finally:
        if chat_id != send_by_user_id:
            message_service.delete_message(chat_id, message_id)


def remove_all_keywords(chat_id: int, send_by_user_id: int, message_id: int) -> None:
    """Logic and validations to remove all keywords from database if exists."""
    try:
        keywords = keyword_repository.get_by_user_id(send_by_user_id)

        if len(keywords) == 0:
            message_service.send_message(
                send_by_user_id,
                f"Não existem palavras-chave para serem removidas da lista de monitoramento",
            )
            return

        keyword_repository.delete_all_by_user_id(send_by_user_id)
        keywords = keyword_repository.get_by_user_id(send_by_user_id)

        if len(keywords) == 0:
            message_service.send_message(
                send_by_user_id,
                f"Todas as palavras-chave foram removidas da lista de monitoramento",
            )
        else:
            message_service.send_message(
                send_by_user_id,
                f"Não foi possível remover as palavras-chave da lista de monitoramento",
            )
    except Exception as ex:
        syslog.create_warning("remove_all_keywords", ex)
        message_service.send_message(
            send_by_user_id, f"Não foi possível remover as palavras-chave"
        )
    finally:
        if chat_id != send_by_user_id:
            message_service.delete_message(chat_id, message_id)
