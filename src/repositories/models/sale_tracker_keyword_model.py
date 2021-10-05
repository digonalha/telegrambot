from sqlalchemy import Column, BigInteger, String, DateTime, Numeric
from src.repositories.database.config import base


class SaleTrackerKeyword(base):
    __tablename__ = "sale_tracker_keyword"

    user_id = Column(BigInteger, primary_key=True, autoincrement=False, index=True)
    user_name = Column(String, nullable=False)
    keyword = Column(String, primary_key=True, nullable=False)
    created_on = Column(DateTime, nullable=False)
    modified_on = Column(DateTime, nullable=False)
