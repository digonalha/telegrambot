from sqlalchemy import Column, BigInteger, String, DateTime, ForeignKey
from data.database.config import base


class TrackingEvent(base):
    __tablename__ = "tracking_event"

    id = Column(BigInteger, primary_key=True, autoincrement=True, index=True)
    tracking_code_id = Column(BigInteger, ForeignKey("tracking_code.id"))
    code = Column(String, nullable=False)
    description = Column(String, nullable=False)
    detail = Column(String, nullable=True)
    city = Column(String, nullable=True)
    country = Column(String, nullable=True)
    event_type = Column(String, nullable=True)
    event_date = Column(DateTime, nullable=False)
    created_on = Column(DateTime, nullable=False)
