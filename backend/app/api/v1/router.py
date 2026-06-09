from fastapi import APIRouter

from app.api.v1 import auth, calendar, dashboard, messages, reminders, tasks, webhooks

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router)
api_router.include_router(webhooks.router)
api_router.include_router(tasks.router)
api_router.include_router(messages.router)
api_router.include_router(reminders.router)
api_router.include_router(calendar.router)
api_router.include_router(dashboard.router)
