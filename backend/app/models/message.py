import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, LargeBinary, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    whatsapp_message_id: Mapped[str] = mapped_column(String(200), unique=True, nullable=False, index=True)
    contact_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("contacts.id"))
    direction: Mapped[str] = mapped_column(String(10), nullable=False)  # inbound | outbound
    message_type: Mapped[str] = mapped_column(String(20), nullable=False)  # text | voice | image | document
    body_encrypted: Mapped[bytes | None] = mapped_column(LargeBinary)
    voice_transcript: Mapped[str | None] = mapped_column(Text)
    is_group_message: Mapped[bool] = mapped_column(Boolean, default=False)
    group_jid: Mapped[str | None] = mapped_column(String(100))
    sender_jid: Mapped[str | None] = mapped_column(String(100))
    push_name: Mapped[str | None] = mapped_column(String(255))
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    ai_processed: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    ai_intent: Mapped[str | None] = mapped_column(String(50))
    ai_category: Mapped[str | None] = mapped_column(String(50))
    ai_confidence: Mapped[float | None] = mapped_column(Float)
    needs_review: Mapped[bool] = mapped_column(Boolean, default=False)
    raw_payload_json: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    contact: Mapped["Contact"] = relationship("Contact", foreign_keys=[contact_id])
