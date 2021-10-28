from configs import settings
import requests


def send_alert_log_channel(message: str):
    if settings.error_log_channel:
        data = {
            "chat_id": settings.error_log_channel,
            "text": message,
            "parse_mode": "markdown",
        }

        response = requests.post(
            f"https://api.telegram.org/bot{settings.api_token}/sendMessage",
            data=data,
        )
        print(response)
