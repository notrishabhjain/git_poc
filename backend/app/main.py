import asyncio
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.db.session import Base, engine
from app.engine.reminder_engine import run_reminder_loop
from app.engine.sync_engine import run_calendar_sync_loop

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def startup():
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created/verified")

    # Start background engines as async tasks
    asyncio.create_task(run_reminder_loop())
    asyncio.create_task(run_calendar_sync_loop())
    logger.info("Background engines started")


async def shutdown():
    await engine.dispose()


app = FastAPI(
    title="WhatsApp AI Assistant",
    version="0.1.0",
    description="AI-powered WhatsApp message processor with task management",
    on_startup=[startup],
    on_shutdown=[shutdown],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
