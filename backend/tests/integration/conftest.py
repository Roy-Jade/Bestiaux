from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from bestiaux.database import get_db
from bestiaux.main import app
from bestiaux.models import Allele, Base
from bestiaux.seed_data import ALLELE_CATALOG

TEST_DATABASE_URL = "postgresql+asyncpg://bestiaux:bestiaux@localhost:5432/bestiaux_test"

engine_test = create_async_engine(TEST_DATABASE_URL)
async_session_test = async_sessionmaker(engine_test, expire_on_commit=False)


@pytest.fixture(autouse=True)
async def setup_database() -> AsyncGenerator[None]:
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with async_session_test() as session:
        session.add_all(Allele(**allele) for allele in ALLELE_CATALOG)
        await session.commit()
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine_test.dispose()


async def _override_get_db() -> AsyncGenerator[AsyncSession]:
    async with async_session_test() as session:
        yield session


app.dependency_overrides[get_db] = _override_get_db


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient]:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
