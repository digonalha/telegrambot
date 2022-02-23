from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.configs import settings


engine = create_engine(settings.connection_string)
session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
base = declarative_base()
