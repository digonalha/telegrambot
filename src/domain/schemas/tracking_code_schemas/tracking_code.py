from domain.schemas.tracking_code_schemas.tracking_code_base import TrackingCodeBase


class TrackingCode(TrackingCodeBase):
    id: int

    class Config:
        orm_mode = True
        validate_assignment = True
