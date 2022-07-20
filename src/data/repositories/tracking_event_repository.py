from datetime import datetime

from data.database import database
from domain.models.tracking_event import TrackingEvent
from domain.schemas.tracking_event_schemas.tracking_event_create import (
    TrackingEventCreate,
)


def add(tracking_event: TrackingEventCreate) -> TrackingEvent:
    local_session = database.get()

    new_event = TrackingEvent(**tracking_event.dict())

    local_session.add(new_event)
    local_session.commit()
    local_session.refresh(new_event)

    return new_event


def get(tracking_code_id: int, code: str, event_datetime: datetime):
    return (
        database.get()
        .query(TrackingEvent)
        .filter(
            TrackingEvent.tracking_code_id == tracking_code_id,
            TrackingEvent.code == code,
            TrackingEvent.event_datetime == event_datetime,
        )
        .first()
    )
