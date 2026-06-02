import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.reminder import Reminder
from app.models.task import Task
from app.services.notification_service import send_push


async def get_due_reminders(db: AsyncSession) -> list[Reminder]:
    now = datetime.now(timezone.utc)
    result = await db.execute(
        select(Reminder)
        .where(Reminder.remind_at <= now)
        .where(Reminder.notification_sent == False)
        .order_by(Reminder.remind_at.asc())
        .limit(50)
    )
    return result.scalars().all()


async def dispatch_reminder(db: AsyncSession, reminder: Reminder) -> bool:
    result = await db.execute(select(Task).where(Task.id == reminder.task_id))
    task = result.scalar_one_or_none()

    title = reminder.title
    body = f"Due: {task.due_date.strftime('%a %b %d %H:%M') if task and task.due_date else 'Now'}"
    if task:
        body += f"\nCategory: {task.category} | Priority: {task.urgency}"

    tags = [task.category if task else "bell", "alarm_clock"]
    sent = await send_push(title=title, body=body, priority="high", tags=tags)

    if sent:
        reminder.notification_sent = True
        await db.commit()

    return sent


async def snooze_reminder(db: AsyncSession, reminder_id: uuid.UUID, minutes: int = 15) -> bool:
    from datetime import timedelta
    result = await db.execute(select(Reminder).where(Reminder.id == reminder_id))
    reminder = result.scalar_one_or_none()
    if not reminder or reminder.snooze_count >= reminder.max_snoozes:
        return False

    reminder.remind_at = datetime.now(timezone.utc) + timedelta(minutes=minutes)
    reminder.notification_sent = False
    reminder.snooze_count += 1
    await db.commit()
    return True
