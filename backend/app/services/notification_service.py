import logging

import httpx

from app.config import settings
from app.utils.retry import async_retry

logger = logging.getLogger(__name__)

PRIORITY_MAP = {"low": 1, "medium": 2, "high": 4, "critical": 5}


@async_retry(max_attempts=3, base_delay=2.0)
async def send_push(
    title: str,
    body: str,
    priority: str = "medium",
    tags: list[str] | None = None,
    click_url: str | None = None,
) -> bool:
    """Send a push notification via ntfy.sh."""
    topic_url = f"https://ntfy.sh/{settings.ntfy_topic}"
    headers = {
        "Title": title,
        "Priority": str(PRIORITY_MAP.get(priority, 3)),
        "Content-Type": "text/plain",
    }
    if tags:
        headers["Tags"] = ",".join(tags)
    if click_url:
        headers["Click"] = click_url
    if settings.ntfy_token:
        headers["Authorization"] = f"Bearer {settings.ntfy_token}"

    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.post(topic_url, content=body.encode(), headers=headers)
        if response.status_code >= 400:
            logger.error(f"ntfy.sh error {response.status_code}: {response.text}")
            return False
        return True
