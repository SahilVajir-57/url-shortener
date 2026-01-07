from pydantic import BaseModel, HttpUrl, Field
from datetime import datetime


# Request schemas
class URLCreate(BaseModel):
    url: HttpUrl
    custom_code: str | None = Field(default=None, min_length=3, max_length=20)
    expires_at: datetime | None = None


# Response schemas
class URLResponse(BaseModel):
    short_code: str
    short_url: str
    original_url: str
    clicks: int
    is_active: bool
    expires_at: datetime | None
    created_at: datetime

    class Config:
        from_attributes = True


class URLStats(BaseModel):
    short_code: str
    original_url: str
    clicks: int
    created_at: datetime
    expires_at: datetime | None
    is_active: bool

    class Config:
        from_attributes = True