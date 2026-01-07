import redis.asyncio as redis
from app.config import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

redis_client = None

try:
    if settings.redis_url:
        redis_client = redis.from_url(settings.redis_url, decode_responses=True)
except Exception as e:
    logger.warning(f"Redis not available: {e}")


async def get_cached_url(short_code: str) -> str | None:
    """Get original URL from cache."""
    if not redis_client:
        return None
    try:
        return await redis_client.get(f"url:{short_code}")
    except Exception:
        return None


async def set_cached_url(short_code: str, original_url: str, expire_seconds: int = 3600) -> None:
    """Cache original URL for 1 hour by default."""
    if not redis_client:
        return
    try:
        await redis_client.set(f"url:{short_code}", original_url, ex=expire_seconds)
    except Exception:
        pass


async def delete_cached_url(short_code: str) -> None:
    """Remove URL from cache."""
    if not redis_client:
        return
    try:
        await redis_client.delete(f"url:{short_code}")
    except Exception:
        pass


async def increment_clicks_cache(short_code: str) -> int:
    """Increment click count in Redis. Returns new count."""
    if not redis_client:
        return 0
    try:
        return await redis_client.incr(f"clicks:{short_code}")
    except Exception:
        return 0


async def get_cached_clicks(short_code: str) -> int:
    """Get click count from cache."""
    if not redis_client:
        return 0
    try:
        clicks = await redis_client.get(f"clicks:{short_code}")
        return int(clicks) if clicks else 0
    except Exception:
        return 0