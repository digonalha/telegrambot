from datetime import datetime
from src.api import telegram_api
from src.helpers.logging_helper import SystemLogging
from random import randint

syslog = SystemLogging(__name__)


def send_audio(chat_id: int, file_id: str, file_name: str, username: str) -> None:
    """Send a request for send audio to telegram api"""
    telegram_api.send_audio(chat_id, file_id, file_name, username)


def send_image(
    chat_id: int,
    file_id: str,
    message: str,
    reply_markup: str = None,
    parse_mode: str = "markdown",
) -> None:
    """Send a request for send a image to telegram api"""
    telegram_api.send_image(
        chat_id, file_id, message, reply_markup=reply_markup, parse_mode=parse_mode
    )


def send_animation(chat_id: int, file_id: str) -> None:
    """Send a request for send animation to telegram api"""
    telegram_api.send_animation(chat_id, file_id)


def send_video(chat_id: int, file_id: str) -> None:
    """Send a request for send video to telegram api"""
    telegram_api.send_video(chat_id, file_id)


def send_message(
    chat_id: int,
    message: str,
    parse_mode: str = "markdown",
    reply_id: int = 0,
    reply_markup: str = None,
) -> None:
    """Send a request for send message to telegram api"""
    if "$random_number[" in message:
        str_numbers = message.split("$random_number[")[1].split("]", 1)[0]
        first_number, second_number = str_numbers.split(",")

        first_number = int(first_number)
        second_number = int(second_number)

        if first_number < 0 or first_number > 1000:
            return
        elif second_number < 0 or second_number > 1000:
            return

        perc = randint(first_number, second_number)
        string_to_replace = f"$random_number[{str_numbers}]"

        message = message.replace(string_to_replace, str(perc))
    if "$random_word[" in message:
        str_words = message.split("$random_word[")[1].split("]", 1)[0]
        words = str_words.split(",")

        total_words = len(words)

        if total_words < 2 or total_words > 10:
            return

        rand_index = randint(0, total_words - 1)

        selected_word = words[rand_index]

        string_to_replace = f"$random_word[{str_words}]"

        message = message.replace(string_to_replace, selected_word)

    telegram_api.send_message(
        chat_id,
        message,
        reply_id=reply_id,
        parse_mode=parse_mode,
        reply_markup=reply_markup,
    )


def edit_message(
    chat_id: int,
    message: str,
    message_id: int,
    parse_mode: str = "markdown",
    reply_markup: str = None,
) -> None:
    """Send a request for edit message to telegram api"""
    telegram_api.edit_message(
        chat_id,
        message,
        message_id,
        parse_mode=parse_mode,
        reply_markup=reply_markup,
    )


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
