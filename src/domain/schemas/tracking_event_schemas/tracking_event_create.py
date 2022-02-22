from datetime import datetime
from domain.schemas.tracking_event_schemas.tracking_event_base import TrackingEventBase


class TrackingEventCreate(TrackingEventBase):
    created_on: datetime
