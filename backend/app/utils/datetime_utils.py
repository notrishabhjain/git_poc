from datetime import datetime

import pytz
from dateutil import parser as dateutil_parser

from app.config import settings


def get_timezone():
    return pytz.timezone(settings.timezone)


def now_local() -> datetime:
    return datetime.now(get_timezone())


def parse_relative_date(date_str: str, reference: datetime | None = None) -> datetime | None:
    """Parse date strings like 'tomorrow', 'next Tuesday', ISO strings, etc."""
    if not date_str:
        return None
    ref = reference or now_local()
    try:
        return dateutil_parser.parse(date_str, default=ref)
    except (ValueError, OverflowError):
        return None


def to_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        local_tz = get_timezone()
        dt = local_tz.localize(dt)
    return dt.astimezone(pytz.utc)
