import requests

from shared.helpers.logging_helper import SystemLogging

syslog = SystemLogging(__name__)

API_URI = f"https://proxyapp.correios.com.br/v1/sro-rastro"


def get_object_tracking_info(tracking_id: str) -> list():
    try:
        res = requests.get(f"{API_URI}/{tracking_id}", timeout=(10, 10))

        if res.status_code != 200:
            return None

        response_json = res.json()

        if "eventos" in response_json["objetos"][0]:
            return response_json["objetos"][0]["eventos"]
    except Exception as ex:
        syslog.create_warning(get_object_tracking_info.__name__, ex)

    return []
