from random import randint
from time import sleep

from app.api import correios_api
from shared.helpers.logging_helper import SystemLogging

syslog = SystemLogging(__name__)


def run_tracking_worker() -> None:
    """Loop for make requests to correios api."""

    while True:
        try:
            # tracking_codes = tracking_code_service.get_all_current()

            correios_api.get_object_tracking_info("LB289177205HK")
        finally:
            sleep(randint(300, 500))
