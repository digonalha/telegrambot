from repositories.database import database
from repositories.models.user_model import User
from schemas import user_schema

local_session = database.get()


def add(user: user_schema.UserCreate) -> User:
    new_user = User(**user.dict())

    local_session.add(new_user)
    local_session.commit()
    local_session.refresh(new_user)

    return new_user


def get_by_id(user_id: int) -> User:
    return local_session.query(User).filter(User.user_id == user_id).first()


def get_all() -> None:
    return local_session.query(User).all()


def update(user: user_schema.UserUpdate) -> User:
    db_user = local_session.query(User).filter(User.user_id == user.user_id).first()

    if not db_user:
        return None

    db_user.first_name = user.first_name
    db_user.user_name = user.user_name
    db_user.modified_on = user.modified_on

    local_session.commit()
    return db_user
