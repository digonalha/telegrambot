import requests

from shared.helpers.logging_helper import SystemLogging

syslog = SystemLogging(__name__)

API_URI = f"https://api.promobit.com.br"


def get_last_sales(limit: int = 50) -> list():
    try:
        res = requests.get(
            f"{API_URI}/offers?limit={limit}&sort=latest", timeout=(10, 10)
        )

        if res.status_code != 200:
            return []

        response_json = res.json()
        return response_json["offers"]
    except requests.exceptions.Timeout as ex_timeout:
        syslog.create_warning(get_last_sales.__name__, ex_timeout)

    return []
