from sqlalchemy import Column, BigInteger, String, DateTime, Boolean, Integer
from src.repositories.database.config import base


class User(base):
    __tablename__ = "user"

    user_id = Column(BigInteger, primary_key=True, autoincrement=False, index=True)
    user_name = Column(String, nullable=True)
    first_name = Column(String, nullable=False)
    is_admin = Column(Boolean, nullable=False)
    table_width = Column(Integer, nullable=True)
    created_on = Column(DateTime, nullable=False)
    modified_on = Column(DateTime, nullable=False)
