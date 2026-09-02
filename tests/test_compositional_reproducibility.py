from pathlib import Path

import pytest

from abductive_jump import compositional_reproducibility as reproducibility


def _write(root: Path, name: str, text: str = "evidence\n") -> None:
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def test_required_outputs_reject_pending_audit(tmp_path: Path, monkeypatch) -> None:
    names = (
        "reports/compositional-completion-audit.md",
        "reports/figures/compositional/figure.svg",
    )
    monkeypatch.setattr(reproducibility, "REQUIRED", names)
    _write(tmp_path, names[0], "| requirement | PENDING |\n")
    _write(tmp_path, names[1], "<svg></svg>\n")

    with pytest.raises(ValueError, match="still contains PENDING"):
        reproducibility._validate_required_outputs(tmp_path)


def test_required_outputs_reject_invalid_svg(tmp_path: Path, monkeypatch) -> None:
    names = (
        "reports/compositional-completion-audit.md",
        "reports/figures/compositional/figure.svg",
    )
    monkeypatch.setattr(reproducibility, "REQUIRED", names)
    _write(tmp_path, names[0], "| requirement | COMPLETE |\n")
    _write(tmp_path, names[1], "not svg\n")

    with pytest.raises(ValueError, match="invalid SVG"):
        reproducibility._validate_required_outputs(tmp_path)
