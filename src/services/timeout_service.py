from datetime import datetime, timedelta
from services import user_service, message_service
from helpers.logging_helper import SystemLogging
from configs import settings

timeout_users = []
syslog = SystemLogging(__name__)


def is_user_in_timeout(chat_id, user_id) -> bool:
    """Check if user is in timeout chat list"""
    return len(timeout_users) > 0 and next(
        (
            tu
            for tu in timeout_users
            if tu["user_id"] == user_id and tu["chat_id"] == chat_id
        ),
        None,
    )


def insert_timeout_user(chat_id: int, message_text: str, send_by_user_id: int) -> None:
    """Insert user in timeout chat list"""
    try:
        command, parameters = message_text.split()

        if command != "/mute" and command != f"/mute@{settings.bot_name}":
            return

        username, timer = parameters.split("|")

        username = username.replace("@", "")
        timer = int(timer)

        if timer < 30 or timer > 3600:
            message_service.send_message(
                chat_id,
                "Valor em segundos inválido! Utilize valores entre 30 (meio minuto) e 3600 (1h)",
            )
            return

        if not user_service.validate_user_permission(chat_id, send_by_user_id):
            return

        user = user_service.get_user_by_username_if_exists(chat_id, username)

        if not user:
            return
        elif user.is_admin:
            message_service.send_message(
                chat_id, f"*@{username}* é um administrador e não pode ser silenciado"
            )
            return

        if len(timeout_users) > 0 and next(
            tu
            for tu in timeout_users
            if tu["user_id"] == user.user_id and tu["chat_id"] == chat_id
        ):
            message_service.send_message(chat_id, f"*@{username}* já está silenciado!")
        else:
            timeout_until = datetime.now() + timedelta(0, timer)
            timeout_users.append(
                {
                    "user_id": user.user_id,
                    "user_name": user.user_name,
                    "timeout_until": timeout_until,
                    "chat_id": chat_id,
                }
            )
            message_service.send_message(
                chat_id, f"*@{username}* silenciado por {timer} segundos..."
            )
    except ValueError as ve:
        message_service.send_message(
            chat_id,
            "Para silenciar um usuário, utilize `/mute username | tempo_em_segundos`",
        )
    except Exception as ex:
        syslog.create_warning("insert_timeout_user", ex, chat_id, message_text)
        message_service.send_message(chat_id, "Não foi possível silenciar o usuário :(")


def remove_timeout_user(chat_id, message_text: str, send_by_user_id: int) -> None:
    """Remove user from timeout chat list"""
    try:
        command, username = message_text.split()

        if command != "/unmute" and command != f"/unmute@{settings.bot_name}":
            return

        username = username.replace("@", "")

        if not user_service.validate_user_permission(chat_id, send_by_user_id):
            return

        user = user_service.get_user_by_username_if_exists(chat_id, username)

        if not user:
            return

        if len(timeout_users) == 0:
            message_service.send_message(chat_id, f"*@{username}* não está silenciado!")

        timeout_user = next(
            (
                tu
                for tu in timeout_users
                if tu["user_id"] == user.user_id and tu["chat_id"] == chat_id
            ),
            None,
        )

        if not timeout_user:
            message_service.send_message(chat_id, f"*@{username}* não está silenciado!")
        else:
            timeout_users.remove(timeout_user)
            message_service.send_message(
                timeout_user["chat_id"],
                f"*@{(timeout_user['user_name'])}* já pode voltar a falar :)",
            )
    except ValueError as ve:
        message_service.send_message(
            chat_id,
            "Para habilitar a fala de um usuário, utilize `/unmute username`",
        )
    except Exception as ex:
        syslog.create_warning("remove_timeout_user", ex, chat_id, message_text)
        message_service.send_message(
            chat_id, "Não foi possível remover o usuário da lista de silenciados"
        )
