from sqlalchemy import Column, Integer, String

from src.storages.postgres import Base


class Meme(Base):
    __tablename__ = 'memes'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(String)
    url = Column(String)
    etag = Column(String, index=True)
