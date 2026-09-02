from pathlib import Path

from abductive_jump.compositional_replay import replay_run


def test_corrected_pilot_replays_without_mismatch():
    root = Path(__file__).resolve().parents[1]
    candidates, ancestry, mismatches = replay_run(
        root / "configs" / "compositional-pilot-existing.json",
        root / "artifacts" / "compositional" / "pilot-existing-corrected",
    )
    assert len(candidates) == 168
    assert ancestry
    assert mismatches == []
