from datetime import datetime, date, time, timedelta
from sqlalchemy import text
from data.database import database
from domain.schemas.sale_schemas.sale_create import SaleCreate
from domain.models.sale import Sale

local_session = database.get()


def add(sale: SaleCreate):
    new_sale = Sale(**sale.dict())

    local_session.add(new_sale)
    local_session.commit()
    local_session.refresh(new_sale)

    return new_sale


def get_last_day_sales():
    greater_than_date = datetime.combine(date.today(), time()) - timedelta(
        1
    )  # date today - 1 day
    return local_session.query(Sale).filter(Sale.sale_date >= greater_than_date).all()


def get_by_id(id: int):
    return local_session.query(Sale).filter(Sale.sale_id == id).first()


def get_by_aggregator_url(aggregator_url: str):
    return (
        local_session.query(Sale).filter(Sale.aggregator_url == aggregator_url).first()
    )


def get_last_day_sales_by_keyword(
    arr_keyword: str, max_price: int = None, skip: int = 0, take: int = 3
) -> list():
    str_SQL = """SELECT ts.product_name, ts.product_image_url, ts.sale_url, ts.aggregator_url, ts.price, ts.old_price, ts.sale_date
               FROM sale ts 
               WHERE lower(ts.product_name) LIKE ALL (:arr_keyword) 
               AND ts.sale_date >= :greater_than_date 
               ORDER BY ts.sale_date DESC
               LIMIT :take OFFSET :skip"""

    if max_price:
        str_SQL += " AND trunc(ts.price) <= :max_price;"

    greater_than_date = datetime.combine(date.today(), time()) - timedelta(1)

    result = local_session.execute(
        text(str_SQL),
        {
            "arr_keyword": arr_keyword,
            "greater_than_date": greater_than_date,
            "max_price": max_price,
            "skip": skip,
            "take": take,
        },
    )

    if result.rowcount == 0:
        return None

    return result.mappings().all()


def count_last_day_sales_by_keyword(arr_keyword: str, max_price: int = None) -> int:
    str_SQL = """SELECT COUNT(*) 
                 FROM sale ts
                 WHERE lower(ts.product_name) LIKE ALL (:arr_keyword) 
                 AND ts.sale_date >= :greater_than_date"""

    if max_price:
        str_SQL += " AND trunc(ts.price) <= :max_price;"

    greater_than_date = datetime.combine(date.today(), time()) - timedelta(1)

    return local_session.execute(
        text(str_SQL),
        {
            "arr_keyword": arr_keyword,
            "greater_than_date": greater_than_date,
            "max_price": max_price,
        },
    ).scalar()
