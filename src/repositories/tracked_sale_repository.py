from src.schemas import tracked_sale_schema
from src.repositories.database import database
from src.repositories.models.tracked_sale_model import TrackedSale
from datetime import datetime, date, time, timedelta
from sqlalchemy import text

local_session = database.get()


def add(tracked_sale: tracked_sale_schema.TrackedSaleCreate):
    new_tracked_sale = TrackedSale(**tracked_sale.dict())

    local_session.add(new_tracked_sale)
    local_session.commit()
    local_session.refresh(new_tracked_sale)

    return new_tracked_sale


def get_past_day_sales():
    greater_than_date = datetime.combine(date.today(), time()) - timedelta(
        1
    )  # date today - 1 day
    return (
        local_session.query(TrackedSale)
        .filter(TrackedSale.sale_date >= greater_than_date)
        .all()
    )


def get_by_id(id: int):
    return local_session.query(TrackedSale).filter(TrackedSale.sale_id == id).first()


def get_last_day_sales_by_keyword(arr_keyword: str, max_price: int = None) -> list():
    greater_than_date = datetime.combine(date.today(), time()) - timedelta(1)

    str_SQL = """SELECT ts.product_name, ts.product_image_url, ts.sale_url, ts.aggregator_url, ts.price, ts.old_price, ts.sale_date
               FROM tracked_sale ts 
               WHERE lower(ts.product_name) LIKE ALL (:arr_keyword) 
               AND ts.sale_date >= :greater_than_date"""

    if max_price:
        str_SQL += " AND trunc(ts.price) <= :max_price;"

    result = local_session.execute(
        text(str_SQL),
        {
            "arr_keyword": arr_keyword,
            "greater_than_date": greater_than_date,
            "max_price": max_price,
        },
    )

    if result.rowcount == 0:
        return None

    return result.mappings().all()
