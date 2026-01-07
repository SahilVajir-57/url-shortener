from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
from app.database import get_db
from app.schemas.url import URLCreate, URLResponse, URLStats
from app.services.shortener import (
    create_short_url,
    get_url_by_code,
    increment_clicks,
    build_short_url,
)
from app.services.cache import (
    get_cached_url,
    set_cached_url,
    delete_cached_url,
    increment_clicks_cache,
    get_cached_clicks,
)

router = APIRouter(tags=["URLs"])


@router.post("/shorten", response_model=URLResponse, status_code=status.HTTP_201_CREATED)
async def shorten_url(
    url_data: URLCreate,
    db: AsyncSession = Depends(get_db),
):
    # Check if custom code already exists
    if url_data.custom_code:
        existing = await get_url_by_code(db, url_data.custom_code)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Custom code already in use",
            )
    
    url = await create_short_url(
        db=db,
        original_url=str(url_data.url),
        custom_code=url_data.custom_code,
        expires_at=url_data.expires_at,
    )
    
    # Cache the URL immediately
    await set_cached_url(url.short_code, url.original_url)
    
    return URLResponse(
        short_code=url.short_code,
        short_url=build_short_url(url.short_code),
        original_url=url.original_url,
        clicks=url.clicks,
        is_active=url.is_active,
        expires_at=url.expires_at,
        created_at=url.created_at,
    )


@router.get("/{short_code}")
async def redirect_to_url(
    short_code: str,
    db: AsyncSession = Depends(get_db),
):
    # Try cache first
    cached_url = await get_cached_url(short_code)
    
    if cached_url:
        # Increment clicks in Redis (async, non-blocking)
        await increment_clicks_cache(short_code)
        return RedirectResponse(url=cached_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    
    # Cache miss - check database
    url = await get_url_by_code(db, short_code)
    
    if not url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="URL not found",
        )
    
    if not url.is_active:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="URL has been deactivated",
        )
    
    if url.expires_at and url.expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="URL has expired",
        )
    
    # Cache for next time
    await set_cached_url(short_code, url.original_url)
    
    # Track click in database
    await increment_clicks(db, url)
    
    return RedirectResponse(url=url.original_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)


@router.get("/{short_code}/stats", response_model=URLStats)
async def get_url_stats(
    short_code: str,
    db: AsyncSession = Depends(get_db),
):
    url = await get_url_by_code(db, short_code)
    
    if not url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="URL not found",
        )
    
    # Get clicks from Redis cache
    cached_clicks = await get_cached_clicks(short_code)
    
    # Return combined clicks (DB + Redis)
    total_clicks = url.clicks + cached_clicks
    
    return URLStats(
        short_code=url.short_code,
        original_url=url.original_url,
        clicks=total_clicks,
        created_at=url.created_at,
        expires_at=url.expires_at,
        is_active=url.is_active,
    )
    
    return url


@router.delete("/{short_code}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_url(
    short_code: str,
    db: AsyncSession = Depends(get_db),
):
    url = await get_url_by_code(db, short_code)
    
    if not url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="URL not found",
        )
    
    url.is_active = False
    await db.flush()
    
    # Remove from cache
    await delete_cached_url(short_code)
    
    return None