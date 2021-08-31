from src.repositories.database import database
from src.repositories.models import user_model
from src.schemas import user_schema

local_session = database.get()


def add(user: user_schema.UserCreate):
    new_user = user_model.User(**user.dict())

    local_session.add(new_user)
    local_session.commit()
    local_session.refresh(new_user)

    return new_user


def get_by_id(user_id: int):
    return (
        local_session.query(user_model.User)
        .filter(user_model.User.telegram_user_id == user_id)
        .first()
    )


def get_all():
    return local_session.query(user_model.User).all()
