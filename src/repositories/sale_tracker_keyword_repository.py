from src.schemas import sale_tracker_keyword_schema
from src.repositories.database import database
from src.repositories.models.sale_tracker_keyword_model import SaleTrackerKeyword

local_session = database.get()


def add(sale_tracker_keyword: sale_tracker_keyword_schema.SaleTrackerKeywordCreate):
    new_sale_tracker_keyword = SaleTrackerKeyword(**sale_tracker_keyword.dict())

    local_session.add(new_sale_tracker_keyword)
    local_session.commit()
    local_session.refresh(new_sale_tracker_keyword)

    return new_sale_tracker_keyword


def delete(user_id: int, chat_id: int, keyword: str):
    local_session.query(SaleTrackerKeyword).filter(
        SaleTrackerKeyword.user_id == user_id,
        SaleTrackerKeyword.chat_id == chat_id,
        SaleTrackerKeyword.keyword == keyword,
    ).delete()

    local_session.commit()


def get_all():
    return local_session.query(SaleTrackerKeyword).all()


def get(user_id: int, chat_id: int, keyword: str):
    return (
        local_session.query(SaleTrackerKeyword)
        .filter(
            SaleTrackerKeyword.user_id == user_id,
            SaleTrackerKeyword.chat_id == chat_id,
            SaleTrackerKeyword.keyword == keyword,
        )
        .first()
    )
