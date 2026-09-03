"""Helpers for auditing frozen historical model outputs."""

from __future__ import annotations

import json
from typing import Any


def strict_json_object(text: str) -> dict[str, Any] | None:
    """Parse the entire answer, apart from an optional Markdown fence."""
    stripped = text.strip()
    if stripped.startswith("```"):
        parts = stripped.split("\n", 1)
        stripped = parts[1] if len(parts) == 2 else ""
        if stripped.endswith("```"):
            stripped = stripped[:-3].rstrip()
    try:
        value = json.loads(stripped)
    except json.JSONDecodeError:
        return None
    return value if isinstance(value, dict) else None
