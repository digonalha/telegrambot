from random import randint
from time import sleep

from app.api import correios_api
from shared.helpers.logging_helper import SystemLogging
from domain.services import tracking_code_service

syslog = SystemLogging(__name__)


def run_tracking_worker() -> None:
    """Loop for make requests to correios api."""

    while True:
        try:
            tracking_codes = tracking_code_service.get_all_active()

            for code in tracking_codes:
                tracking_info = correios_api.get_object_tracking_info(
                    code.tracking_code
                )

                if len(tracking_info) == 1 and tracking_info[0]["mensagem"].startswith(
                    "SRO-019"
                ):
                    tracking_code_service.delete_tracking_code(code.id)
                    return
                elif len(tracking_info) == 1 and tracking_info[0][
                    "mensagem"
                ].startswith("SRO-020"):
                    return

                for info in tracking_info:
                    print(info)

        finally:
            sleep(randint(300, 500))
