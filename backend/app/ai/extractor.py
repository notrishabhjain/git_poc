import json
import logging
from datetime import datetime

from app.ai.prompts import EXTRACTOR_SYSTEM
from app.ai.provider import Provider, chat_with_fallback
from app.ai.schemas import INTENT_TOOL_MAP
from app.utils.datetime_utils import now_local

logger = logging.getLogger(__name__)


async def extract_entities(
    body: str,
    intent: str,
    sender_name: str,
) -> dict | None:
    """Extract structured entities for the given intent. Returns None if no tool available."""
    tool = INTENT_TOOL_MAP.get(intent)
    if tool is None:
        return None

    today = now_local().strftime("%Y-%m-%d %H:%M %Z")
    messages = [
        {"role": "system", "content": EXTRACTOR_SYSTEM.format(today=today)},
        {
            "role": "user",
            "content": f"Sender: {sender_name}\n\nMessage: {body}\n\nExtract the details using the provided function.",
        },
    ]

    try:
        # Prefer NVIDIA for larger model quality on extraction
        _, response = await chat_with_fallback(
            messages=messages,
            tools=[tool],
            tool_choice={"type": "function", "function": {"name": tool["function"]["name"]}},
            prefer_provider=Provider.NVIDIA,
            temperature=0.0,
        )
        choice = response.choices[0]
        if choice.message.tool_calls:
            args_str = choice.message.tool_calls[0].function.arguments
            return json.loads(args_str)
        # Fallback: try to parse content as JSON
        content = choice.message.content or "{}"
        return json.loads(content)
    except Exception as e:
        logger.error(f"Extraction failed for intent={intent}: {e}")
        return None


def compute_priority_score(priority: str, urgency: str | None = None) -> int:
    """Convert qualitative priority to 0-100 score."""
    base = {"low": 20, "medium": 50, "high": 75, "critical": 95}.get(priority, 50)
    urgency_bonus = {"low": 0, "medium": 5, "high": 15, "critical": 25}.get(urgency or "medium", 0)
    return min(100, base + urgency_bonus)
