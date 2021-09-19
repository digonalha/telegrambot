from src.schemas import moderator_schema
from src.repositories.database import database
from src.repositories.models import moderator_model

local_session = database.get()


def add(moderator: moderator_schema.ModeratorCreate):
    new_moderator = moderator_model.Moderator(**moderator.dict())

    local_session.add(new_moderator)
    local_session.commit()
    local_session.refresh(new_moderator)

    return new_moderator


def delete(user_id: int, chat_id: int):
    local_session.query(moderator_model.Moderator).filter(
        moderator_model.Moderator.telegram_user_id == user_id,
        moderator_model.Moderator.chat_id == chat_id,
    ).delete()

    local_session.commit()


def get_all():
    return local_session.query(moderator_model.Moderator).all()


def get(user_id: int, chat_id: int):
    return (
        local_session.query(moderator_model.Moderator)
        .filter(
            moderator_model.Moderator.telegram_user_id == user_id,
            moderator_model.Moderator.chat_id == chat_id,
        )
        .first()
    )
