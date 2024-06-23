import asyncio

import pytest
from faker import Faker
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from ..core import models, repositories
from ..public.api.v1.endpoints import get_meme_repo, get_file_service
from ..public.app import app as public_app
from ..storages.postgres import Base

fake = Faker('ru_RU')

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
ASYNC_SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
async_engine = create_async_engine(ASYNC_SQLALCHEMY_DATABASE_URL,
                                   connect_args={"check_same_thread": False},
                                   poolclass=StaticPool)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
AsyncTestingSessionLocal = async_sessionmaker(async_engine,
                                              class_=AsyncSession,
                                              expire_on_commit=False,
                                              autocommit=False,
                                              autoflush=False)


Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

def override_get_meme_repo():
    meme_repo = repositories.MemeRepository()
    meme_repo._engine = async_engine
    meme_repo.session = AsyncTestingSessionLocal()
    yield meme_repo


public_app.dependency_overrides[get_meme_repo] = override_get_meme_repo


@pytest.fixture(scope="session")
def event_loop():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="module")
def sync_db_session():
    connection = engine.connect()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()

@pytest.fixture
def client():
    return AsyncClient(app=public_app, base_url='http://testserver')


@pytest.fixture
def meme_data_factory():
    def _create_meme_data() -> dict:
        return {"title": fake.sentence(), "content": fake.sentence(), "url": fake.url(), "etag": fake.uuid4()}
    return _create_meme_data


@pytest.fixture
def meme_factory(meme_data_factory, sync_db_session):
    memes = []
    data_list = []
    def meme(qty: int = 1):
        for _ in range(qty):
            data = meme_data_factory()
            meme = models.Meme(**data)
            sync_db_session.add(meme)
            memes.append(meme)
            data_list.append(data)
        sync_db_session.commit()
        return list(zip(memes, data_list))
    yield meme
    for meme in memes:
        sync_db_session.delete(meme)
    sync_db_session.commit()


