from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.url import URL
from app.utils.base62 import generate_short_code
from app.config import get_settings

settings = get_settings()


async def create_short_url(
    db: AsyncSession,
    original_url: str,
    custom_code: str | None = None,
    expires_at = None,
) -> URL:
    # Use custom code or generate one
    if custom_code:
        short_code = custom_code
    else:
        short_code = await generate_unique_code(db)
    
    url = URL(
        short_code=short_code,
        original_url=original_url,
        expires_at=expires_at,
    )
    db.add(url)
    await db.flush()
    await db.refresh(url)
    return url


async def generate_unique_code(db: AsyncSession, length: int = 7) -> str:
    """Generate a unique short code that doesn't exist in DB."""
    for _ in range(10):  # Max 10 attempts
        code = generate_short_code(length)
        existing = await get_url_by_code(db, code)
        if not existing:
            return code
    # If still colliding, increase length
    return await generate_unique_code(db, length + 1)


async def get_url_by_code(db: AsyncSession, short_code: str) -> URL | None:
    result = await db.execute(
        select(URL).where(URL.short_code == short_code)
    )
    return result.scalar_one_or_none()


async def increment_clicks(db: AsyncSession, url: URL) -> None:
    url.clicks += 1
    await db.flush()


def build_short_url(short_code: str) -> str:
    return f"{settings.base_url}/{short_code}"