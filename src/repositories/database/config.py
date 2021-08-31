from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

CONNECTION_STRING = os.getenv("CONNECTION_STRING")

engine = create_engine(CONNECTION_STRING)
session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
base = declarative_base()
