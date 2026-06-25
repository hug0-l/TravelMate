"""Utility helpers for TravelMate."""

import html
from typing import Any


def sanitize(value: str | None) -> str | None:
    """Strip HTML tags and escape special characters to prevent XSS."""
    if value is None:
        return None
    return html.escape(value.strip(), quote=True)


def sanitize_dict(data: dict[str, Any], fields: list[str]) -> dict[str, Any]:
    """Sanitize specific fields in a dict."""
    sanitized = {}
    for key, val in data.items():
        if key in fields and isinstance(val, str):
            sanitized[key] = sanitize(val)
        else:
            sanitized[key] = val
    return sanitized