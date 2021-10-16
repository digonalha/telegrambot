from datetime import datetime
from src.repositories.models.user_model import User
from src.helpers.logging_helper import SystemLogging
from src.repositories import user_repository
from src.schemas import user_schema
from src.services import moderator_service, message_service

users = []
syslog = SystemLogging(__name__)


def validate_user_permission(
    chat_id: int, user_id: int, validate_admin_only: bool = False
) -> bool:
    """Validate if user is admin or moderator."""
    user_send = next((u for u in users if u.user_id == user_id), None)

    if not user_send and validate_admin_only == True:
        return False
    elif (not user_send or not user_send.is_admin) and not next(
        (
            m
            for m in moderator_service.moderators
            if m.chat_id == chat_id and m.user_id == user_id
        ),
        None,
    ):
        message_service.send_message(
            chat_id, "Você não tem permissão para utilizar esse comando"
        )
        return False

    return True


def get_user_by_username_if_exists(chat_id: int, username: int) -> User:
    """Get user by username if exists on global users variable."""
    if username.startswith("@"):
        username = username.split("@")[1]

    user = next((u for u in users if u.user_name == username), None)

    if user == None:
        message_service.send_message(
            chat_id,
            f"Eu ainda não conheço o usuário *{username}* :(",
        )
        return False

    return user


def get_user_by_id_if_exists(user_id: int) -> User:
    """Get user by user_id from  global variable users if exists."""
    return next(
        (u for u in users if u.user_id == user_id),
        None,
    )


def get_all_users() -> None:
    """Fill the global variable users with all users found in database."""
    global users
    users = user_repository.get_all()


def add_or_update_user(user_id: int, first_name: str, user_name: str) -> None:
    """Create a new user on database if not exists, or update if necessary."""
    try:
        if next(
            (
                u
                for u in users
                if u.user_id == user_id
                and u.first_name == first_name
                and u.user_name == user_name
            ),
            None,
        ):
            return

        db_user = user_repository.get_by_id(user_id)

        if not db_user:
            now = datetime.now()

            db_user = user_repository.add(
                user_schema.UserCreate(
                    user_id=user_id,
                    user_name=user_name,
                    first_name=first_name,
                    is_admin=False,
                    created_on=now,
                    modified_on=now,
                )
            )

            if db_user:
                users.append(db_user)
        elif db_user.user_name != user_name or db_user.first_name != first_name:
            now = datetime.now()

            updated_user = user_repository.update(
                user_schema.UserUpdate(
                    user_id=user_id,
                    user_name=user_name,
                    first_name=first_name,
                    modified_on=now,
                )
            )

            if updated_user:
                try:
                    users.remove(db_user)
                    users.append(updated_user)
                except:
                    get_all_users()

    except Exception as ex:
        syslog.create_warning("add_user_if_not_exists", ex)
