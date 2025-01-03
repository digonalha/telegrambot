import requests

from app.configs import settings


def send_alert_log_channel(message: str):
    if settings.error_log_channel:
        data = {
            "chat_id": settings.error_log_channel,
            "text": message,
            "parse_mode": "markdown",
        }

        requests.post(
            f"https://api.telegram.org/bot{settings.api_token}/sendMessage",
            data=data,
        )
