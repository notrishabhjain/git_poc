import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.contact import Contact
from app.models.message import Message
from app.utils.crypto import decrypt, encrypt

logger = logging.getLogger(__name__)


async def get_or_create_contact(db: AsyncSession, jid: str, display_name: str, is_group: bool) -> Contact:
    result = await db.execute(select(Contact).where(Contact.whatsapp_jid == jid))
    contact = result.scalar_one_or_none()
    if not contact:
        contact = Contact(
            whatsapp_jid=jid,
            display_name=display_name,
            is_group=is_group,
            category="uncategorized",
        )
        db.add(contact)
        await db.flush()
    elif contact.display_name != display_name and display_name:
        contact.display_name = display_name
    return contact


async def ingest_message(db: AsyncSession, payload: dict) -> tuple[Message | None, str]:
    """
    Deduplicate, store, and return (message, body_plaintext).
    Returns (None, "") if duplicate.
    """
    msg_id = payload["message_id"]

    # Deduplication check
    result = await db.execute(select(Message).where(Message.whatsapp_message_id == msg_id))
    if result.scalar_one_or_none():
        logger.debug(f"Duplicate message ignored: {msg_id}")
        return None, ""

    chat_jid = payload["chat_jid"]
    sender_jid = payload.get("sender_jid", chat_jid)
    push_name = payload.get("push_name", "")
    is_group = payload.get("is_group", False)
    body = payload.get("body") or ""
    message_type = payload.get("message_type", "text")
    ts = payload.get("timestamp", 0)
    timestamp = datetime.fromtimestamp(ts, tz=timezone.utc) if ts else datetime.now(timezone.utc)

    # Get/create contact
    contact = await get_or_create_contact(
        db=db,
        jid=chat_jid,
        display_name=push_name if not is_group else chat_jid,
        is_group=is_group,
    )

    message = Message(
        whatsapp_message_id=msg_id,
        contact_id=contact.id,
        direction="inbound",
        message_type=message_type,
        body_encrypted=encrypt(body) if body else None,
        is_group_message=is_group,
        group_jid=chat_jid if is_group else None,
        sender_jid=sender_jid,
        push_name=push_name,
        timestamp=timestamp,
        ai_processed=False,
        raw_payload_json={k: v for k, v in payload.items() if k != "body"},
    )
    db.add(message)
    await db.flush()
    return message, body


async def get_messages(db: AsyncSession, limit: int = 50, offset: int = 0) -> list[dict]:
    result = await db.execute(
        select(Message).order_by(Message.timestamp.desc()).limit(limit).offset(offset)
    )
    messages = result.scalars().all()
    out = []
    for m in messages:
        body = ""
        if m.body_encrypted:
            try:
                body = decrypt(m.body_encrypted)
            except Exception:
                body = "[encrypted]"
        out.append({
            "id": str(m.id),
            "whatsapp_message_id": m.whatsapp_message_id,
            "direction": m.direction,
            "message_type": m.message_type,
            "body": body,
            "voice_transcript": m.voice_transcript,
            "is_group_message": m.is_group_message,
            "sender_jid": m.sender_jid,
            "push_name": m.push_name,
            "timestamp": m.timestamp.isoformat(),
            "ai_intent": m.ai_intent,
            "ai_category": m.ai_category,
            "ai_confidence": m.ai_confidence,
            "needs_review": m.needs_review,
            "ai_processed": m.ai_processed,
        })
    return out
