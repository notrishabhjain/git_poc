import logging

import httpx

from app.config import settings
from app.utils.retry import async_retry

logger = logging.getLogger(__name__)


@async_retry(max_attempts=3, base_delay=2.0)
async def send_message(jid: str, text: str) -> bool:
    """Send an outbound WhatsApp message via the Baileys bridge."""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                f"{settings.bridge_url}/send",
                json={"jid": jid, "message": text},
                headers={"Authorization": f"Bearer {settings.bridge_shared_secret}"},
            )
            return response.status_code < 400
    except Exception as e:
        logger.error(f"Failed to send WhatsApp message: {e}")
        return False
