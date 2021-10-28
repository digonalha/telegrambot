from sqlalchemy import Column, BigInteger, String, DateTime
from sqlalchemy.sql.sqltypes import Integer
from repositories.database.config import base
from enum import IntEnum


class MediaType(IntEnum):
    NONE = 0
    AUDIO = 1
    IMAGE = 2
    ANIMATION = 3
    VIDEO = 4


class CustomCommand(base):
    __tablename__ = "custom_command"

    command = Column(String, primary_key=True, index=True)
    text = Column(String, nullable=True)
    description = Column(String, nullable=True)
    file_id = Column(String, nullable=True)
    media_type = Column(Integer, nullable=True)
    chat_id = Column(BigInteger, primary_key=True, autoincrement=False, index=True)
    created_by_user_id = Column(BigInteger, nullable=False)
    created_by_user_name = Column(String, nullable=False)
    created_on = Column(DateTime, nullable=False)
    modified_on = Column(DateTime, nullable=False)
