from sqlalchemy import (
    Column,
    BigInteger,
    ForeignKey,
    String,
    DateTime,
    Integer,
    UniqueConstraint,
)
from database.config import base


class Keyword(base):
    __tablename__ = "keyword"
    __table_args__ = (UniqueConstraint("user_id", "keyword", name="_user_keyword_uc"),)

    id = Column(BigInteger, primary_key=True, autoincrement=True, index=True)
    user_id = Column(BigInteger, ForeignKey("user.user_id"))
    keyword = Column(String, nullable=False)
    max_price = Column(Integer, nullable=True)
    created_on = Column(DateTime, nullable=False)
    modified_on = Column(DateTime, nullable=False)
