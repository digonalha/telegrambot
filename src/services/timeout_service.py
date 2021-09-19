from datetime import datetime, timedelta
from src.services import user_service, message_service
from src.helpers.logging_helper import SystemLogging

timeout_users = []
syslog = SystemLogging(__name__)


def is_user_in_timeout(chat_id, user_id):
    if len(timeout_users) == 0:
        return False

    return next(
        (
            tu
            for tu in timeout_users
            if tu["user_id"] == user_id and tu["chat_id"] == chat_id
        ),
        None,
    )


def insert_timeout_user(chat_id: int, message_text: str, send_by_user_id: int):
    try:
        command, username, timer = message_text.split()

        if command != "!mute":
            raise Exception("unknow command: " + command)
    except Exception as ex:
        message_service.send_message(
            chat_id, "Para silenciar um usuário, utilize *!mute <username> <30~3600>*"
        )
        syslog.create_warning("insert_timeout_user", ex)
        return

    try:
        timer = int(timer)
        if timer < 30 or timer > 3600:
            message_service.send_message(
                chat_id,
                "Valor em segundos inválido! Utilize valores entre 30 (½ min) e 3600 (1h)",
            )
            return

        if not user_service.validate_user_permission(chat_id, send_by_user_id):
            return

        user = user_service.validate_username_exists(chat_id, username)

        if not user:
            return
        elif user["is_admin"]:
            message_service.send_message(
                chat_id, f"*{username}* é um administrador e não pode ser silenciado"
            )
            return

        if len(timeout_users) > 0 and next(
            tu
            for tu in timeout_users
            if tu["user_id"] == user["user_id"] and tu["chat_id"] == chat_id
        ):
            message_service.send_message(chat_id, f"*{username}* já está silenciado!")
        else:
            timeout_until = datetime.now() + timedelta(0, timer)
            timeout_users.append(
                {
                    "user_id": user["user_id"],
                    "username": user["username"],
                    "timeout_until": timeout_until,
                    "chat_id": chat_id,
                }
            )
            message_service.send_message(
                chat_id, f"*{username}* silenciado por {timer} segundos..."
            )
    except Exception as ex:
        syslog.create_warning("insert_timeout_user", ex)
        message_service.send_message(chat_id, "Não foi possível silenciar o usuário :(")


def remove_timeout_user(chat_id, message_text: str, send_by_user_id: int):
    try:
        command, username = message_text.split()

        if command != "!unmute":
            raise Exception("unknow command: " + command)
    except Exception as ex:
        message_service.send_message(
            chat_id,
            "Para habilitar a fala de um usuário, utilize *!unmute <username>*",
        )
        syslog.create_warning("remove_timeout_user", ex)
        return

    try:
        if not user_service.validate_user_permission(chat_id, send_by_user_id):
            return

        user = user_service.validate_username_exists(chat_id, username)

        if not user:
            return

        if len(timeout_users) == 0:
            message_service.send_message(chat_id, f"*{username}* não está silenciado!")

        silenced_user = next(
            (
                tu
                for tu in timeout_users
                if tu["user_id"] == user["user_id"] and tu["chat_id"] == chat_id
            ),
            None,
        )

        if not silenced_user:
            message_service.send_message(chat_id, f"*{username}* não está silenciado!")
        else:
            timeout_users.remove(silenced_user)
            message_service.send_message(
                silenced_user["chat_id"],
                f"*{(silenced_user['username'])}* já pode voltar a falar :)",
            )
    except Exception as ex:
        syslog.create_warning("remove_timeout_user", ex)
        message_service.send_message(
            chat_id, "Não foi possível remover o usuário da lista de silenciados :("
        )
