from data.database import database
from domain.models.moderator import Moderator
from domain.schemas.moderator_schemas.moderator_create import ModeratorCreate


def add(moderator: ModeratorCreate):
    local_session = database.get()
    new_moderator = Moderator(**moderator.dict())

    local_session.add(new_moderator)
    local_session.commit()
    local_session.refresh(new_moderator)

    return new_moderator


def delete(user_id: int, chat_id: int):
    local_session = database.get()
    local_session.query(Moderator).filter(
        Moderator.user_id == user_id, Moderator.chat_id == chat_id
    ).delete()

    local_session.commit()


def get_all():
    return database.get().query(Moderator).all()


def get(user_id: int, chat_id: int):
    return (
        database.get()
        .query(Moderator)
        .filter(Moderator.user_id == user_id, Moderator.chat_id == chat_id)
        .first()
    )
