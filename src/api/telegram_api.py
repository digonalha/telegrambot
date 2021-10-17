import requests
from ast import literal_eval
from random import randint
from src.helpers.logging_helper import SystemLogging
from src.configs import settings

syslog = SystemLogging(__name__)

API_URI = f"https://api.telegram.org/bot{settings.api_token}"


def create_log_from_response(function_name, response):
    if response["ok"]:
        syslog.create_info(function_name, f"request has been sucessfully submitted!")
        return True

    syslog.create_warning(function_name, response["description"])
    return False


def get_updates(offset: int):
    try:
        query_offset = ""
        if offset > 0:
            query_offset = f"?offset={offset}"
        res = requests.get(f"{API_URI}/getUpdates{query_offset}")
        response_json = res.json()
        if create_log_from_response("get_updates", response_json):
            return response_json["result"]
        else:
            return []
    except Exception as ex:
        syslog.create_warning("get_updates", ex)
        return []


def delete_message(chat_id: int, message_id: int):
    try:
        res = requests.post(
            f"{API_URI}/deleteMessage",
            {"chat_id": chat_id, "message_id": message_id},
        )

        create_log_from_response("delete_message", res.json())
    except Exception as ex:
        syslog.create_warning("delete_message", ex)


def send_message(
    chat_id: int, message: str, reply_id: int = 0, parse_mode: str = "markdown"
):
    try:
        data = {"chat_id": chat_id, "text": message, "parse_mode": parse_mode, "disable_web_page_preview": True}

        if reply_id != None and reply_id > 0:
            data["reply_to_message_id"] = reply_id
        res = requests.post(f"{API_URI}/sendMessage", data=data)
        create_log_from_response("send_message", res.json())
    except Exception as ex:
        syslog.create_warning("send_message", ex)


def send_animation(chat_id: int, file_id: str, reply_id: int = 0):
    try:
        data = {"chat_id": chat_id, "animation": file_id}
        if reply_id != None and reply_id > 0:
            data["reply_to_message_id"] = reply_id
        res = requests.post(f"{API_URI}/sendAnimation", data=data)
        create_log_from_response("send_animation", res.json())
    except Exception as ex:
        syslog.create_warning("send_animation", ex)


def send_video(chat_id: int, video_url: str, reply_id: int = 0):
    try:
        data = {"chat_id": chat_id, "video": video_url}
        if reply_id != None and reply_id > 0:
            data["reply_to_message_id"] = reply_id
        res = requests.post(f"{API_URI}/sendVideo", data=data)
        create_log_from_response("send_video", res.json())
    except Exception as ex:
        syslog.create_warning("send_video", ex)


def send_audio(chat_id: int, file_id: str, title: str, username: str):
    try:
        data = {
            "chat_id": chat_id,
            # "title": title,
            # "performer": username,
            "audio": file_id,
        }

        res = requests.post(f"{API_URI}/sendAudio", data=data)
        create_log_from_response("send_audio", res.json())
    except Exception as ex:
        syslog.create_warning("send_audio", ex)


def send_image(chat_id: int, file_id: str, caption: str = None, reply_id: int = None):
    try:
        if file_id.startswith("[") and file_id.endswith("]"):
            arr_photo = literal_eval(file_id)
            random_index = randint(0, len(arr_photo) - 1)
            file_id = arr_photo[random_index]

        data = {"chat_id": chat_id, "photo": file_id, "parse_mode": "markdown"}

        if caption:
            data["caption"] = caption
        if reply_id:
            data["reply_to_message_id"] = reply_id

        res = requests.post(f"{API_URI}/sendPhoto", data=data)
        create_log_from_response("send_photo", res.json())
    except Exception as ex:
        syslog.create_warning("send_photo", ex)
