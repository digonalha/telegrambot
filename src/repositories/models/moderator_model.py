from sqlalchemy import Column, BigInteger, DateTime
from src.repositories.database.config import base


class Moderator(base):
    __tablename__ = "moderator"

    telegram_user_id = Column(BigInteger, primary_key=True, index=True)
    chat_id = Column(BigInteger, primary_key=True, index=True)
    created_on = Column(DateTime, nullable=False)
