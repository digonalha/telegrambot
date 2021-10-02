from datetime import datetime
from src.helpers.logging_helper import SystemLogging
from src.repositories import user_repository
from src.schemas import user_schema
from src.services import moderator_service, message_service

users = []
syslog = SystemLogging(__name__)


def validate_user_permission(
    chat_id: int, user_id: int, validate_admin_only: bool = False
) -> bool:
    user_send = next((u for u in users if u["user_id"] == user_id), None)

    if user_send == None and validate_admin_only == True:
        return False
    elif (user_send == None or not user_send["is_admin"]) and next(
        (
            m
            for m in moderator_service.moderators
            if m["chat_id"] == chat_id and m["user_id"] == user_id
        ),
        None,
    ) == None:
        message_service.send_message(
            chat_id, "Você não tem permissão para utilizar esse comando"
        )
        return False

    return True


def validate_username_exists(chat_id: int, username: int):
    if username.startswith("@"):
        username = username.split("@")[1]

    user = next((u for u in users if u["user_name"] == username), None)

    if user == None:
        message_service.send_message(
            chat_id,
            f"Eu ainda não conheço *{username}* :(",
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
                    "user_id": user.user_id,
                    "user_name": user.user_name,
                    "is_admin": user.is_admin,
                }
            )
    except:
        return users


def add_user_if_not_exists(user_id: int, username: str):
    try:
        for user in users:
            if user["user_id"] == user_id:
                return

        if not user_repository.get_by_id(user_id):
            now = datetime.now()

            create_schema = user_schema.UserCreate(
                user_id=user_id,
                user_name=username,
                is_admin=False,
                created_on=now,
                modified_on=now,
            )

            db_user = user_repository.add(create_schema)

            if db_user:
                users.append(
                    {
                        "user_id": db_user.user_id,
                        "user_name": db_user.user_name,
                        "is_admin": db_user.is_admin,
                    }
                )
    except Exception as ex:
        syslog.create_warning("add_user_if_not_exists", ex)
