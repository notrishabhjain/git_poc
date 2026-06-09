from datetime import datetime, time

from sqlalchemy import Boolean, DateTime, LargeBinary, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class UserSettings(Base):
    __tablename__ = "user_settings"

    id: Mapped[int] = mapped_column(primary_key=True, default=1)
    working_hours_start: Mapped[str] = mapped_column(String(5), default="09:00")
    working_hours_end: Mapped[str] = mapped_column(String(5), default="19:00")
    timezone: Mapped[str] = mapped_column(String(50), default="Asia/Kolkata")
    notification_prefs_json: Mapped[str | None] = mapped_column(Text)  # JSON string
    google_oauth_token: Mapped[bytes | None] = mapped_column(LargeBinary)
    whatsapp_connected: Mapped[bool] = mapped_column(Boolean, default=False)
    ai_classifier_model: Mapped[str] = mapped_column(String(100), default="llama-3.1-8b-instant")
    ai_extractor_model: Mapped[str] = mapped_column(String(100), default="meta/llama-3.3-70b-instruct")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
