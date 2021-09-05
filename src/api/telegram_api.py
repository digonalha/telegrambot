import requests
import os
from dotenv import load_dotenv
from src.helpers.logging_helper import SystemLogging

syslog = SystemLogging(__name__)

load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")
API_URI = f"https://api.telegram.org/bot{API_TOKEN}"


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


def send_message(chat_id: int, message: str, reply_id: int = 0):
    try:
        data = {"chat_id": chat_id, "text": message, "parse_mode": "markdown"}
        if reply_id != None and reply_id > 0:
            data["reply_to_message_id"] = reply_id
        res = requests.post(f"{API_URI}/sendMessage", data=data)
        create_log_from_response("send_message", res.json())
    except Exception as ex:
        syslog.create_warning("send_message", ex)


def send_video(chat_id: int, video_url: str, reply_id: int = 0):
    try:
        data = {"chat_id": chat_id, "video": video_url}
        if reply_id != None and reply_id > 0:
            data["reply_to_message_id"] = reply_id
        res = requests.post(f"{API_URI}/sendVideo", data=data)
        create_log_from_response("send_video", res.json())
    except Exception as ex:
        syslog.create_warning("send_video", ex)


def send_photo(chat_id: int, photo: str, caption: str, reply_id: int = 0):
    try:
        data = {"chat_id": chat_id, "photo": photo, "caption": caption}
        if reply_id != None and reply_id > 0:
            data["reply_to_message_id"] = reply_id
        res = requests.post(f"{API_URI}/sendPhoto", data=data)
        create_log_from_response("send_photo", res.json())
    except Exception as ex:
        syslog.create_warning("send_photo", ex)
