import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source_message_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("messages.id"))
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    intent: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending", index=True)
    priority_score: Mapped[int] = mapped_column(Integer, default=50)
    urgency: Mapped[str] = mapped_column(String(10), default="medium")
    importance: Mapped[str] = mapped_column(String(10), default="medium")
    due_date: Mapped[datetime | None] = mapped_column(DateTime, index=True)
    due_date_flexible: Mapped[bool] = mapped_column(Boolean, default=True)
    assigned_contact_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("contacts.id"))
    context_summary: Mapped[str | None] = mapped_column(Text)
    calendar_event_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("calendar_events.id", use_alter=True)
    )
    tags_json: Mapped[str | None] = mapped_column(Text)  # JSON array string
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime)

    source_message: Mapped["Message"] = relationship("Message", foreign_keys=[source_message_id])
    assigned_contact: Mapped["Contact"] = relationship("Contact", foreign_keys=[assigned_contact_id])
