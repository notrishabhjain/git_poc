"""Heuristic pre-filter to skip messages that don't need AI processing.
Saves ~60% of API calls by skipping obviously non-actionable messages.
"""
import re

# Short social phrases that don't need processing
_SOCIAL_PATTERNS = re.compile(
    r"^(ok|okay|thanks|thank you|thx|👍|🙏|😊|lol|haha|nice|cool|sure|yes|no|hmm|k|np|yep|nope|got it)\.?$",
    re.IGNORECASE,
)

# Minimum meaningful message length
_MIN_LENGTH = 10

# Intents that should always be processed regardless of other filters
_ALWAYS_PROCESS_KEYWORDS = re.compile(
    r"\b(meet|meeting|call|reminder|remind|tomorrow|deadline|due|urgent|asap|schedule|"
    r"follow.?up|action|task|review|submit|send|complete|finish|discuss|plan|arrange)\b",
    re.IGNORECASE,
)


def should_process(
    body: str,
    direction: str,
    message_type: str,
    is_group: bool,
) -> tuple[bool, str]:
    """Return (should_process, reason)."""
    # Never process outbound messages (your own)
    if direction == "outbound":
        return False, "outbound"

    # Skip media-only messages with no text
    if message_type in ("image", "video", "sticker", "reaction") and not body:
        return False, "media_no_caption"

    # Always process voice notes (will be transcribed)
    if message_type == "voice":
        return True, "voice_note"

    body_stripped = body.strip()

    # Skip empty messages
    if not body_stripped:
        return False, "empty"

    # Skip forwarded spam (usually long chains)
    if body_stripped.startswith("Forwarded") and len(body_stripped) > 500:
        return False, "forwarded_spam"

    # If message mentions action keywords, always process regardless of length
    if _ALWAYS_PROCESS_KEYWORDS.search(body_stripped):
        return True, "action_keyword"

    # Skip very short messages
    if len(body_stripped) < _MIN_LENGTH:
        return False, "too_short"

    # Skip obvious social chatter
    if _SOCIAL_PATTERNS.match(body_stripped):
        return False, "social"

    return True, "passed"
