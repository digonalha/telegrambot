import prettytable as pt
from textwrap import fill
from datetime import datetime
from src.helpers.logging_helper import SystemLogging
from src.repositories import keyword_repository
from src.schemas import keyword_schema
from src.services import message_service, user_service, tracked_sale_service
from src.configs import settings
from src.helpers import string_helper

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

        message = f"Nenhuma palavra-chave encontrada. Você pode adicionar palavras-chave utilizando: \n\n*/addpromo <palavra-chave> | <valor-máx>*\n\n_parâmetro valor-máx opcional_"

        if keywords and len(keywords) > 0:
            width = 0 if not user.table_width else user.table_width
            message = f"<b>Promobot 🤖</b>\n\nAqui está uma lista com suas palavras-chave monitoradas. Palavras-chave sem preço máximo serão sempre notificadas, independente do valor da promoção.\n\n"
            table = None
            plain_str = ""
            if width >= 10:
                table = pt.PrettyTable(["Palavra-chave", "R$"])
                table.align["Palavra-chave"] = "l"
                table.align["R$"] = "r"

                for stk in keywords:
                    table.add_row(
                        [
                            fill(
                                stk.keyword,
                                width=width,
                            ),
                            f"{'--' if not stk.max_price else string_helper.format_decimal(stk.max_price)}",
                        ]
                    )
            else:
                message += "<b>Palavra-chave * Valor máx. (R$)</b>\n"
                for stk in keywords:
                    plain_str += f"\n• <code>{stk.keyword}</code>{'' if not stk.max_price else ' * ' + string_helper.format_decimal(stk.max_price)}"
                plain_str += "\n"

            str_max_keywords = f"/{settings.max_keywords}" if not user.is_admin else ""

            message += f"{table if table else plain_str}\n<code>Total: {len(keywords)}{str_max_keywords}</code>\n\n<i>/addpromo  /delpromo  /clearpromo</i>"

            message_service.send_message(user_id, message, parse_mode="HTML")
        else:
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
        max_price = None
        keyword = None
        command, parameters = message_text.split(" ", 1)

        try:
            keyword, max_price = parameters.split("|")

            keyword = keyword.strip()
            try:
                max_price = int(max_price.strip())

                if max_price < 10 or max_price > 9999:
                    raise
            except:
                message_service.send_message(
                    send_by_user_id,
                    "Valor inserido para preço máximo inválido.\n\n*Valor mín: 10 - Valor máx: 9999*\n\n_Não utilize separador para milhares_\n_Não utilize separador para decimais_",
                )
                return

        except ValueError as ve:
            keyword = parameters

        if command != "/addpromo":
            raise Exception("unknow command: " + command)
        elif len(keyword) < 4:
            message_service.send_message(
                send_by_user_id,
                "Palavra-chave não pode ter menos de 4 caracteres",
            )
            return
        elif len(keyword) > 40:
            message_service.send_message(
                send_by_user_id,
                "Palavra-chave não pode ter mais de 40 caracteres",
            )
            return

    except ValueError as ve:
        command = message_text.split(" ", 1)[0]

        if command == "/addpromo":
            message_service.send_message(
                send_by_user_id,
                "Para monitorar uma palavra-chave nas promoções, utilize: \n\n*/addpromo <palavra-chave> | <valor-máx>*\n\n_parâmetro valor-máx opcional_",
            )
            syslog.create_warning("insert_keyword", ve)

            if chat_id != send_by_user_id:
                message_service.delete_message(chat_id, message_id)
        return
    except Exception as ex:
        message_service.send_message(
            send_by_user_id,
            "Para monitorar uma palavra-chave nas promoções, utilize: \n\n*/addpromo <palavra-chave> | <valor-máx>*\n\n_parâmetro valor-máx opcional_",
        )
        syslog.create_warning("insert_keyword", ex)
        return

    try:
        send_by_user = user_service.get_user_by_id_if_exists(send_by_user_id)

        if not send_by_user:
            raise Exception("user not found. id: " + send_by_user_id)

        user_keywords = keyword_repository.get_by_user_id(send_by_user.user_id)

        if len(user_keywords) >= settings.max_keywords and not send_by_user.is_admin:
            message = f"Você atingiu o seu limite de {settings.max_keywords} palavras-chave. Remova palavras-chave utilizando: \n\n*/delpromo <palavra-chave>*"
            message_service.send_message(send_by_user.user_id, message)
            return

        new_keyword = {
            "user_id": send_by_user.user_id,
            "keyword": keyword.lower(),
            "max_price": max_price,
            "created_on": datetime.now(),
        }

        if add_keyword(new_keyword):
            message_service.send_message(
                send_by_user.user_id,
                f'A palavra-chave *"{keyword}"* agora está sendo monitorada.\n\n_Envie /promo para ver sua lista palavras-chave_',
            )

            tracked_sale_service.check_last_tracked_sales(
                send_by_user.user_id, new_keyword
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
                if stk.user_id == user_id and stk.keyword.lower() == keyword.lower()
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

        if command != "/delpromo":
            raise Exception("unknow command: " + command)
    except ValueError as ve:
        command = message_text.split(" ", 1)[0]

        if command == "/delpromo":
            message_service.send_message(
                send_by_user_id,
                "Para remover uma palavra-chave, utilize: \n\n*/delpromo <palavra-chave>*",
            )
            syslog.create_warning("remove_keyword", ve)

            if chat_id != send_by_user_id:
                message_service.delete_message(chat_id, message_id)
        return
    except Exception as ex:
        message_service.send_message(
            send_by_user_id,
            "Para remover uma palavra-chave, utilize: \n\n*/delpromo <palavra-chave>*",
        )
        syslog.create_warning("remove_keyword", ex)
        return

    try:
        if delete_keyword(send_by_user_id, keyword):
            message_service.send_message(
                send_by_user_id,
                f'A palavra-chave *"{keyword}"* foi removida da lista de monitoramento.\n\n_Envie /promo para ver sua lista palavras-chave_',
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


def remove_all_keywords(
    chat_id: int, message_text: str, send_by_user_id: int, message_id: int
) -> None:
    """Logic and validations to remove all keywords from database if exists."""
    try:
        command, confirmation = message_text.split(" ", 1)

        if command != "/clearpromo":
            raise Exception("unknow command: " + command)
        if confirmation != "yes-baby":
            raise Exception("unknow command: " + command)
    except ValueError as ve:
        command = message_text.split(" ", 1)[0]

        if command == "/clearpromo":
            message_service.send_message(
                send_by_user_id,
                "Para remover todas as palavras-chave, utilize: \n\n*/clearpromo yes-baby*",
            )
            syslog.create_warning("remove_all_keywords", ve)

            if chat_id != send_by_user_id:
                message_service.delete_message(chat_id, message_id)
        return
    except Exception as ex:
        message_service.send_message(
            send_by_user_id,
            "Para remover todas as palavras-chave, utilize: \n\n*/clearpromo yes-baby*",
        )
        syslog.create_warning("remove_all_keywords", ex)
        return
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
