from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.message_service import get_messages

router = APIRouter(prefix="/messages", tags=["messages"])


@router.get("")
async def list_messages(
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    return await get_messages(db, limit=limit, offset=offset)
