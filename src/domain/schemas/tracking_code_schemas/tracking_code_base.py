from pydantic import BaseModel


class TrackingCodeBase(BaseModel):
    user_id: int
    tracking_code: str
    name: str
    is_active: bool
