from datetime import datetime, time

from sqlalchemy import Boolean, DateTime, LargeBinary, String, Time, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class UserSettings(Base):
    __tablename__ = "user_settings"

    id: Mapped[int] = mapped_column(primary_key=True, default=1)
    working_hours_start: Mapped[time] = mapped_column(Time, default=time(9, 0))
    working_hours_end: Mapped[time] = mapped_column(Time, default=time(19, 0))
    timezone: Mapped[str] = mapped_column(String(50), default="Asia/Kolkata")
    notification_prefs: Mapped[dict] = mapped_column(JSONB, default=dict)
    google_oauth_token: Mapped[bytes | None] = mapped_column(LargeBinary)
    whatsapp_connected: Mapped[bool] = mapped_column(Boolean, default=False)
    ai_classifier_model: Mapped[str] = mapped_column(String(100), default="llama-3.1-8b-instant")
    ai_extractor_model: Mapped[str] = mapped_column(String(100), default="meta/llama-3.3-70b-instruct")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
