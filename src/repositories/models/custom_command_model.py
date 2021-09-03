from sqlalchemy import Column, BigInteger, String, DateTime
from src.repositories.database.config import base


class CustomCommand(base):
    __tablename__ = "custom_command"

    id = Column(BigInteger, primary_key=True, index=True)
    command = Column(String, nullable=False)
    description = Column(String, nullable=False)
    telegram_file_id = Column(String, nullable=True)
    text = Column(String, nullable=True)
    created_by_user_id = Column(BigInteger, nullable=True)
    created_by_username = Column(String, nullable=False)
    chat_id = Column(BigInteger, nullable=True)
    created_on = Column(DateTime, nullable=False)
    modified_on = Column(DateTime, nullable=False)
