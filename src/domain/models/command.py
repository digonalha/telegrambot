from sqlalchemy import (
    Column,
    BigInteger,
    ForeignKey,
    String,
    DateTime,
    UniqueConstraint,
)
from sqlalchemy.sql.sqltypes import Integer
from data.database.config import base


class Command(base):
    __tablename__ = "command"
    __table_args__ = (UniqueConstraint("chat_id", "command", name="_chat_command_uc"),)

    id = Column(BigInteger, primary_key=True, autoincrement=True, index=True)
    chat_id = Column(BigInteger, nullable=False)
    command = Column(String, nullable=False)
    text = Column(String, nullable=True)
    description = Column(String, nullable=True)
    file_id = Column(String, nullable=True)
    media_type = Column(Integer, nullable=True)
    created_by_user_id = Column(BigInteger, ForeignKey("user.user_id"))
    created_by_user_name = Column(String, nullable=False)
    created_on = Column(DateTime, nullable=False)
    modified_on = Column(DateTime, nullable=False)
