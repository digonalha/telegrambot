from src.repositories.models.tracked_sale_model import TrackedSale
from src.helpers.logging_helper import SystemLogging
from src.repositories import tracked_sale_repository
from src.schemas import tracked_sale_schema
from src.services import message_service

tracked_sales = []
syslog = SystemLogging(__name__)


def get_all_tracked_sales() -> None:
    """Fill the global variable tracked_sales with all tracked_sales found in database."""
    global tracked_sales
    tracked_sales = tracked_sale_repository.get_all()


def get_last_tracked_sales(keyword: str) -> list():
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

    return tracked_sale_repository.get_last_tracked_sales(keyword_to_search)


def check_last_tracked_sales(chat_id: int, keyword: str):
    try:
        last_sales = get_last_tracked_sales(keyword)
        total_sales = len(last_sales)
        if last_sales and total_sales > 0:
            last_sales_message = f'Encontrei essas {total_sales} promoções relacionadas a palavra-chave *"{keyword}"* nas ultimas 8 horas:\n\n'
            index = 1
            # send sales from last 8 hours if exists
            for sale in last_sales:
                last_sales_message += f"*{sale['product_name']}*\n"
                last_sales_message += f"Valor: {sale['price']}\n\n"
                last_sales_message += f"[Link promoção]({sale['sale_url']}) - [Link Gatry]({sale['aggregator_url']})\n\n"
                if index < total_sales:
                    last_sales_message += f"--------\n\n"

                index += 1

            message_service.send_message(chat_id, last_sales_message)
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
