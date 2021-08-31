from sqlalchemy import Column, BigInteger, String, DateTime, Boolean
from src.repositories.database.config import base


class User(base):
    __tablename__ = "user"

    telegram_user_id = Column(BigInteger, primary_key=True, index=True)
    telegram_username = Column(String, nullable=False)
    is_admin = Column(Boolean, nullable=False)
    created_on = Column(DateTime, nullable=False)
    modified_on = Column(DateTime, nullable=False)
