from datetime import datetime
from dateutil import parser

from shared.helpers.logging_helper import SystemLogging
from domain.models.tracking_event import TrackingEvent
from domain.schemas.tracking_event_schemas.tracking_event_create import (
    TrackingEventCreate,
)
from data.repositories import tracking_event_repository

syslog = SystemLogging(__name__)


def add_tracking_event(
    tracking_code_id: int, tracking_event_obj
) -> TrackingEvent or None:
    """Create a new tracking event on database if not exists."""

    if not tracking_event_repository.get(
        tracking_code_id,
        tracking_event_obj["codigo"],
        tracking_event_obj["dtHrCriado"],
    ):

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

        db_tracking_event = tracking_event_repository.add(
            TrackingEventCreate(
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
        )

        if db_tracking_event:
            return db_tracking_event

    return None


# def delete_tracking_code(user_id: int, code: str) -> bool:
#     """Remove a tracking code from database if exists."""

#     tracking_code_db = tracking_code_repository.get(user_id, code)

#     if tracking_code_db:
#         tracking_code_repository.delete(user_id, code)
#         return True

#     return False
