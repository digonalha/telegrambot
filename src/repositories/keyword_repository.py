from sqlalchemy import func
from src.schemas import keyword_schema
from src.repositories.database import database
from src.repositories.models.keyword_model import Keyword

local_session = database.get()


def add(keyword: keyword_schema.KeywordCreate):
    new_keyword = Keyword(**keyword.dict())

    local_session.add(new_keyword)
    local_session.commit()
    local_session.refresh(new_keyword)

    return new_keyword


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
