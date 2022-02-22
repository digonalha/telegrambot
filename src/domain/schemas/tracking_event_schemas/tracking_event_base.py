from pydantic import BaseModel


class TrackingEventBase(BaseModel):
    tracking_code_id: int
    code: str
    description: str
    detail: str
    city: str
    country: str
    event_type: str
