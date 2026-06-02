from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.message import Message
from app.models.reminder import Reminder
from app.models.task import Task

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats")
async def get_stats(db: AsyncSession = Depends(get_db)):
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today_start + timedelta(days=1)

    tasks_today = await db.execute(
        select(func.count(Task.id)).where(Task.created_at >= today_start)
    )
    tasks_pending = await db.execute(
        select(func.count(Task.id)).where(Task.status == "pending")
    )
    tasks_overdue = await db.execute(
        select(func.count(Task.id))
        .where(Task.status == "pending")
        .where(Task.due_date < now)
    )
    tasks_completed_today = await db.execute(
        select(func.count(Task.id))
        .where(Task.completed_at >= today_start)
    )
    reminders_upcoming = await db.execute(
        select(func.count(Reminder.id))
        .where(Reminder.remind_at.between(now, tomorrow))
        .where(Reminder.notification_sent == False)
    )
    messages_today = await db.execute(
        select(func.count(Message.id)).where(Message.received_at >= today_start)
    )

    return {
        "tasks_created_today": tasks_today.scalar() or 0,
        "tasks_pending": tasks_pending.scalar() or 0,
        "tasks_overdue": tasks_overdue.scalar() or 0,
        "tasks_completed_today": tasks_completed_today.scalar() or 0,
        "reminders_upcoming_24h": reminders_upcoming.scalar() or 0,
        "messages_today": messages_today.scalar() or 0,
    }
