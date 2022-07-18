import requests

from shared.helpers.logging_helper import SystemLogging

syslog = SystemLogging(__name__)

API_URI = f"https://api.promobit.com.br"


def get_last_sales(limit: int = 50) -> list():
    res = requests.get(f"{API_URI}/offers?limit={limit}&sort=latest")

    if res.status_code != 200:
        return None

    response_json = res.json()
    return response_json["offers"]
