from random import randint
from time import sleep
from helpers.logging_helper import SystemLogging

syslog = SystemLogging(__name__)


def run_tracking_worker() -> None:
    """Loop for make requests to correios api."""

    while True:
        try:

        finally:
            sleep(randint(300, 500))
