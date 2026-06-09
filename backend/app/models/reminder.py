import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Reminder(Base):
    __tablename__ = "reminders"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("tasks.id"))
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    remind_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    recurrence_rule: Mapped[str | None] = mapped_column(String(255))
    notification_sent: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    snooze_count: Mapped[int] = mapped_column(Integer, default=0)
    max_snoozes: Mapped[int] = mapped_column(Integer, default=3)
    escalation_action: Mapped[str] = mapped_column(String(50), default="notify")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    task: Mapped["Task"] = relationship("Task", foreign_keys=[task_id])
