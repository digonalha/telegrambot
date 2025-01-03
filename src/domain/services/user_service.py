from datetime import datetime
from domain.services import message_service

from data.repositories import user_repository
from shared.helpers.logging_helper import SystemLogging
from domain.models.user import User
from domain.schemas.user_schemas.user_create import UserCreate
from domain.schemas.user_schemas.user_update import UserUpdate
from domain.services import moderator_service

syslog = SystemLogging(__name__)


def validate_user_permission(
    chat_id: int, user_id: int, validate_admin_only: bool = False
) -> bool:
    """Validate if user is admin or moderator."""
    user_send = user_repository.get_by_id(user_id)

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


def get_user_by_id_if_exists(user_id: int) -> User:
    """Get user by username if exists on global users variable."""
    user = user_repository.get_by_id(user_id)

    if user == None:
        return False

    return user


def get_user_by_username_if_exists(chat_id: int, username: int) -> User:
    """Get user by username if exists on global users variable."""
    if username.startswith("@"):
        username = username.split("@")[1]

    user = user_repository.get_by_username(username)

    if user == None:
        message_service.send_message(
            chat_id,
            f"Eu ainda não conheço o usuário *{username}* :(",
        )
        return False

    return user


def add_or_update_user(user_id: int, first_name: str, user_name: str) -> None:
    """Create a new user on database if not exists, or update if necessary."""
    try:
        db_user = user_repository.get_by_id(user_id)

        if not db_user:
            now = datetime.now()

            db_user = user_repository.add(
                UserCreate(
                    user_id=user_id,
                    user_name=user_name,
                    first_name=first_name,
                    is_admin=False,
                    created_on=now,
                    modified_on=now,
                )
            )

            if db_user:
                return True
        elif db_user.user_name != user_name or db_user.first_name != first_name:

            updated_user = user_repository.update(
                UserUpdate(
                    user_id=user_id,
                    user_name=user_name,
                    first_name=first_name,
                    modified_on=datetime.now(),
                )
            )

            if updated_user:
                return True

        return False

    except Exception as ex:
        user_info = f"first_name: {first_name}| username: {user_name}"
        syslog.create_warning("add_user_if_not_exists", ex, user_id, user_info)
        raise
