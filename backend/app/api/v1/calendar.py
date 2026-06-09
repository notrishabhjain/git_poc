from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.session import get_db
from app.models.calendar_event import CalendarEvent
from app.models.user_settings import UserSettings
from app.services.calendar_service import get_credentials, get_oauth_flow, sync_pending_events
from app.utils.crypto import encrypt

router = APIRouter(prefix="/calendar", tags=["calendar"])


@router.get("/auth-url")
async def get_auth_url():
    """Step 1: Get the Google OAuth URL to redirect the user to."""
    if not settings.google_client_id:
        raise HTTPException(status_code=400, detail="Google OAuth not configured")
    flow = get_oauth_flow()
    auth_url, _ = flow.authorization_url(access_type="offline", prompt="consent")
    return {"auth_url": auth_url}


@router.get("/callback")
async def oauth_callback(code: str, db: AsyncSession = Depends(get_db)):
    """Step 2: Handle Google OAuth callback and store credentials."""
    flow = get_oauth_flow()
    flow.fetch_token(code=code)
    creds = flow.credentials

    result = await db.execute(select(UserSettings).where(UserSettings.id == 1))
    user_settings = result.scalar_one_or_none()
    if not user_settings:
        user_settings = UserSettings(id=1)
        db.add(user_settings)

    user_settings.google_oauth_token = encrypt(creds.to_json())
    await db.commit()
    return {"status": "connected"}


@router.get("/status")
async def calendar_status(db: AsyncSession = Depends(get_db)):
    creds = await get_credentials(db)
    return {"connected": creds is not None and creds.valid}


@router.post("/sync")
async def trigger_sync(db: AsyncSession = Depends(get_db)):
    await sync_pending_events(db)
    return {"status": "sync_triggered"}


@router.get("/events")
async def list_events(limit: int = 50, offset: int = 0, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(CalendarEvent).order_by(CalendarEvent.start_time.asc()).limit(limit).offset(offset)
    )
    events = result.scalars().all()
    return [
        {
            "id": str(e.id),
            "task_id": str(e.task_id) if e.task_id else None,
            "google_event_id": e.google_event_id,
            "title": e.title,
            "start_time": e.start_time.isoformat(),
            "end_time": e.end_time.isoformat(),
            "location": e.location,
            "sync_status": e.sync_status,
        }
        for e in events
    ]
