from data.database import database
from domain.models.user import User
from domain.schemas.user_schemas.user_create import UserCreate
from domain.schemas.user_schemas.user_update import UserUpdate


def add(user: UserCreate) -> User:
    new_user = User(**user.dict())
    local_session = database.get()

    local_session.add(new_user)
    local_session.commit()
    local_session.refresh(new_user)

    return new_user


def get_by_id(user_id: int) -> User:
    return database.get().query(User).filter(User.user_id == user_id).first()


def get_all() -> None:
    return database.get().query(User).all()


def update(user: UserUpdate) -> User:
    local_session = database.get()

    db_user = local_session.query(User).filter(User.user_id == user.user_id).first()

    if not db_user:
        return None

    db_user.first_name = user.first_name
    db_user.user_name = user.user_name
    db_user.modified_on = user.modified_on

    local_session.commit()
    return db_user
