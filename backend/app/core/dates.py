"""Small shared helpers."""
from datetime import datetime, timezone


def utcnow() -> str:
    """ISO-8601 UTC timestamp, e.g. 2026-10-15T19:00:00Z."""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
