from sqlalchemy import func

from data.database import database
from domain.models.tracking_code import TrackingCode
from domain.schemas.tracking_code_schemas.tracking_code_create import TrackingCodeCreate


local_session = database.get()


def add(tracking_code: TrackingCodeCreate) -> TrackingCode:
    new_tracking = TrackingCode(**tracking_code.dict())

    local_session.add(new_tracking)
    local_session.commit()
    local_session.refresh(new_tracking)

    return new_tracking


def get_all():
    return (
        local_session.query(TrackingCode).filter(TrackingCode.is_active == True).all()
    )


def get(user_id: int, code: str):
    return (
        local_session.query(TrackingCode)
        .filter(TrackingCode.user_id == user_id, TrackingCode.tracking_code == code)
        .first()
    )


def delete(user_id: int, code: str):
    local_session.query(TrackingCode).filter(
        TrackingCode.user_id == user_id,
        func.lower(TrackingCode.tracking_code) == code.lower(),
    ).delete(synchronize_session="fetch")

    local_session.commit()


def delete_all_by_user_id(user_id: int):
    local_session.query(TrackingCode).filter(TrackingCode.user_id == user_id).delete()
    local_session.commit()
