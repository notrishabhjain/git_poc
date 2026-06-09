import asyncio
import logging

from app.db.session import AsyncSessionLocal
from app.services.reminder_service import dispatch_reminder, get_due_reminders

logger = logging.getLogger(__name__)


async def run_reminder_loop():
    """Background task: check for due reminders every 60 seconds."""
    logger.info("Reminder engine started")
    while True:
        try:
            async with AsyncSessionLocal() as db:
                reminders = await get_due_reminders(db)
                for reminder in reminders:
                    await dispatch_reminder(db, reminder)
                if reminders:
                    logger.info(f"Dispatched {len(reminders)} reminder(s)")
        except Exception as e:
            logger.error(f"Reminder engine error: {e}")
        await asyncio.sleep(60)
