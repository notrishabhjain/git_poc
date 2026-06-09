import logging

from openai import AsyncOpenAI

from app.config import settings

logger = logging.getLogger(__name__)


async def transcribe_audio(audio_bytes: bytes, filename: str = "audio.ogg") -> str | None:
    """Transcribe voice note using Groq's free Whisper endpoint."""
    if not settings.groq_api_key:
        logger.warning("GROQ_API_KEY not set; skipping voice transcription")
        return None

    client = AsyncOpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=settings.groq_api_key,
    )
    try:
        import io
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = filename
        response = await client.audio.transcriptions.create(
            model=settings.whisper_model,
            file=audio_file,
            response_format="text",
        )
        return str(response).strip()
    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        return None
