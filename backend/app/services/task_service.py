import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task


async def get_tasks(
    db: AsyncSession,
    status: str | None = None,
    category: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[dict]:
    q = select(Task)
    if status:
        q = q.where(Task.status == status)
    if category:
        q = q.where(Task.category == category)
    q = q.order_by(Task.priority_score.desc(), Task.created_at.desc()).limit(limit).offset(offset)
    result = await db.execute(q)
    return [_task_to_dict(t) for t in result.scalars().all()]


async def get_task(db: AsyncSession, task_id: uuid.UUID) -> dict | None:
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    return _task_to_dict(task) if task else None


async def update_task_status(db: AsyncSession, task_id: uuid.UUID, status: str) -> dict | None:
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        return None
    task.status = status
    if status == "done":
        task.completed_at = datetime.now(timezone.utc)
    await db.commit()
    return _task_to_dict(task)


async def create_manual_task(db: AsyncSession, data: dict) -> dict:
    task = Task(
        title=data["title"],
        description=data.get("description"),
        category=data.get("category", "personal"),
        intent=data.get("intent", "task"),
        status="pending",
        priority_score=data.get("priority_score", 50),
        urgency=data.get("urgency", "medium"),
        importance=data.get("importance", "medium"),
        due_date=data.get("due_date"),
        tags=data.get("tags"),
    )
    db.add(task)
    await db.commit()
    return _task_to_dict(task)


def _task_to_dict(t: Task) -> dict:
    return {
        "id": str(t.id),
        "title": t.title,
        "description": t.description,
        "category": t.category,
        "intent": t.intent,
        "status": t.status,
        "priority_score": t.priority_score,
        "urgency": t.urgency,
        "importance": t.importance,
        "due_date": t.due_date.isoformat() if t.due_date else None,
        "due_date_flexible": t.due_date_flexible,
        "context_summary": t.context_summary,
        "tags": t.tags,
        "source_message_id": str(t.source_message_id) if t.source_message_id else None,
        "calendar_event_id": str(t.calendar_event_id) if t.calendar_event_id else None,
        "created_at": t.created_at.isoformat(),
        "updated_at": t.updated_at.isoformat(),
        "completed_at": t.completed_at.isoformat() if t.completed_at else None,
    }
