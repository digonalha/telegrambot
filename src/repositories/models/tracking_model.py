from sqlalchemy import Column, BigInteger, String, DateTime, Integer
from repositories.database.config import base


class Tracking(base):
    __tablename__ = "tracking"

    user_id = Column(BigInteger, primary_key=True, autoincrement=False, index=True)
    code = Column(String, nullable=False)
    description = Column(String, nullable=False)
    detail = Column(String, nullable=True)
    created_on = Column(DateTime, nullable=False)
