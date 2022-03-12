from random import randint
from time import sleep

from app.api import correios_api
from domain.services import (
    tracking_code_service,
    tracking_event_service,
    message_service,
)
from shared.helpers.logging_helper import SystemLogging

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

                tracking_events = []

                for info in reversed(tracking_info):
                    tracking_event = tracking_event_service.add_tracking_event(
                        code.id, info
                    )

                    if tracking_event:
                        tracking_events.append(tracking_event)

                if len(tracking_events) > 0:
                    if code.name:
                        tracking_message = (
                            f"<b>Correios</b>"
                            + "\n--------------------\n"
                            + "<u>Informações</u>"
                            + f"\n\n<b>Nome</b>: {code.name}"
                            + f"\n<b>Cód. Rastreio</b>: {code.tracking_code}"
                            + "\n--------------------\n"
                            + "<u>Eventos</u>\n\n"
                        )
                    index = 0

                    for tracking_event in tracking_events:
                        if len(tracking_events) > 1:
                            index += 1

                        if index > 1:
                            tracking_message += "\n\n"

                        if index >= 1:
                            tracking_message += f"<b>{index}.</b> "

                        tracking_message += f"[{tracking_event.event_datetime.strftime('%d/%m/%y - %H:%M')}]  <b>{tracking_event.description}</b>"

                        if tracking_event.unit_name_destination:
                            tracking_message += f"\n<b>Destino</b>: {tracking_event.unit_name_destination}"

                            if tracking_event.state_destination:
                                tracking_message += (
                                    f" - {tracking_event.state_destination}"
                                )

                        if tracking_event.unit_name_origin:
                            tracking_message += (
                                f"\n<b>Origem</b>: {tracking_event.unit_name_origin}"
                            )

                            if tracking_event.state_origin:
                                tracking_message += f" - {tracking_event.state_origin}"

                    message_service.send_message(
                        code.user_id, tracking_message, parse_mode="HTML"
                    )

        except Exception as ex:
            syslog.create_warning("run_tracking_worker", ex, code.user_id)
        finally:
            sleep(randint(300, 500))
