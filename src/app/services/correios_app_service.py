from random import randint
from time import sleep

from domain.services import tracking_code_service, tracking_event_service
from shared.helpers.logging_helper import SystemLogging

syslog = SystemLogging(__name__)


def run_tracking_worker() -> None:
    """Loop for make requests to correios api."""

    while True:
        try:
            tracking_codes = tracking_code_service.get_all_active()

            for code in tracking_codes:
                tracking_event_service.list_tracking_events(code, False)

        except Exception as ex:
            syslog.create_warning("run_tracking_worker", ex, code.user_id)
        finally:
            sleep(randint(180, 360))
