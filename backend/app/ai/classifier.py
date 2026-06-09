import json
import logging

from app.ai.prompts import CLASSIFIER_SYSTEM, CLASSIFIER_USER
from app.ai.provider import Provider, chat_with_fallback

logger = logging.getLogger(__name__)


class ClassificationResult:
    def __init__(self, intent: str, category: str, confidence: float, reasoning: str):
        self.intent = intent
        self.category = category
        self.confidence = confidence
        self.reasoning = reasoning

    def __repr__(self):
        return f"<Classification intent={self.intent} category={self.category} conf={self.confidence:.2f}>"


VALID_INTENTS = {
    "meeting_request", "deadline", "follow_up", "reminder", "task",
    "question", "fyi_no_action", "social", "spam",
}
VALID_CATEGORIES = {"work", "personal", "family", "friends"}


async def classify_message(
    body: str,
    sender_name: str,
    is_group: bool,
) -> ClassificationResult:
    chat_type = "group chat" if is_group else "private chat"
    messages = [
        {"role": "system", "content": CLASSIFIER_SYSTEM},
        {
            "role": "user",
            "content": CLASSIFIER_USER.format(
                sender_name=sender_name,
                chat_type=chat_type,
                message_body=body,
            ),
        },
    ]

    try:
        _, response = await chat_with_fallback(
            messages=messages,
            prefer_provider=Provider.GROQ,
            temperature=0.0,
        )
        content = response.choices[0].message.content or "{}"
        # Strip markdown code fences if present
        content = content.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        data = json.loads(content)

        intent = data.get("intent", "fyi_no_action")
        if intent not in VALID_INTENTS:
            intent = "fyi_no_action"

        category = data.get("category", "personal")
        if category not in VALID_CATEGORIES:
            category = "personal"

        return ClassificationResult(
            intent=intent,
            category=category,
            confidence=float(data.get("confidence", 0.5)),
            reasoning=data.get("reasoning", ""),
        )
    except Exception as e:
        logger.error(f"Classification failed: {e}")
        return ClassificationResult(
            intent="fyi_no_action",
            category="personal",
            confidence=0.0,
            reasoning=f"Classification error: {e}",
        )
