"""OpenAI-compatible tool-use schemas for each intent type."""

MEETING_TOOL = {
    "type": "function",
    "function": {
        "name": "create_meeting",
        "description": "Extract meeting/call details from the message",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Brief meeting title"},
                "proposed_date": {"type": "string", "description": "ISO 8601 date or null"},
                "proposed_time": {"type": "string", "description": "ISO 8601 time (HH:MM) or null"},
                "duration_minutes": {"type": "integer", "default": 60},
                "location": {"type": "string", "description": "Physical or virtual location, or null"},
                "attendees": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "role": {"type": "string", "enum": ["organizer", "required", "optional"]},
                        },
                        "required": ["name"],
                    },
                },
                "agenda": {"type": "string", "description": "Meeting agenda or purpose, or null"},
                "priority": {"type": "string", "enum": ["low", "medium", "high", "critical"]},
                "needs_scheduling": {
                    "type": "boolean",
                    "description": "True if date/time is not yet confirmed",
                },
            },
            "required": ["title", "priority", "needs_scheduling"],
        },
    },
}

TASK_TOOL = {
    "type": "function",
    "function": {
        "name": "create_task",
        "description": "Extract a general task or action item from the message",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Clear, actionable task title"},
                "description": {"type": "string", "description": "Additional context, or null"},
                "due_date": {"type": "string", "description": "ISO 8601 datetime or null"},
                "due_date_flexible": {"type": "boolean", "description": "Is the due date approximate?"},
                "priority": {"type": "string", "enum": ["low", "medium", "high", "critical"]},
                "tags": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["title", "priority"],
        },
    },
}

DEADLINE_TOOL = {
    "type": "function",
    "function": {
        "name": "create_deadline",
        "description": "Extract a deadline or submission requirement from the message",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "deliverable": {"type": "string", "description": "What needs to be submitted/done"},
                "due_date": {"type": "string", "description": "ISO 8601 datetime"},
                "priority": {"type": "string", "enum": ["low", "medium", "high", "critical"]},
                "flexibility": {
                    "type": "string",
                    "enum": ["hard", "soft"],
                    "description": "hard=firm deadline, soft=approximate",
                },
            },
            "required": ["title", "due_date", "priority"],
        },
    },
}

REMINDER_TOOL = {
    "type": "function",
    "function": {
        "name": "create_reminder",
        "description": "Extract a reminder request from the message",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "remind_at": {"type": "string", "description": "ISO 8601 datetime when to remind"},
                "recurrence": {
                    "type": "string",
                    "description": "iCal RRULE string if recurring, else null",
                },
                "context": {"type": "string", "description": "Why this reminder exists"},
            },
            "required": ["title", "remind_at"],
        },
    },
}

FOLLOW_UP_TOOL = {
    "type": "function",
    "function": {
        "name": "create_follow_up",
        "description": "Extract a follow-up action from the message",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "original_topic": {"type": "string"},
                "follow_up_with": {"type": "string", "description": "Person or team to follow up with"},
                "deadline": {"type": "string", "description": "ISO 8601 datetime by when to follow up"},
                "escalation_date": {
                    "type": "string",
                    "description": "ISO 8601 datetime after which to escalate",
                },
            },
            "required": ["title", "follow_up_with"],
        },
    },
}

INTENT_TOOL_MAP: dict[str, dict] = {
    "meeting_request": MEETING_TOOL,
    "deadline": DEADLINE_TOOL,
    "reminder": REMINDER_TOOL,
    "task": TASK_TOOL,
    "follow_up": FOLLOW_UP_TOOL,
}
