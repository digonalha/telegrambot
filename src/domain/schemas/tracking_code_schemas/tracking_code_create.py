from datetime import datetime
from domain.schemas.tracking_code_schemas.tracking_code_base import TrackingCodeBase


class TrackingCodeCreate(TrackingCodeBase):
    created_on: datetime
