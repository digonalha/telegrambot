from datetime import datetime
from src.api import telegram_api
from src.helpers.logging_helper import SystemLogging
from random import randint

syslog = SystemLogging(__name__)


def send_audio(chat_id: int, file_id: str, file_name: str, username: str) -> None:
    """Send a request for send audio to telegram api"""
    telegram_api.send_audio(chat_id, file_id, file_name, username)


def send_image(chat_id: int, file_id: str, message: str) -> None:
    """Send a request for send a image to telegram api"""
    telegram_api.send_image(chat_id, file_id, message)


def send_animation(chat_id: int, file_id: str) -> None:
    """Send a request for send animation to telegram api"""
    telegram_api.send_animation(chat_id, file_id)


def send_video(chat_id: int, file_id: str) -> None:
    """Send a request for send video to telegram api"""
    telegram_api.send_video(chat_id, file_id)


def send_message(chat_id: int, message: str) -> None:
    """Send a request for send message to telegram api"""
    if "$random_percent" in message:
        perc = randint(0, 100)
        message = message.replace("$random_percent", str(perc))

    telegram_api.send_message(chat_id, message)


def get_updates(offset: int) -> list:
    """List last message updates from chats"""
    return telegram_api.get_updates(offset)


def get_update_id_offset(updates) -> int:
    """Return last update_id from chat message updates"""
    total_updates = len(updates)
    return 0 if total_updates == 0 else updates[total_updates - 1]["update_id"] + 1


def delete_messages(updates, timeout_users) -> None:
    """Remove chat messages posted by muted users if exists."""
    if (len(timeout_users)) == 0:
        return

    for user_timeout in timeout_users:
        if user_timeout["timeout_until"] <= datetime.now():
            timeout_users.remove(user_timeout)
            send_message(
                user_timeout["chat_id"],
                f"*@{(user_timeout['user_name'])}* já pode voltar a falar :)",
            )
            continue

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


def delete_message(chat_id: int, message_id: int) -> None:
    telegram_api.delete_message(chat_id, message_id)
