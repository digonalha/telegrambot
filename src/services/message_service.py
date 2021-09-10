from datetime import datetime
from src.api import telegram_api
from src.services import user_service
from src.helpers.logging_helper import SystemLogging

syslog = SystemLogging(__name__)


def send_help_message(chat_id: int, reply_user: int, message_id: int):
    user = user_service.get_user(reply_user)

    help_message = (
        f"Olá, *{(user['username'])}*!\n"
        "Aqui está a minha lista de comandos disponiveis:\n\n"
        "*!help:* lista de comandos disponíveis\n"
        "*!mod username:* adiciona o usuário na lista de moderadores ×\n"
        "*!unmod username:* remove o usuário da lista de moderadores ×\n"
        "*!mute username tempo_em_segundos:* adiciona o usuário na lista de silenciados pelo tempo especificado ××\n"
        "*!unmute username:* remove o usuário da lista de silenciados ××\n\n\n"
        "× _necessário ser um administrador_\n"
        "×× _necessário ser um administrador ou moderador_"
    )

    telegram_api.send_message(chat_id, help_message, message_id)


def send_message(chat_id: int, message: str):
    telegram_api.send_message(chat_id, message)


def get_updates(offset: int):
    try:
        return telegram_api.get_updates(offset)
    except:
        return []


def get_last_update_id(updates):
    total_updates = 0
    try:
        total_updates = len(updates)
    except:
        return 0
    return 0 if total_updates == 0 else updates[total_updates - 1]["update_id"]


def delete_messages(updates, timeout_users):
    if (len(timeout_users)) == 0:
        return
    for user_timeout in timeout_users:
        for update in updates:
            try:
                message = update["message"]
                if (
                    message["from"]["id"] == user_timeout["user_id"]
                    and message["chat"]["id"] == user_timeout["chat_id"]
                ):
                    telegram_api.delete_message(
                        message["chat"]["id"], message["message_id"]
                    )
            except:
                continue

        if user_timeout["timeout_until"] <= datetime.now():
            timeout_users.remove(user_timeout)
            send_message(
                user_timeout["chat_id"],
                f"*{(user_timeout['username'])}* já pode voltar a falar :)",
            )
            continue
