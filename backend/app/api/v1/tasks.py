import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.task_service import create_manual_task, get_task, get_tasks, update_task_status

router = APIRouter(prefix="/tasks", tags=["tasks"])


class CreateTaskRequest(BaseModel):
    title: str
    description: str | None = None
    category: str = "personal"
    intent: str = "task"
    urgency: str = "medium"
    importance: str = "medium"
    priority_score: int = 50
    due_date: str | None = None
    tags: list[str] | None = None


class UpdateStatusRequest(BaseModel):
    status: str


@router.get("")
async def list_tasks(
    status: str | None = None,
    category: str | None = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    return await get_tasks(db, status=status, category=category, limit=limit, offset=offset)


@router.get("/{task_id}")
async def get_single_task(task_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    task = await get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.post("", status_code=201)
async def create_task(body: CreateTaskRequest, db: AsyncSession = Depends(get_db)):
    return await create_manual_task(db, body.model_dump())


@router.patch("/{task_id}/status")
async def update_status(
    task_id: uuid.UUID,
    body: UpdateStatusRequest,
    db: AsyncSession = Depends(get_db),
):
    valid = {"pending", "in_progress", "done", "cancelled", "deferred"}
    if body.status not in valid:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid}")
    task = await update_task_status(db, task_id, body.status)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
