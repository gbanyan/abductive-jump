"""Outcome-neutral helpers for fair-interface publication tables."""

from __future__ import annotations

from typing import Any


def paired_row(
    reference_name: str,
    reference: dict[tuple[str, int], bool],
    comparison_name: str,
    comparison: dict[tuple[str, int], bool],
) -> dict[str, Any]:
    if reference.keys() != comparison.keys():
        raise ValueError(f"paired panels differ: {reference_name} versus {comparison_name}")
    pairs = [(reference[key], comparison[key]) for key in sorted(reference)]
    return {
        "worlds": len(pairs),
        "both_fail": sum(not old and not new for old, new in pairs),
        "both_succeed": sum(old and new for old, new in pairs),
        "comparison_only_success": sum(not old and new for old, new in pairs),
        "reference_only_success": sum(old and not new for old, new in pairs),
        "paired_jsr_difference": (
            sum(new for _, new in pairs) - sum(old for old, _ in pairs)
        )
        / len(pairs),
        "reference": reference_name,
        "comparison": comparison_name,
    }
