from sqlalchemy import Column, BigInteger, String, DateTime, Numeric
from src.repositories.database.config import base


class SaleTrackerKeyword(base):
    __tablename__ = "sale_tracker_keyword"

    id = Column(BigInteger, primary_key=True, autoincrement=True, index=True)
    user_id = Column(BigInteger, nullable=False)
    chat_id = Column(BigInteger, nullable=False)
    user_name = Column(String, nullable=False)
    keyword = Column(String, nullable=False)
    created_on = Column(DateTime, nullable=False)
    modified_on = Column(DateTime, nullable=False)
