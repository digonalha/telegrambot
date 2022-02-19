from sqlalchemy import func
from schemas import keyword_schema
from database import database
from models.keyword import Keyword

local_session = database.get()


def add(keyword: keyword_schema.KeywordCreate):
    new_keyword = Keyword(**keyword.dict())

    local_session.add(new_keyword)
    local_session.commit()
    local_session.refresh(new_keyword)

    return new_keyword


def update(keyword: keyword_schema.KeywordUpdate) -> Keyword:
    db_keyword = (
        local_session.query(Keyword)
        .filter(
            Keyword.user_id == keyword.user_id,
            func.lower(Keyword.keyword) == keyword.keyword.lower(),
        )
        .first()
    )

    if not db_keyword:
        return None

    db_keyword.max_price = keyword.max_price
    db_keyword.modified_on = keyword.modified_on

    local_session.commit()
    return db_keyword


def delete(user_id: int, keyword: str):
    local_session.query(Keyword).filter(
        Keyword.user_id == user_id,
        func.lower(Keyword.keyword) == keyword.lower(),
    ).delete(synchronize_session="fetch")

    local_session.commit()


def delete_all_by_user_id(user_id: int):
    local_session.query(Keyword).filter(Keyword.user_id == user_id).delete()
    local_session.commit()


def get_all():
    return local_session.query(Keyword).all()


def get(user_id: int, keyword: str):
    return (
        local_session.query(Keyword)
        .filter(
            Keyword.user_id == user_id,
            func.lower(Keyword.keyword) == keyword.lower(),
        )
        .first()
    )


def get_by_user_id(user_id: int):
    return (
        local_session.query(Keyword)
        .filter(Keyword.user_id == user_id)
        .order_by(Keyword.keyword)
        .all()
    )
