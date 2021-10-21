from datetime import timezone
from src.repositories.models.tracked_sale_model import TrackedSale
from src.helpers.logging_helper import SystemLogging
from src.repositories import tracked_sale_repository
from src.schemas import tracked_sale_schema
from src.services import message_service
from src.helpers import string_helper

tracked_sales = []
syslog = SystemLogging(__name__)


def get_past_day_sales() -> None:
    """Fill the global variable tracked_sales with last 24h tracked_sales found in database."""
    global tracked_sales
    tracked_sales = tracked_sale_repository.get_past_day_sales()


def get_last_day_sales_by_keyword(keyword: dict) -> list():
    keyword_to_search = ""

    str_keyword = keyword["keyword"]

    if len(str_keyword) == 0:
        return

    for k_splitted in str_keyword.split():
        if len(keyword_to_search) > 0:
            keyword_to_search += ","
        else:
            keyword_to_search += "{"

        keyword_to_search += f'"%{k_splitted}%"'

    keyword_to_search += "}"

    return tracked_sale_repository.get_last_day_sales_by_keyword(
        keyword_to_search, keyword["max_price"]
    )


def check_last_tracked_sales(chat_id: int, keyword: dict):
    try:
        last_sales = get_last_day_sales_by_keyword(keyword)

        if not last_sales:
            return

        total_sales = len(last_sales)
        if last_sales and total_sales > 0:
            last_sales_message = "🚨 <b>Alerta Promobot</b> 🚨"
            last_sales_message += f'\n\nEncontrei {total_sales} {"promoções relacionadas" if total_sales > 1 else "promoção relacionada" } à palavra-chave <b>"{keyword["keyword"]}"</b> nas últimas 24 horas:\n'
            last_sales_message += f"______________________\n"
            # send sales from last 8 hours if exists
            for sale in last_sales:
                last_sales_message += f"\n<b>{sale['product_name']}</b>\n\n"
                last_sales_message += f"Valor: {string_helper.get_old_new_price_str(sale['price'], sale['old_price'])}\n"
                last_sales_message += (
                    f"Data: {sale['sale_date'].strftime('%d/%m - %H:%M')}\n\n"
                )
                last_sales_message += f"<b><a href='{sale['aggregator_url']}'>Ir para a promoção</a></b>  🔗\n"
                last_sales_message += f"______________________\n"

            last_sales_message += f'\n\nDaqui pra frente você receberá uma notificação todas as vezes que uma promoção relacionada a essa palavra-chave monitorada aparecer! Para remover essa palavra-chave do monitor, utilize o comando:\n\n<code>/delpromo {keyword["keyword"]}</code>\n\n<i>Clique no comando para copiá-lo</i>'

            message_service.send_message(chat_id, last_sales_message, parse_mode="HTML")
    except Exception as ex:
        syslog.create_warning("check_last_tracked_sales", ex)


def add_tracked_sale_if_not_exists(tracked_sale: dict) -> TrackedSale:
    """Create a new tracked_sale on database if not exists."""
    try:
        db_tracked_sale = None

        if next(
            (u for u in tracked_sales if u.sale_id == tracked_sale["sale_id"]),
            None,
        ):
            return

        if not tracked_sale_repository.get_by_id(tracked_sale["sale_id"]):
            db_tracked_sale = tracked_sale_repository.add(
                tracked_sale_schema.TrackedSaleCreate(**tracked_sale)
            )

            if db_tracked_sale:
                tracked_sales.append(db_tracked_sale)

        return db_tracked_sale
    except Exception as ex:
        syslog.create_warning("add_tracked_sale_if_not_exists", ex)
