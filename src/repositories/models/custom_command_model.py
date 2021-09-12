from sqlalchemy import Column, BigInteger, String, DateTime
from src.repositories.database.config import base


class CustomCommand(base):
    __tablename__ = "custom_command"

    command = Column(String, primary_key=True, index=True)
    text = Column(String, nullable=True)
    description = Column(String, nullable=True)
    file_id = Column(String, nullable=True)
    media_type = Column(String, nullable=True)
    chat_id = Column(BigInteger, primary_key=True, index=True)
    created_by_user_id = Column(BigInteger, nullable=False)
    created_by_username = Column(String, nullable=False)
    created_on = Column(DateTime, nullable=False)
    modified_on = Column(DateTime, nullable=False)
