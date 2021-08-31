from datetime import datetime
from src.helpers.logging_helper import SystemLogging
from src.repositories import user_repository
from src.schemas import user_schema
from src.services import moderator_service, message_service

users = []

syslog = SystemLogging(__name__)


def validate_user_command(chat_id: int, send_by_user_id: int, username_on_command: str):
    username = username_on_command

    if username.startswith("@"):
        username = username.split("@")[1]

    user_send = next((u for u in users if u["user_id"] == send_by_user_id), None)

    if (user_send == None or not user_send["is_admin"]) and next(
        (
            m
            for m in moderator_service.moderators
            if m["chat_id"] == chat_id and m["user_id"] == send_by_user_id
        ),
        None,
    ) == None:
        message_service.send_message(
            chat_id, "Você não tem permissão para utilizar esse comando"
        )
        return False

    user = next((u for u in users if u["username"] == username), None)

    if user == None:
        message_service.send_message(
            chat_id,
            f"eu ainda não conheço *{username}* :(",
        )
        return False

    return user


def get_user(user_id: int):
    return next(
        (u for u in users if u["user_id"] == user_id),
        None,
    )


def get_all():
    global users
    try:
        users_db = user_repository.get_all()
        users = []
        for user in users_db:
            users.append(
                {
                    "user_id": user.telegram_user_id,
                    "username": user.telegram_username,
                    "is_admin": user.is_admin,
                }
            )
    except:
        return users


def add_user(user_id, user_name):
    db_user = None

    user_already_in_db = user_repository.get_by_id(user_id)

    if not user_already_in_db:
        created_date = datetime.now()

        create_schema = user_schema.UserCreate(
            telegram_user_id=user_id,
            telegram_username=user_name,
            is_admin=False,
            created_on=created_date,
            modified_on=created_date,
        )
        db_user = user_repository.add(create_schema)

    return db_user


def add_if_user_not_exists(user_id, user_name):
    result = False

    for user in users:
        if user["user_id"] == user_id:
            return

    db_user = add_user(user_id, user_name)
    if db_user != None:
        users.append(
            {
                "user_id": db_user.telegram_user_id,
                "username": db_user.telegram_username,
                "is_admin": db_user.is_admin,
            }
        )
    return result
