from sqlalchemy import Column, BigInteger, String, DateTime, ForeignKey
from data.database.config import base


class TrackingEvent(base):
    __tablename__ = "tracking_event"

    id = Column(BigInteger, primary_key=True, autoincrement=True, index=True)
    tracking_code_id = Column(BigInteger, ForeignKey("tracking_code.id"))
    code = Column(String, nullable=False)
    description = Column(String, nullable=False)
    detail = Column(String, nullable=True)

    city_origin = Column(String, nullable=True)
    state_origin = Column(String, nullable=True)
    unit_name_origin = Column(String, nullable=True)
    unit_type_origin = Column(String, nullable=False)

    city_destination = Column(String, nullable=True)
    state_destination = Column(String, nullable=True)
    unit_name_destination = Column(String, nullable=True)
    unit_type_destination = Column(String, nullable=True)

    event_datetime = Column(DateTime, nullable=False)
    created_on = Column(DateTime, nullable=False)
