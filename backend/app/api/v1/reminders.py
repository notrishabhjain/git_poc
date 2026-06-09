import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.reminder import Reminder
from app.services.reminder_service import snooze_reminder

router = APIRouter(prefix="/reminders", tags=["reminders"])


@router.get("")
async def list_reminders(
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Reminder).order_by(Reminder.remind_at.asc()).limit(limit).offset(offset)
    )
    reminders = result.scalars().all()
    return [
        {
            "id": str(r.id),
            "task_id": str(r.task_id) if r.task_id else None,
            "title": r.title,
            "remind_at": r.remind_at.isoformat(),
            "recurrence_rule": r.recurrence_rule,
            "notification_sent": r.notification_sent,
            "snooze_count": r.snooze_count,
            "max_snoozes": r.max_snoozes,
        }
        for r in reminders
    ]


class SnoozeRequest(BaseModel):
    minutes: int = 15


@router.post("/{reminder_id}/snooze")
async def snooze(
    reminder_id: uuid.UUID,
    body: SnoozeRequest,
    db: AsyncSession = Depends(get_db),
):
    ok = await snooze_reminder(db, reminder_id, body.minutes)
    if not ok:
        raise HTTPException(status_code=400, detail="Cannot snooze (max snoozes reached or not found)")
    return {"status": "snoozed", "minutes": body.minutes}
