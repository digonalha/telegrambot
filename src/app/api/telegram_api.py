import requests
from ast import literal_eval
from random import randint

from app.configs import settings
from shared.helpers.logging_helper import SystemLogging
from domain.services.keyword_service import remove_all_keywords_by_user_id

syslog = SystemLogging(__name__)

API_URI = f"https://api.telegram.org/bot{settings.api_token}"


def create_log_from_response(function_name, response, chat_id: int = None):
    if response["ok"]:
        syslog.create_info(function_name, f"request has been sucessfully submitted!")
        return True
    if (
        response["error_code"] == 403
        and chat_id
        and "description" in response
        and "blocked by the user" in response["description"]
    ):
        # delete keywords from user
        remove_all_keywords_by_user_id(chat_id)
        return True

    raise Exception(response["description"])


def get_updates(offset: int):
    query_offset = ""
    if offset > 0:
        query_offset = f"?offset={offset}"
    res = requests.get(f"{API_URI}/getUpdates{query_offset}")
    response_json = res.json()
    if create_log_from_response("get_updates", response_json):
        return response_json["result"]
    else:
        return []


def delete_message(chat_id: int, message_id: int):
    res = requests.post(
        f"{API_URI}/deleteMessage",
        {"chat_id": chat_id, "message_id": message_id},
    )

    create_log_from_response("delete_message", res.json(), chat_id)


def send_message(
    chat_id: int,
    message: str,
    reply_id: int = 0,
    parse_mode: str = "markdown",
    reply_markup: str = None,
    disable_web_page_preview: bool = True,
):
    data = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": parse_mode,
        "disable_web_page_preview": disable_web_page_preview,
    }

    if reply_id != None and reply_id > 0:
        data["reply_to_message_id"] = reply_id
    if reply_markup:
        data["reply_markup"] = reply_markup

    requests.post(f"{API_URI}/sendMessage", data=data)


def edit_message(
    chat_id: int,
    message: str,
    message_id: int,
    parse_mode: str = "markdown",
    reply_markup: str = None,
):
    data = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": message,
        "parse_mode": parse_mode,
        "disable_web_page_preview": True,
    }

    if reply_markup:
        data["reply_markup"] = reply_markup

    requests.post(f"{API_URI}/editMessageText", data=data)


def edit_message_reply_markup(
    chat_id: int,
    message_id: int,
    reply_markup: str,
):
    data = {
        "chat_id": chat_id,
        "message_id": message_id,
        "reply_markup": reply_markup,
    }

    requests.post(f"{API_URI}/editMessageReplyMarkup", data=data)


def send_animation(chat_id: int, file_id: str, reply_id: int = 0):
    data = {"chat_id": chat_id, "animation": file_id}
    if reply_id != None and reply_id > 0:
        data["reply_to_message_id"] = reply_id

    requests.post(f"{API_URI}/sendAnimation", data=data)


def send_video(chat_id: int, video_url: str, reply_id: int = 0):
    data = {"chat_id": chat_id, "video": video_url}
    if reply_id != None and reply_id > 0:
        data["reply_to_message_id"] = reply_id

    requests.post(f"{API_URI}/sendVideo", data=data)


def send_audio(chat_id: int, file_id: str, title: str, username: str):
    data = {
        "chat_id": chat_id,
        "audio": file_id,
    }

    requests.post(f"{API_URI}/sendAudio", data=data)


def send_image(
    chat_id: int,
    file_id: str,
    caption: str = None,
    reply_id: int = None,
    reply_markup: str = None,
    parse_mode: str = "markdown",
):
    if file_id.startswith("[") and file_id.endswith("]"):
        arr_photo = literal_eval(file_id)
        random_index = randint(0, len(arr_photo) - 1)
        file_id = arr_photo[random_index]
    data = {"chat_id": chat_id, "photo": file_id, "parse_mode": parse_mode}
    if caption:
        data["caption"] = caption
    if reply_id:
        data["reply_to_message_id"] = reply_id
    if reply_markup:
        data["reply_markup"] = reply_markup

    res = requests.post(f"{API_URI}/sendPhoto", data=data)

    if res.status_code == 400 and caption:
        send_message(
            chat_id=chat_id,
            message=caption,
            reply_id=reply_id,
            reply_markup=reply_markup,
            parse_mode=parse_mode,
            disable_web_page_preview=False,
        )


def answer_callback_query(callback_query_id: str, notification_text: str):
    data = {"callback_query_id": callback_query_id}
    if notification_text and len(notification_text) > 0:
        data["show_alert"] = True
        data["text"] = notification_text
    requests.post(f"{API_URI}/answerCallbackQuery", data=data)
