from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.declarative import declarative_base

from src.config import get_settings

settings = get_settings()
DATABASE_URL = settings.pg.uri
engine = create_async_engine(DATABASE_URL, echo=True, future=True)
metadata = MetaData()
Base = declarative_base(metadata=metadata)
