from random import randint
from time import sleep

from domain.services import tracking_code_service, tracking_event_service
from shared.helpers.logging_helper import SystemLogging

syslog = SystemLogging(__name__)


def run_tracking_worker() -> None:
    """Loop for make requests to correios api."""
    try:
        while True:
            try:
                sleep(randint(120, 380))
                tracking_codes = tracking_code_service.get_all_active()
                for code in tracking_codes:
                    tracking_event_service.list_tracking_events(code, False)

            except Exception as ex:
                syslog.create_warning("tracking_worker", ex)
                continue
    except:
          syslog.create_warning("tracking_worker", ex)


