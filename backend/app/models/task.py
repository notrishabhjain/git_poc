import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_message_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("messages.id"))
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(50), nullable=False)  # work/personal/family/friends
    intent: Mapped[str] = mapped_column(String(50), nullable=False)  # meeting/deadline/follow_up/reminder/task/fyi
    status: Mapped[str] = mapped_column(String(20), default="pending", index=True)
    priority_score: Mapped[int] = mapped_column(Integer, default=50)  # 0-100
    urgency: Mapped[str] = mapped_column(String(10), default="medium")  # low/medium/high/critical
    importance: Mapped[str] = mapped_column(String(10), default="medium")
    due_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    due_date_flexible: Mapped[bool] = mapped_column(Boolean, default=True)
    assigned_contact_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("contacts.id")
    )
    context_summary: Mapped[str | None] = mapped_column(Text)
    calendar_event_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("calendar_events.id", use_alter=True)
    )
    tags: Mapped[list[str] | None] = mapped_column(ARRAY(String))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    source_message: Mapped["Message"] = relationship("Message", foreign_keys=[source_message_id])
    assigned_contact: Mapped["Contact"] = relationship("Contact", foreign_keys=[assigned_contact_id])
