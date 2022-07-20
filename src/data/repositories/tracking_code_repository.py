from data.database import database
from domain.models.tracking_code import TrackingCode
from domain.models.tracking_event import TrackingEvent
from domain.schemas.tracking_code_schemas.tracking_code_create import TrackingCodeCreate


def add(tracking_code: TrackingCodeCreate) -> TrackingCode:
    local_session = database.get()

    new_tracking = TrackingCode(**tracking_code.dict())

    local_session.add(new_tracking)
    local_session.commit()
    local_session.refresh(new_tracking)

    return new_tracking


def get_all_active():
    return (
        database.get().query(TrackingCode).filter(TrackingCode.is_active == True).all()
    )


def get(user_id: int, code: str):
    return (
        database.get()
        .query(TrackingCode)
        .filter(TrackingCode.user_id == user_id, TrackingCode.tracking_code == code)
        .first()
    )


def get_by_id(id: int):
    return database.get().query(TrackingCode).filter(TrackingCode.id == id).first()


def get_by_user_id(user_id: int):
    return (
        database.get().query(TrackingCode).filter(TrackingCode.user_id == user_id).all()
    )


def delete_by_id(id: int):
    try:
        local_session = database.get()

        local_session.query(TrackingEvent).filter(
            TrackingEvent.tracking_code_id == id
        ).delete(synchronize_session="fetch")

        local_session.query(TrackingCode).filter(TrackingCode.id == id).delete(
            synchronize_session="fetch"
        )

        local_session.commit()
    except:
        local_session.rollback()
        raise


def delete_all_by_user_id(user_id: int):
    local_session = database.get()

    local_session.query(TrackingCode).filter(TrackingCode.user_id == user_id).delete()
    local_session.commit()


def deactivate_code(code_id: int) -> TrackingCode:
    local_session = database.get()

    db_tracking_code = (
        local_session.query(TrackingCode).filter(TrackingCode.id == code_id).first()
    )

    if not db_tracking_code:
        return None

    db_tracking_code.is_active = False

    local_session.commit()
    local_session.refresh(db_tracking_code)

    return not db_tracking_code.is_active
