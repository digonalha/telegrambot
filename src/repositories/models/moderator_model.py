from sqlalchemy import Column, BigInteger, DateTime
from src.repositories.database.config import base


class Moderator(base):
    __tablename__ = "moderator"

    user_id = Column(BigInteger, primary_key=True, autoincrement=False, index=True)
    chat_id = Column(BigInteger, primary_key=True, autoincrement=False, index=True)
    created_on = Column(DateTime, nullable=False)
