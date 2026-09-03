"""Deterministic design helpers for the minimal NMI sensitivity panel."""

from __future__ import annotations

import hashlib

PANEL_SALT = "NMI-MIN-SENS-V1|outcome-blind|sha256-rank|2026-09-03"


def select_panel_seeds(
    source_seeds: list[int], count: int, *, salt: str = PANEL_SALT
) -> list[int]:
    """Select seeds by an outcome-blind salted SHA-256 rank."""
    if count < 1 or count > len(source_seeds):
        raise ValueError("count must be between one and the number of source seeds")
    if len(source_seeds) != len(set(source_seeds)):
        raise ValueError("source seeds must be unique")
    ranked = sorted(
        source_seeds,
        key=lambda seed: (hashlib.sha256(f"{salt}|{seed}".encode()).hexdigest(), seed),
    )
    return ranked[:count]
