import asyncio
import logging

from app.db.session import AsyncSessionLocal
from app.services.calendar_service import sync_pending_events

logger = logging.getLogger(__name__)


async def run_calendar_sync_loop():
    """Background task: sync pending calendar events every 5 minutes."""
    logger.info("Calendar sync engine started")
    while True:
        await asyncio.sleep(300)  # 5 minutes
        try:
            async with AsyncSessionLocal() as db:
                await sync_pending_events(db)
        except Exception as e:
            logger.error(f"Calendar sync error: {e}")
