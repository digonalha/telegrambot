from random import randint
from time import sleep
from helpers.logging_helper import SystemLogging
from api import correios_api

syslog = SystemLogging(__name__)


def run_tracking_worker() -> None:
    """Loop for make requests to correios api."""

    while True:
        try:
            correios_api.get_object_tracking_info("LB289177205HK")
        finally:
            sleep(randint(300, 500))