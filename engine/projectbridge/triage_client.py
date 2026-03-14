"""Fire-and-forget event emitter for the triage companion service.

Sends operational events (errors, warnings, developer notes) to the
triage service for async classification and GitHub issue creation.
If the triage service is unavailable, events are silently dropped.
"""

from __future__ import annotations

import logging
import traceback
from datetime import datetime, timezone

import requests

logger = logging.getLogger(__name__)

TRIAGE_URL = "http://localhost:4000/api/events"


def emit_triage_event(
    source_type: str,
    message: str,
    *,
    stack_trace: str | None = None,
    stage: str | None = None,
    extra: dict | None = None,
) -> None:
    """Send an event to the triage companion service (fire-and-forget).

    Args:
        source_type: One of 'application_error', 'validation_warning',
                     or 'developer_note'.
        message: Human-readable description of the event.
        stack_trace: Optional stack trace string.
        stage: Pipeline stage where the event originated.
        extra: Additional metadata to include.
    """
    payload = {
        "sourceType": source_type,
        "project": "project-bridge",
        "environment": "development",
        "message": message,
        "stackTrace": stack_trace,
        "metadata": {"stage": stage, **(extra or {})},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    try:
        resp = requests.post(TRIAGE_URL, json=payload, timeout=3)
        logger.debug("Triage event sent: %s", resp.status_code)
    except requests.RequestException:
        logger.debug("Triage service unavailable, skipping")


def emit_pipeline_error(stage: str, exc: Exception) -> None:
    """Convenience wrapper for pipeline errors."""
    emit_triage_event(
        "application_error",
        str(exc),
        stack_trace=traceback.format_exc(),
        stage=stage,
    )


def emit_validation_warning(message: str, *, stage: str = "validation") -> None:
    """Convenience wrapper for validation warnings."""
    emit_triage_event(
        "validation_warning",
        message,
        stage=stage,
    )
