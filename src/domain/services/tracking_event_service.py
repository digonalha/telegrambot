from datetime import datetime
from dateutil import parser

from app.api import correios_api
from domain.services import tracking_code_service, message_service
from shared.helpers.logging_helper import SystemLogging
from shared.helpers.datetime_helper import days_between
from domain.models.tracking_event import TrackingEvent
from domain.schemas.tracking_event_schemas.tracking_event_create import (
    TrackingEventCreate,
)
from data.repositories import tracking_event_repository

syslog = SystemLogging(__name__)


def generate_tracking_event_create(
    tracking_code_id: int, tracking_event_obj
) -> TrackingEventCreate:
    city_destination = ""
    state_destination = ""
    unit_name_destination = ""
    unit_type_destination = ""

    if "unidadeDestino" in tracking_event_obj:
        city_destination = tracking_event_obj["unidadeDestino"]["endereco"].get(
            "cidade", ""
        )
        state_destination = tracking_event_obj["unidadeDestino"]["endereco"].get(
            "uf", ""
        )
        unit_name_destination = tracking_event_obj["unidadeDestino"].get("nome", "")
        unit_type_destination = tracking_event_obj["unidadeDestino"]["tipo"]

    return TrackingEventCreate(
        tracking_code_id=tracking_code_id,
        code=tracking_event_obj["codigo"],
        description=tracking_event_obj["descricao"],
        detail=tracking_event_obj.get("detalhe", ""),
        city_origin=tracking_event_obj["unidade"]["endereco"].get("cidade", ""),
        state_origin=tracking_event_obj["unidade"]["endereco"].get("uf", ""),
        unit_name_origin=tracking_event_obj["unidade"].get("nome", ""),
        unit_type_origin=tracking_event_obj["unidade"].get("tipo", ""),
        city_destination=city_destination,
        state_destination=state_destination,
        unit_name_destination=unit_name_destination,
        unit_type_destination=unit_type_destination,
        event_datetime=parser.parse(tracking_event_obj.get("dtHrCriado", "")),
        created_on=datetime.now(),
    )


def add_tracking_event(
    tracking_code_id: int, tracking_event_obj
) -> TrackingEvent or None:
    """Create a new tracking event on database if not exists."""

    if not tracking_event_repository.get(
        tracking_code_id,
        tracking_event_obj["codigo"],
        tracking_event_obj["dtHrCriado"],
    ):

        db_tracking_event = tracking_event_repository.add(
            generate_tracking_event_create(tracking_code_id, tracking_event_obj)
        )

        if db_tracking_event:
            return db_tracking_event

    return None


def list_tracking_events(code, list_all=True):
    tracking_info = correios_api.get_object_tracking_info(code.tracking_code)

    if len(tracking_info) == 1 and tracking_info[0]["mensagem"].startswith("SRO-019"):
        tracking_code_service.delete_tracking_code(code.id)
        return
    elif len(tracking_info) == 1 and tracking_info[0]["mensagem"].startswith("SRO-020"):
        return

    tracking_events = []

    for info in reversed(tracking_info):
        if list_all:
            tracking_events.append(generate_tracking_event_create(1, info))
        else:
            tracking_event = add_tracking_event(code.id, info)

            if tracking_event:
                tracking_events.append(tracking_event)

    tracking_message = ""

    if len(tracking_events) > 0:
        if code.name:
            tracking_message = (
                f"<b>Rastreio Correios</b> [{code.tracking_code} - {code.name}]\n\n"
            )
        else:
            tracking_message = f"<b>Rastreio Correios</b> [{code.tracking_code}]\n\n"

        index = 0

        for tracking_event in tracking_events:
            if len(tracking_events) > 1:
                index += 1

            if index > 1:
                tracking_message += "\n\n"

            tracking_message += f"🏷\n{tracking_event.description}"

            if tracking_event.detail:
                tracking_message += f"\n<i>{tracking_event.detail}</i>"

            if (
                tracking_event.unit_type_origin
                and tracking_event.unit_type_destination
                and tracking_event.unit_type_origin != "País"
            ):
                tracking_message += f"\nde <b>{tracking_event.unit_type_origin}</b> em <b>{tracking_event.city_origin} - {tracking_event.state_origin}</b>"
            elif tracking_event.unit_type_origin != "País":
                tracking_message += f"\nem <b>{tracking_event.unit_type_origin}</b>, <b>{tracking_event.city_origin} - {tracking_event.state_origin}</b>"
            else:
                tracking_message += f"\nem <b>{tracking_event.unit_name_origin}</b>"

            if (
                tracking_event.unit_type_destination
                and tracking_event.unit_type_origin != "País"
            ):
                tracking_message += f"\npara <b>{tracking_event.unit_type_destination}</b> em <b>{tracking_event.city_destination} - {tracking_event.state_destination}</b>"
            elif (
                tracking_event.unit_type_origin == "País"
                and tracking_event.unit_name_destination
            ):
                tracking_message += (
                    f"\npara <b>{tracking_event.unit_name_destination}</b>"
                )

                if tracking_event.state_destination:
                    tracking_message += f" - <b>{tracking_event.state_destination}</b>"

            tracking_message += (
                f"\n{tracking_event.event_datetime.strftime('%d/%m/%y - %H:%M')}"
            )

        if len(tracking_info) > 1:
            tracking_message += f"\n\n******\n<b>Tempo decorrido</b>: \n{days_between(tracking_info[len(tracking_info) - 1]['dtHrCriado'], tracking_info[0]['dtHrCriado'])} dias"
    elif list_all:
        tracking_message = f"Nenhum evento encontrado para o código de rastreio <b>{code.tracking_code}</b>"

    if (
        code.id > 0
        and len(tracking_info) > 0
        and tracking_info[0]["codigo"].startswith("BDE")
    ):
        tracking_code_service.deactivate_tracking_code(code.id)

    if tracking_message:
        message_service.send_message(code.user_id, tracking_message, parse_mode="HTML")
