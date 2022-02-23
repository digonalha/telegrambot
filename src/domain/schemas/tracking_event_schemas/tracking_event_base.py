from datetime import datetime
from pydantic import BaseModel


class TrackingEventBase(BaseModel):
    tracking_code_id: int
    code: str
    description: str
    detail: str

    city_origin: str
    state_origin: str
    unit_name_origin: str
    unit_type_origin: str

    city_destination: str
    state_destination: str
    unit_name_destination: str
    unit_type_destination: str

    event_datetime: datetime
