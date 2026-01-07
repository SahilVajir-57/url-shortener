import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from unittest.mock import AsyncMock, patch
from app.database import Base, get_db
from app.main import app
from app.models import URL, Click

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def override_get_db():
    async with TestSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(autouse=True)
def mock_redis():
    """Mock Redis for all tests."""
    cache_storage = {}
    
    async def mock_get(key):
        return cache_storage.get(key)
    
    async def mock_set(key, value, ex=None):
        cache_storage[key] = value
    
    async def mock_delete(key):
        cache_storage.pop(key, None)
    
    async def mock_incr(key):
        cache_storage[key] = cache_storage.get(key, 0) + 1
        return cache_storage[key]
    
    with patch("app.services.cache.redis_client") as mock_client:
        mock_client.get = AsyncMock(side_effect=mock_get)
        mock_client.set = AsyncMock(side_effect=mock_set)
        mock_client.delete = AsyncMock(side_effect=mock_delete)
        mock_client.incr = AsyncMock(side_effect=mock_incr)
        yield mock_client


@pytest.fixture(autouse=True)
def mock_rate_limiter():
    """Disable rate limiting for tests."""
    with patch("app.routers.urls.rate_limit_shorten", new_callable=AsyncMock):
        with patch("app.routers.urls.rate_limit_by_ip", new_callable=AsyncMock):
            yield


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c