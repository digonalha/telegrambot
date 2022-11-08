import requests
from ast import literal_eval
from random import randint

from app.configs import settings
from shared.helpers.logging_helper import SystemLogging
from domain.services.keyword_service import remove_all_keywords_by_user_id
from shared.helpers.string_helper import escape_markdown_string

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
        # delete all keywords from user
        remove_all_keywords_by_user_id(chat_id)
        return True

    raise Exception(response["description"])


def get_updates(offset: int):
    try:
        query_offset = ""

        if offset > 0:
            query_offset = f"?offset={offset}"

        res = requests.get(f"{API_URI}/getUpdates{query_offset}", timeout=(60, 60))
        response_json = res.json()

        if create_log_from_response("get_updates", response_json):
            return response_json["result"]

    except Exception as ex:
        syslog.create_warning(get_updates.__name__, ex)

    return []


def delete_message(chat_id: int, message_id: int):
    try:
        res = requests.post(
            f"{API_URI}/deleteMessage",
            {"chat_id": chat_id, "message_id": message_id},
            timeout=(10, 10),
        )

        create_log_from_response("delete_message", res.json(), chat_id)

    except Exception as ex:
        syslog.create_warning(delete_message.__name__, ex)


def send_message(
    chat_id: int,
    message: str,
    reply_id: int = 0,
    parse_mode: str = None,
    reply_markup: str = None,
    disable_web_page_preview: bool = True,
):
    try:
        data = {
            "chat_id": chat_id,
            "text": message,
            "disable_web_page_preview": disable_web_page_preview,
        }

        if reply_id != None and reply_id > 0:
            data["reply_to_message_id"] = reply_id
        if reply_markup:
            data["reply_markup"] = reply_markup
        if parse_mode:
            data["parse_mode"] = parse_mode

        res = requests.post(f"{API_URI}/sendMessage", data=data)

        if res.status_code == 400 and "byte offset" in res.text:
            data["text"] = escape_markdown_string(data["text"])
            res = requests.post(f"{API_URI}/sendMessage", data=data, timeout=(60, 60))

    except Exception as ex:
        syslog.create_warning(send_message.__name__, ex)


def edit_message(
    chat_id: int,
    message: str,
    message_id: int,
    parse_mode: str = None,
    reply_markup: str = None,
):
    try:
        data = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": message,
            "disable_web_page_preview": True,
        }

        if reply_markup:
            data["reply_markup"] = reply_markup
        if parse_mode:
            data["parse_mode"] = parse_mode

        res = requests.post(f"{API_URI}/editMessageText", data=data)

        if res.status_code == 400 and "byte offset" in res.text:
            data["text"] = escape_markdown_string(data["text"])
            res = requests.post(
                f"{API_URI}/editMessageText", data=data, timeout=(60, 60)
            )

    except Exception as ex:
        syslog.create_warning(edit_message.__name__, ex)


def edit_message_reply_markup(
    chat_id: int,
    message_id: int,
    reply_markup: str,
):
    try:
        data = {
            "chat_id": chat_id,
            "message_id": message_id,
            "reply_markup": reply_markup,
        }

        requests.post(f"{API_URI}/editMessageReplyMarkup", data=data, timeout=(60, 60))

    except Exception as ex:
        syslog.create_warning(edit_message_reply_markup.__name__, ex)


def send_animation(chat_id: int, file_id: str, reply_id: int = 0):
    try:
        data = {"chat_id": chat_id, "animation": file_id}
        if reply_id != None and reply_id > 0:
            data["reply_to_message_id"] = reply_id

        requests.post(f"{API_URI}/sendAnimation", data=data, timeout=(60, 60))

    except Exception as ex:
        syslog.create_warning(send_animation.__name__, ex)


def send_video(chat_id: int, video_url: str, reply_id: int = 0):
    try:
        data = {"chat_id": chat_id, "video": video_url}
        if reply_id != None and reply_id > 0:
            data["reply_to_message_id"] = reply_id

        requests.post(f"{API_URI}/sendVideo", data=data, timeout=(60, 60))

    except Exception as ex:
        syslog.create_warning(send_video.__name__, ex)


def send_audio(chat_id: int, file_id: str, title: str, username: str):
    try:
        data = {
            "chat_id": chat_id,
            "audio": file_id,
        }

        requests.post(f"{API_URI}/sendAudio", data=data, timeout=(60, 60))

    except Exception as ex:
        syslog.create_warning(edit_message.__name__, ex)


def send_image(
    chat_id: int,
    file_id: str,
    caption: str = None,
    reply_id: int = None,
    reply_markup: str = None,
    parse_mode: str = "markdown",
):
    try:
        if file_id.startswith("[") and file_id.endswith("]"):
            arr_photo = literal_eval(file_id)
            random_index = randint(0, len(arr_photo) - 1)
            file_id = arr_photo[random_index]

        data = {"chat_id": chat_id, "photo": file_id}

        if caption:
            data["caption"] = caption
        if reply_id:
            data["reply_to_message_id"] = reply_id
        if reply_markup:
            data["reply_markup"] = reply_markup
        if parse_mode:
            data["parse_mode"] = parse_mode

        res = requests.post(f"{API_URI}/sendPhoto", data=data, timeout=(60, 60))

        if res.status_code == 400 and caption:
            send_message(
                chat_id=chat_id,
                message=caption,
                reply_id=reply_id,
                reply_markup=reply_markup,
                disable_web_page_preview=False,
                parse_mode=parse_mode,
            )
    except Exception as ex:
        syslog.create_warning(send_image.__name__, ex)


def answer_callback_query(callback_query_id: str, notification_text: str):
    try:
        data = {"callback_query_id": callback_query_id}
        if notification_text and len(notification_text) > 0:
            data["show_alert"] = True
            data["text"] = notification_text
        requests.post(f"{API_URI}/answerCallbackQuery", data=data, timeout=(60, 60))

    except Exception as ex:
        syslog.create_warning(answer_callback_query.__name__, ex)
