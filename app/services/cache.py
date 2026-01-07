import redis.asyncio as redis
from app.config import get_settings

settings = get_settings()

redis_client = redis.from_url(settings.redis_url, decode_responses=True)


async def get_cached_url(short_code: str) -> str | None:
    """Get original URL from cache."""
    return await redis_client.get(f"url:{short_code}")


async def set_cached_url(short_code: str, original_url: str, expire_seconds: int = 3600) -> None:
    """Cache original URL for 1 hour by default."""
    await redis_client.set(f"url:{short_code}", original_url, ex=expire_seconds)


async def delete_cached_url(short_code: str) -> None:
    """Remove URL from cache."""
    await redis_client.delete(f"url:{short_code}")


async def increment_clicks_cache(short_code: str) -> int:
    """Increment click count in Redis. Returns new count."""
    return await redis_client.incr(f"clicks:{short_code}")


async def get_cached_clicks(short_code: str) -> int:
    """Get click count from cache."""
    clicks = await redis_client.get(f"clicks:{short_code}")
    return int(clicks) if clicks else 0