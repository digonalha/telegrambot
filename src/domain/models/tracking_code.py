from sqlalchemy import (
    Boolean,
    Column,
    BigInteger,
    ForeignKey,
    String,
    DateTime,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from data.database.config import base
from domain.models.tracking_event import TrackingEvent


class TrackingCode(base):
    __tablename__ = "tracking_code"
    __table_args__ = (
        UniqueConstraint("user_id", "tracking_code", name="_user_trackingcode_uc"),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True, index=True)
    user_id = Column(BigInteger, ForeignKey("user.user_id"))
    tracking_code = Column(String, nullable=False)
    name = Column(String, nullable=True)
    is_active = Column(Boolean, nullable=True)
    created_on = Column(DateTime, nullable=False)
    event = relationship(TrackingEvent)
