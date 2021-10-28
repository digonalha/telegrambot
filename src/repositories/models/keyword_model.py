from sqlalchemy import Column, BigInteger, String, DateTime, Integer
from repositories.database.config import base


class Keyword(base):
    __tablename__ = "keyword"

    user_id = Column(BigInteger, primary_key=True, autoincrement=False, index=True)
    keyword = Column(String, primary_key=True, nullable=False)
    max_price = Column(Integer, nullable=True)
    created_on = Column(DateTime, nullable=False)
