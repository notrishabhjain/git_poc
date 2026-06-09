"""Core AI pipeline: prefilter → classify → extract → act."""
import json
import logging
import uuid
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.classifier import classify_message
from app.ai.extractor import compute_priority_score, extract_entities
from app.ai.prefilter import should_process
from app.ai.voice import transcribe_audio
from app.models.message import Message
from app.models.task import Task
from app.models.reminder import Reminder
from app.utils.datetime_utils import parse_relative_date, to_utc

logger = logging.getLogger(__name__)

# Intents that result in task creation
ACTIONABLE_INTENTS = {"meeting_request", "deadline", "follow_up", "reminder", "task"}


async def process_message(
    message: Message,
    body_plaintext: str,
    sender_name: str,
    db: AsyncSession,
    audio_bytes: bytes | None = None,
) -> dict:
    """Run the full pipeline for one message. Returns a summary dict."""

    # Step 1: Pre-filter
    ok, reason = should_process(
        body=body_plaintext,
        direction=message.direction,
        message_type=message.message_type,
        is_group=message.is_group_message,
    )
    if not ok:
        message.ai_processed = True
        message.ai_intent = "skipped"
        await db.commit()
        return {"action": "skipped", "reason": reason}

    # Step 1.5: Voice transcription
    if message.message_type == "voice" and audio_bytes:
        transcript = await transcribe_audio(audio_bytes)
        if transcript:
            body_plaintext = transcript
            message.voice_transcript = transcript

    # Step 2: Classify
    classification = await classify_message(
        body=body_plaintext,
        sender_name=sender_name,
        is_group=message.is_group_message,
    )
    message.ai_intent = classification.intent
    message.ai_category = classification.category
    message.ai_confidence = classification.confidence

    # Low confidence → flag for manual review
    if classification.confidence < 0.7:
        message.needs_review = True
        message.ai_processed = True
        await db.commit()
        return {
            "action": "flagged_for_review",
            "intent": classification.intent,
            "confidence": classification.confidence,
        }

    # Non-actionable intents → mark processed, no task
    if classification.intent not in ACTIONABLE_INTENTS:
        message.ai_processed = True
        await db.commit()
        return {"action": "no_action", "intent": classification.intent}

    # Step 3: Extract entities
    entities = await extract_entities(
        body=body_plaintext,
        intent=classification.intent,
        sender_name=sender_name,
    )

    # Step 4: Create task
    task = await _create_task(
        message=message,
        classification=classification,
        entities=entities,
        db=db,
    )

    # Step 5: Create reminder if applicable
    reminder = None
    if task and task.due_date:
        reminder = await _create_reminder(task=task, entities=entities, db=db)

    message.ai_processed = True
    await db.commit()

    logger.info(f"Pipeline complete for message {message.id}: task={task.id if task else None}")
    return {
        "action": "task_created",
        "task_id": str(task.id) if task else None,
        "reminder_id": str(reminder.id) if reminder else None,
        "intent": classification.intent,
        "category": classification.category,
    }


async def _create_task(
    message: Message,
    classification,
    entities: dict | None,
    db: AsyncSession,
) -> Task | None:
    if not entities:
        # Create a minimal task from classification alone
        title = f"Action from {message.push_name or 'WhatsApp'}"
        priority = "medium"
        due_date = None
    else:
        title = entities.get("title", f"Task from {message.push_name or 'WhatsApp'}")
        priority = entities.get("priority", "medium")
        due_date_str = entities.get("due_date") or entities.get("remind_at") or entities.get("proposed_date")
        due_date = parse_relative_date(due_date_str) if due_date_str else None
        if due_date:
            due_date = to_utc(due_date)

    task = Task(
        source_message_id=message.id,
        title=title,
        description=entities.get("description") or entities.get("agenda") or entities.get("context") if entities else None,
        category=classification.category,
        intent=classification.intent,
        status="pending",
        priority_score=compute_priority_score(priority),
        urgency=priority,
        importance=priority,
        due_date=due_date,
        due_date_flexible=entities.get("due_date_flexible", True) if entities else True,
        context_summary=classification.reasoning,
        tags_json=json.dumps(entities.get("tags")) if entities and entities.get("tags") else None,
    )
    db.add(task)
    await db.flush()  # get task.id without committing
    return task


async def _create_reminder(task: Task, entities: dict | None, db: AsyncSession) -> Reminder | None:
    if not task.due_date:
        return None

    from datetime import timedelta
    # Default: remind 30 minutes before due date, or at due time for reminders
    if task.intent == "reminder":
        remind_at = task.due_date
    else:
        remind_at = task.due_date - timedelta(hours=1)

    reminder = Reminder(
        task_id=task.id,
        title=f"Reminder: {task.title}",
        remind_at=remind_at,
        recurrence_rule=entities.get("recurrence") if entities else None,
        escalation_action="notify",
    )
    db.add(reminder)
    await db.flush()
    return reminder
