from pydantic import BaseModel


class TrackingCodeBase(BaseModel):
    user_id: int
    tracking_code: str
    is_active: bool
