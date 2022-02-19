import requests
from helpers.logging_helper import SystemLogging

syslog = SystemLogging(__name__)

API_URI = "https://proxyapp.correios.com.br/v1/sro-rastro"


def get_object_tracking_info(tracking_id: str) -> list():
    try:
        res = requests.get(f"{API_URI}/{tracking_id}")

        if res.status_code != 200:
            return None

        response_json = res.json()

        return response_json["objetos"]
    except Exception as ex:
        syslog.create_warning("get_object_tracking_info", ex)
        return []