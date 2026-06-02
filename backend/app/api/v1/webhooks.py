import hashlib
import hmac
import logging

from fastapi import APIRouter, BackgroundTasks, Depends, Header, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.pipeline import process_message
from app.config import settings
from app.db.session import get_db
from app.services.message_service import ingest_message
from app.services.whatsapp_service import send_message

router = APIRouter(prefix="/webhooks", tags=["webhooks"])
logger = logging.getLogger(__name__)


def verify_bridge_signature(body: bytes, signature: str | None) -> bool:
    if not signature:
        return False
    expected = hmac.new(
        settings.bridge_shared_secret.encode(),
        body,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


async def _process_in_background(payload: dict, message_id_str: str):
    """Run AI pipeline in the background after webhook returns."""
    from app.db.session import AsyncSessionLocal
    from sqlalchemy import select
    from app.models.message import Message
    import uuid

    async with AsyncSessionLocal() as db:
        try:
            result = await db.execute(
                select(Message).where(Message.whatsapp_message_id == payload["message_id"])
            )
            message = result.scalar_one_or_none()
            if not message:
                return

            body = payload.get("body") or message.voice_transcript or ""
            sender_name = payload.get("push_name") or payload.get("sender_jid", "Unknown")

            pipeline_result = await process_message(
                message=message,
                body_plaintext=body,
                sender_name=sender_name,
                db=db,
            )

            # Send confirmation for actionable tasks
            if pipeline_result.get("action") == "task_created":
                chat_jid = payload.get("chat_jid")
                if chat_jid and not payload.get("is_group"):
                    await send_message(
                        jid=chat_jid,
                        text=f"✅ Task noted: {payload.get('body', '')[:50]}…",
                    )
        except Exception as e:
            logger.error(f"Background pipeline error for {message_id_str}: {e}")


@router.post("/whatsapp/message", status_code=status.HTTP_202_ACCEPTED)
async def receive_whatsapp_message(
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    x_webhook_signature: str | None = Header(default=None),
):
    body_bytes = await request.body()

    if not verify_bridge_signature(body_bytes, x_webhook_signature):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid signature")

    payload = await request.json()

    message, body_plaintext = await ingest_message(db, payload)
    if message is None:
        return {"status": "duplicate"}

    await db.commit()

    background_tasks.add_task(_process_in_background, payload, str(message.id))

    return {"status": "accepted", "message_id": str(message.id)}
