from domain.schemas.tracking_event_schemas.tracking_event_base import TrackingEventBase


class TrackingEvent(TrackingEventBase):
    id: int

    class Config:
        orm_mode = True
        validate_assignment = True
