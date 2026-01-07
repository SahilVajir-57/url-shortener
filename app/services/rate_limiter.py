import redis.asyncio as redis
from fastapi import HTTPException, status, Request
from app.config import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

redis_client = None

try:
    if settings.redis_url:
        redis_client = redis.from_url(settings.redis_url, decode_responses=True)
except Exception as e:
    logger.warning(f"Redis not available for rate limiting: {e}")


async def check_rate_limit(
    key: str,
    max_requests: int = 10,
    window_seconds: int = 60,
) -> None:
    """
    Check if rate limit exceeded.
    Skip if Redis not available.
    """
    if not redis_client:
        return
    
    try:
        current = await redis_client.get(key)
        
        if current is None:
            await redis_client.set(key, 1, ex=window_seconds)
        elif int(current) >= max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Try again in {window_seconds} seconds.",
            )
        else:
            await redis_client.incr(key)
    except HTTPException:
        raise
    except Exception:
        pass


async def rate_limit_by_ip(request: Request, max_requests: int = 10, window_seconds: int = 60) -> None:
    """Rate limit by IP address."""
    client_ip = request.client.host if request.client else "unknown"
    key = f"rate_limit:{client_ip}"
    await check_rate_limit(key, max_requests, window_seconds)


async def rate_limit_shorten(request: Request) -> None:
    """Stricter rate limit for creating URLs: 5 per minute."""
    client_ip = request.client.host if request.client else "unknown"
    key = f"rate_limit:shorten:{client_ip}"
    await check_rate_limit(key, max_requests=5, window_seconds=60)