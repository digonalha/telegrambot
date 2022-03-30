import json
import math
from domain.services import message_service

from data.repositories import sale_repository
from shared.helpers.logging_helper import SystemLogging
from shared.helpers import string_helper
from domain.schemas.sale_schemas.sale_create import SaleCreate
from domain.models.sale import Sale
from domain.services import keyword_service


sales = []
syslog = SystemLogging(__name__)


def get_last_day_sales() -> None:
    """Fill the global variable sales with last 24h sales found in database."""
    global sales
    sales = sale_repository.get_last_day_sales()


def count_last_day_sales_by_keyword(keyword: str, max_price: float = None) -> list:
    keyword_to_search = ""

    if len(keyword) == 0:
        return

    for k_splitted in keyword.split():
        if len(keyword_to_search) > 0:
            keyword_to_search += ","
        else:
            keyword_to_search += "{"

        keyword_to_search += f'"%{k_splitted}%"'

    keyword_to_search += "}"

    return sale_repository.count_last_day_sales_by_keyword(keyword_to_search, max_price)


def get_last_day_sales_by_keyword(
    keyword: str, max_price: float = None, skip: int = 0, take: int = 3
) -> list:
    keyword_to_search = ""

    if len(keyword) == 0:
        return

    for k_splitted in keyword.split():
        if len(keyword_to_search) > 0:
            keyword_to_search += ","
        else:
            keyword_to_search += "{"

        keyword_to_search += f'"%{k_splitted}%"'

    keyword_to_search += "}"

    return sale_repository.get_last_day_sales_by_keyword(
        keyword_to_search, max_price, skip, take
    )


def create_header_last_sales(total_sales: int, keyword) -> str:
    last_sales_message = f'\n\nEncontrei {total_sales} {"promoções relacionadas" if total_sales > 1 else "promoção relacionada" } à palavra-chave <b>"{keyword}"</b> nas últimas 24 horas:'
    return last_sales_message


def create_footer_last_sales(keyword: str, is_add_keyword: bool = False):
    if is_add_keyword:
        return f"\n\n******\n<i>Para remover essa palavra-chave do monitor e deixar de ser notificado sempre que uma nova promoção aparecer, utilize o comando (clique para copiar):</i>\n\n<code>/delpromo {keyword}</code>"
    else:
        return f"\n\n******\n<i>Para adicionar essa palavra-chave e ser notificado sempre que uma nova promoção aparecer, utilize o comando (clique para copiar):</i>\n\n<code>/addpromo {keyword}</code>"


def check_last_sales(
    user_id: int,
    keyword: dict,
    is_add_keyword: bool = False,
    callback_data: str = None,
    message_id: int = None,
) -> bool:
    try:
        str_keyword = keyword["keyword"]
        str_max_price = keyword["max_price"]
        page = 1

        if callback_data:
            cbk_action, cbk_page, cbk_keyword, cbk_max_price = callback_data.split("|")
            page = int(cbk_page)
            if cbk_action == "preview":
                page = page - 1 if page > 1 else 1
            elif cbk_action == "next":
                page = page + 1
            else:
                return
            str_keyword = cbk_keyword.strip()
            str_max_price = None if cbk_max_price == "None" else cbk_max_price.strip()
            is_add_keyword = keyword_service.get_keyword(user_id, str_keyword) != None

        str_keyword = string_helper.string_sanitize(str_keyword)

        if str_max_price:
            str_max_price = int(str_max_price)

        total_last_day_sales = count_last_day_sales_by_keyword(
            str_keyword, str_max_price
        )

        if total_last_day_sales == 0:
            return False

        take = 3
        skip = 0 if page <= 1 else (page - 1) * take

        total_pages = math.ceil(total_last_day_sales / take)

        last_sales = get_last_day_sales_by_keyword(
            str_keyword, str_max_price, skip, take
        )

        if not last_sales:
            return

        last_sales_message = create_header_last_sales(total_last_day_sales, str_keyword)

        index = 1

        for sale in last_sales:
            last_sales_message += f"\n\n📌\n<b><a href='{sale['aggregator_url']}'>{sale['product_name']}</a></b>\n\n"
            last_sales_message += f"<b>Valor: {string_helper.get_old_new_price_str(sale['price'], sale['old_price'])}</b>\n"
            last_sales_message += (
                f"<b>Data: {sale['sale_date'].strftime('%d/%m - %H:%M')}</b>\n\n"
            )

            last_sales_message += f"\n"

        last_sales_message += create_footer_last_sales(str_keyword, is_add_keyword)

        reply_markup = None

        if total_pages > 1:
            str_page = str(page)
            str_total_page = str(total_pages)

            data_left = f"preview|{str_page}|{str_keyword}|{str_max_price}"
            data_middle = f"refresh|{str_page}|{str_keyword}|{str_max_price}"
            data_right = f"next|{str_page}|{str_keyword}|{str_max_price}"
            reply_markup = (
                '{"inline_keyboard": [[{"text": "'
                + ("← Ant." if page > 1 else "")
                + '", "callback_data": "'
                + data_left
                + '"},'
            )
            reply_markup += (
                '{"text": "Pág. '
                + str_page
                + "/"
                + str_total_page
                + '", "callback_data": "'
                + data_middle
                + '"}'
            )
            reply_markup += (
                ',{"text": "'
                + ("Próx. →" if page < total_pages else "")
                + '", "callback_data": "'
                + data_right
                + '"}]]}'
            )

        if not callback_data:
            message_service.send_message(
                user_id,
                last_sales_message,
                parse_mode="HTML",
                reply_markup=reply_markup,
            )
        else:
            message_service.edit_message(
                user_id,
                last_sales_message,
                message_id,
                parse_mode="HTML",
                reply_markup=reply_markup,
            )
        return True
    except Exception as ex:
        str_keyword_dict = json.dumps(keyword)
        syslog.create_warning("check_last_sales", ex, user_id, str_keyword_dict)


def add_sale_if_not_exists(sale: dict) -> Sale:
    """Create a new sale on database if not exists."""
    try:
        db_sale = None

        if next(
            (u for u in sales if u.sale_id == sale["sale_id"]),
            None,
        ):
            return

        if not sale_repository.get_by_id(sale["sale_id"]):
            db_sale = sale_repository.add(SaleCreate(**sale))

            if db_sale:
                sales.append(db_sale)

        return db_sale
    except Exception as ex:
        syslog.create_warning("add_sale_if_not_exists", ex, 0, "")


def add_sale_if_aggregator_url_not_exists(sale: dict) -> Sale:
    """Create a new sale on database if not exists."""
    try:
        db_sale = None

        if next(
            (u for u in sales if u.aggregator_url == sale["aggregator_url"]),
            None,
        ):
            return

        if not sale_repository.get_by_aggregator_url(sale["aggregator_url"]):
            db_sale = sale_repository.add(SaleCreate(**sale))

            if db_sale:
                sales.append(db_sale)

        return db_sale
    except Exception as ex:
        syslog.create_warning("add_sale_if_not_exists", ex, 0, "")
