from datetime import datetime
from helpers.logging_helper import SystemLogging
from repositories import keyword_repository
from repositories.models.keyword_model import Keyword
from schemas import keyword_schema
from services import message_service, user_service, sale_service
from configs import settings
from helpers import string_helper
import json

keywords = []
syslog = SystemLogging(__name__)


def get_keyword(user_id: int, keyword: str) -> Keyword:
    return keyword_repository.get(user_id, keyword)


def get_all_keywords() -> None:
    """Fill the global variable keyword with all keywords found in database."""
    global keywords
    keywords = keyword_repository.get_all()


def get_user_keywords(user_id: int) -> list:
    try:
        keywords = keyword_repository.get_by_user_id(user_id)

        user = user_service.get_user_by_id_if_exists(user_id)

        if not user:
            raise Exception("user not found. id: " + user_id)

        message = f"Nenhuma palavra-chave encontrada. Você pode adicionar palavras-chave utilizando: \n\n`/addpromo palavra-chave | valor-máx`\n\n_parâmetro valor-máx opcional_"

        if keywords and len(keywords) > 0:
            message = f"<b>Promobot</b>\n\nAqui está uma lista com suas palavras-chave monitoradas. Fique atento pois palavras-chave sem valor máximo serão sempre notificadas, independente do valor da promoção.\n\n"
            message += "<u><b>[Valor máx] Palavra-chave</b></u>\n"

            str_max_keywords = f"/{settings.max_keywords}" if not user.is_admin else ""

            message += f"<b>Total: {len(keywords)}{str_max_keywords}</b>\n"

            for stk in keywords:
                message += f"\n<b>📌</b>{'' if not stk.max_price else ' [R$' + string_helper.format_decimal(stk.max_price) + ']'} <code>{stk.keyword}</code>"

            message += f"\n\n<i>Clique na palavra-chave para copiá-la</i>\n\n<i>/addpromo  /delpromo  /clearpromo</i>"

            message_service.send_message(user_id, message, parse_mode="HTML")
        else:
            message_service.send_message(user_id, message)
    except Exception as ex:
        syslog.create_warning("get_user_keywords", ex, user_id, "")
        message_service.send_message(
            user_id,
            f"Ocorreu um erro ao buscar as palavras-chave",
        )


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


def insert_keyword(user_id: int, message_text: str):
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
                    user_id,
                    "Valor inserido para preço máximo inválido.\n\n*Valor mín: 10 - Valor máx: 9999*\n\n_Não utilize separador para milhares_\n_Não utilize separador para decimais_",
                )
                return

        except ValueError as ve:
            keyword = parameters

        if command != "/addpromo":
            return
        elif len(keyword) < 4:
            message_service.send_message(
                user_id,
                "Palavra-chave não pode ter menos de 4 caracteres",
            )
            return
        elif len(keyword) > 40:
            message_service.send_message(
                user_id,
                "Palavra-chave não pode ter mais de 40 caracteres",
            )
            return

        send_by_user = user_service.get_user_by_id_if_exists(user_id)

        if not send_by_user:
            raise Exception("user not found. id: " + user_id)

        user_keywords = keyword_repository.get_by_user_id(send_by_user.user_id)

        if len(user_keywords) >= settings.max_keywords and not send_by_user.is_admin:
            message = f"Você atingiu o seu limite de {settings.max_keywords} palavras-chave. Remova palavras-chave utilizando: \n\n`/delpromo palavra-chave`"
            message_service.send_message(send_by_user.user_id, message)
            return

        date_now = datetime.now()
        keyword = keyword.lower().strip()

        new_keyword = {
            "user_id": send_by_user.user_id,
            "keyword": keyword,
            "max_price": max_price,
            "created_on": date_now,
            "modified_on": date_now,
        }

        if add_keyword(new_keyword):
            message_service.send_message(
                send_by_user.user_id,
                f'A palavra-chave *"{keyword}"* agora está sendo monitorada.\n\n_Envie /promo para ver sua lista de palavras-chave_',
            )

            sale_service.check_last_sales(
                send_by_user.user_id, new_keyword, is_add_keyword=True
            )
        else:
            db_keyword = get_keyword(new_keyword["user_id"], new_keyword["keyword"])

            if db_keyword.max_price != new_keyword["max_price"]:
                updated_keyword = update_keyword(new_keyword)

                if updated_keyword:
                    if new_keyword["max_price"] and new_keyword["max_price"] > 0:
                        message_service.send_message(
                            send_by_user.user_id,
                            f'O valor máximo da palavra-chave *"{keyword}"* foi alterado para R${new_keyword["max_price"]}',
                        )
                    else:
                        message_service.send_message(
                            send_by_user.user_id,
                            f'O valor máximo da palavra-chave *"{keyword}"* foi removido. Todas as promoções da palavra-chave serão notificadas',
                        )

                else:
                    raise Exception("Cant update keyword")
            else:
                message_service.send_message(
                    send_by_user.user_id,
                    f'A palavra-chave *"{keyword}"* já está sendo monitorada',
                )
    except ValueError as ve:
        message_service.send_message(
            user_id,
            "Para monitorar uma palavra-chave nas promoções, utilize: \n\n`/addpromo palavra-chave | valor-máx`\n\n_parâmetro valor-máx opcional_",
        )
    except Exception as ex:
        syslog.create_warning("insert_keyword", user_id, message_text)
        message_service.send_message(
            send_by_user.user_id,
            f'Não foi possível adicionar a palavra-chave *"{keyword}"*',
        )


def update_keyword(keyword: dict) -> bool:
    updated_keyword = keyword_repository.update(
        keyword_schema.KeywordUpdate(
            user_id=keyword["user_id"],
            keyword=keyword["keyword"],
            max_price=keyword["max_price"],
            modified_on=datetime.now(),
        )
    )

    if updated_keyword:
        try:
            keywords.remove(updated_keyword)
            keywords.append(updated_keyword)

            return True
        except:
            get_all_keywords()

    return False


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


def remove_keyword(user_id: int, message_text: str) -> None:
    """Logic and validations to remove a keyword from database if exists."""
    try:
        command, keyword = message_text.split(" ", 1)

        if command != "/delpromo":
            return

        keyword = keyword.lower().strip()

        if delete_keyword(user_id, keyword):
            message_service.send_message(
                user_id,
                f'A palavra-chave *"{keyword}"* foi removida da lista de monitoramento.\n\n_Envie /promo para ver sua lista de palavras-chave_',
            )
        else:
            message_service.send_message(
                user_id,
                f'A palavra-chave *"{keyword}"* não está sendo monitorada',
            )
    except ValueError as ve:
        message_service.send_message(
            user_id,
            "Para remover uma palavra-chave, utilize: \n\n`/delpromo palavra-chave`",
        )
        return
    except Exception as ex:
        syslog.create_warning("remove_keyword", ex, user_id, message_text)
        message_service.send_message(
            user_id, f'Não foi possível remover a palavra-chave *"{keyword}"*'
        )


def remove_all_keywords_by_user_id(user_id: int) -> bool:
    keyword_repository.delete_all_by_user_id(user_id)
    keywords = keyword_repository.get_by_user_id(user_id)

    all_removed = not keywords or len(keywords) == 0

    if all_removed:
        get_all_keywords()

    return all_removed


def remove_all_keywords(user_id: int, message_text: str) -> None:
    """Logic and validations to remove all keywords from database if exists."""
    try:
        command, confirmation = message_text.split(" ", 1)

        if command != "/clearpromo":
            return
        if confirmation != "yes-baby":
            message_service.send_message(
                user_id,
                "Para remover todas as palavras-chave, utilize:\n\n`/clearpromo yes-baby`\n\n_Clique no comando para copiá-lo_",
            )
            return

        keywords = keyword_repository.get_by_user_id(user_id)

        if len(keywords) == 0:
            message_service.send_message(
                user_id,
                f"Não existem palavras-chave para serem removidas da lista de monitoramento",
            )
            return

        all_removed = remove_all_keywords_by_user_id(user_id)

        if all_removed:
            message_service.send_message(
                user_id,
                f"Todas as palavras-chave foram removidas da lista de monitoramento",
            )
        else:
            message_service.send_message(
                user_id,
                f"Não foi possível remover as palavras-chave da lista de monitoramento",
            )
    except ValueError as ve:
        message_service.send_message(
            user_id,
            "Para remover todas as palavras-chave, utilize:\n\n`/clearpromo yes-baby`\n\n_Clique no comando para copiá-lo_",
        )
    except Exception as ex:
        syslog.create_warning("remove_all_keywords", ex, user_id, message_text)
        message_service.send_message(
            user_id, f"Não foi possível remover as palavras-chave"
        )


def get_last_sales_by_keyword(user_id: int, message_text: str):
    """Logic and validations to search last sales in database if not exists."""
    try:
        command, keyword = message_text.split(" ", 1)

        if command != "/lastpromo":
            return
        elif len(keyword) < 4:
            message_service.send_message(
                user_id,
                "Palavra-chave não pode ter menos de 4 caracteres",
            )
            return
        elif len(keyword) > 40:
            message_service.send_message(
                user_id,
                "Palavra-chave não pode ter mais de 40 caracteres",
            )
            return

        keyword = keyword.lower().strip()
        keyword_to_search = {
            "keyword": keyword.lower(),
            "max_price": None,
        }

        any_sale_found = sale_service.check_last_sales(user_id, keyword_to_search)

        if not (any_sale_found):
            message_service.send_message(
                user_id,
                f'Não foi possível encontrar promoções utilizando a palavra-chave *"{keyword}"*',
            )
    except ValueError as ve:
        message_service.send_message(
            user_id,
            "Para verificar as últimas promoções por palavra-chave, utilize: \n\n`/lastpromo palavra-chave`",
        )
    except Exception as ex:
        syslog.create_warning("get_last_sales_by_keyword", ex, user_id, message_text)
        message_service.send_message(
            user_id,
            f'Ocorreu um erro ao buscar promoções que contenham a palavra-chave *"{keyword}"*',
        )


def delete_by_callback(
    user_id: int, keywords_string: str, message_id: str, inline_keyboard
) -> None:
    try:
        arr_keywords = keywords_string.split(";")

        for kw in arr_keywords:
            delete_keyword(user_id, kw)        

        ikb_str = (
            '{ "inline_keyboard": [['
            + json.dumps(inline_keyboard[0][0])
            + "],["
            + json.dumps(inline_keyboard[1][0])
            + "]]}"
        )

        message_service.edit_reply_markup(user_id, message_id, ikb_str)
    except Exception as ex:
        syslog.create_warning("delete_by_callback", ex, user_id)
    finally:
        get_all_keywords()
