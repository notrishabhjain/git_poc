"""Google Calendar integration with OAuth2."""
import json
import logging
from datetime import datetime, timedelta

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.calendar_event import CalendarEvent
from app.models.user_settings import UserSettings
from app.utils.crypto import decrypt, encrypt

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/calendar.events"]


def get_oauth_flow() -> Flow:
    client_config = {
        "web": {
            "client_id": settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [settings.google_redirect_uri],
        }
    }
    flow = Flow.from_client_config(client_config, scopes=SCOPES)
    flow.redirect_uri = settings.google_redirect_uri
    return flow


async def get_credentials(db: AsyncSession) -> Credentials | None:
    result = await db.execute(select(UserSettings).where(UserSettings.id == 1))
    user_settings = result.scalar_one_or_none()
    if not user_settings or not user_settings.google_oauth_token:
        return None

    token_json = decrypt(user_settings.google_oauth_token)
    creds = Credentials.from_authorized_user_info(json.loads(token_json), SCOPES)

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        await _save_credentials(db, creds, user_settings)

    return creds if creds.valid else None


async def _save_credentials(db: AsyncSession, creds: Credentials, user_settings: UserSettings):
    token_json = creds.to_json()
    user_settings.google_oauth_token = encrypt(token_json)
    await db.commit()


async def sync_pending_events(db: AsyncSession):
    """Push all pending calendar events to Google Calendar."""
    creds = await get_credentials(db)
    if not creds:
        logger.warning("Google Calendar not connected; skipping sync")
        return

    service = build("calendar", "v3", credentials=creds)
    result = await db.execute(
        select(CalendarEvent).where(CalendarEvent.sync_status == "pending")
    )
    events = result.scalars().all()

    for event in events:
        try:
            body = {
                "summary": event.title,
                "description": event.description or "",
                "start": {"dateTime": event.start_time.isoformat(), "timeZone": settings.timezone},
                "end": {"dateTime": event.end_time.isoformat(), "timeZone": settings.timezone},
            }
            if event.location:
                body["location"] = event.location
            if event.attendees_json:
                body["attendees"] = event.attendees_json

            if event.google_event_id:
                service.events().update(
                    calendarId="primary", eventId=event.google_event_id, body=body
                ).execute()
            else:
                created = service.events().insert(calendarId="primary", body=body).execute()
                event.google_event_id = created["id"]

            event.sync_status = "synced"
            event.last_synced_at = datetime.utcnow()
        except Exception as e:
            logger.error(f"Failed to sync event {event.id}: {e}")
            event.sync_status = "failed"

    await db.commit()
