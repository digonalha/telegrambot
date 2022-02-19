from sqlalchemy import Column, BigInteger, String, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from repositories.database.config import base
from repositories.models.tracking_event_model import TrackingEvent


class TrackingCode(base):
    __tablename__ = "tracking_code"

    __table_args__ = (
        UniqueConstraint('user_id', 'tracking_code', name='_user_trackingcode_uc'),
      )

    id = Column(BigInteger, primary_key=True, autoincrement=True, index=True)
    user_id = Column(BigInteger, nullable=False)
    tracking_code = Column(String, nullable=False)
    created_on = Column(DateTime, nullable=False)
    event = relationship(TrackingEvent)
