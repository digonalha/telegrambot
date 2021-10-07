from src.repositories.database import database
from src.repositories.models.user_model import User
from src.schemas import user_schema

local_session = database.get()


def add(user: user_schema.UserCreate):
    new_user = User(**user.dict())

    local_session.add(new_user)
    local_session.commit()
    local_session.refresh(new_user)

    return new_user


def get_by_id(user_id: int):
    return local_session.query(User).filter(User.user_id == user_id).first()


def get_all():
    return local_session.query(User).all()
