from sqlalchemy import String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from app.database import Base
from datetime import datetime


class Click(Base):
    __tablename__ = "clicks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    url_id: Mapped[int] = mapped_column(Integer, ForeignKey("urls.id"), nullable=False)
    ip_address: Mapped[str | None] = mapped_column(String(50), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)
    referrer: Mapped[str | None] = mapped_column(Text, nullable=True)
    country: Mapped[str | None] = mapped_column(String(100), nullable=True)
    clicked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())