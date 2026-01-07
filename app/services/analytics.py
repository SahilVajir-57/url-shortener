from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import Request
from app.models.click import Click
from datetime import datetime, timedelta, timezone


async def record_click(
    db: AsyncSession,
    url_id: int,
    request: Request,
) -> None:
    """Record detailed click analytics."""
    click = Click(
        url_id=url_id,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        referrer=request.headers.get("referer"),
    )
    db.add(click)
    await db.flush()


async def get_click_analytics(
    db: AsyncSession,
    url_id: int,
    days: int = 7,
) -> dict:
    """Get click analytics for the past N days."""
    since = datetime.now(timezone.utc) - timedelta(days=days)
    
    # Total clicks
    total_result = await db.execute(
        select(func.count()).select_from(Click).where(
            Click.url_id == url_id,
            Click.clicked_at >= since,
        )
    )
    total_clicks = total_result.scalar()
    
    # Clicks per day
    daily_result = await db.execute(
        select(
            func.date(Click.clicked_at).label("date"),
            func.count().label("clicks"),
        )
        .where(Click.url_id == url_id, Click.clicked_at >= since)
        .group_by(func.date(Click.clicked_at))
        .order_by(func.date(Click.clicked_at))
    )
    daily_clicks = [{"date": str(row.date), "clicks": row.clicks} for row in daily_result]
    
    # Top referrers
    referrer_result = await db.execute(
        select(Click.referrer, func.count().label("count"))
        .where(Click.url_id == url_id, Click.clicked_at >= since, Click.referrer.isnot(None))
        .group_by(Click.referrer)
        .order_by(func.count().desc())
        .limit(5)
    )
    top_referrers = [{"referrer": row.referrer, "count": row.count} for row in referrer_result]
    
    return {
        "total_clicks": total_clicks,
        "daily_clicks": daily_clicks,
        "top_referrers": top_referrers,
    }