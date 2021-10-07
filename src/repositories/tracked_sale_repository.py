from src.schemas import tracked_sale_schema
from src.repositories.database import database
from src.repositories.models.tracked_sale_model import TrackedSale
from datetime import datetime, date, time, timedelta

local_session = database.get()


def add(tracked_sale: tracked_sale_schema.TrackedSaleCreate):
    new_tracked_sale = TrackedSale(**tracked_sale.dict())

    local_session.add(new_tracked_sale)
    local_session.commit()
    local_session.refresh(new_tracked_sale)

    return new_tracked_sale


def get_all():
    greater_than_date = datetime.combine(date.today(), time()) - timedelta(
        1
    )  # date today - 1h:30
    return (
        local_session.query(TrackedSale)
        .filter(TrackedSale.sale_date >= greater_than_date)
        .all()
    )


def get_by_id(id: int):
    return local_session.query(TrackedSale).filter(TrackedSale.sale_id == id).first()
