#!/usr/bin/env python3
"""Build and verify an upload-ready NMI reviewer archive.

The archive contains the clean tracked repository plus explicitly enumerated
large historical call ledgers and superseded/partial extension records that
are intentionally excluded from Git. Model weights are never included.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import subprocess
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "output" / "archive"

HISTORICAL_CALL_LEDGERS = [
    "artifacts/confirmatory/ablation-a6-control/llm_calls.jsonl",
    "artifacts/confirmatory/ablation-a6-jump/llm_calls.jsonl",
    "artifacts/confirmatory/factorial-control/llm_calls.jsonl",
    "artifacts/confirmatory/factorial-jump/llm_calls.jsonl",
    "artifacts/confirmatory/primary-control/llm_calls.jsonl",
    "artifacts/confirmatory/primary-jump/llm_calls.jsonl",
    "artifacts/compositional/confirmatory-existing-control/llm_calls.jsonl",
    "artifacts/compositional/confirmatory-existing/llm_calls.jsonl",
    "artifacts/compositional/confirmatory-heldout-control/llm_calls.jsonl",
    "artifacts/compositional/confirmatory-heldout/llm_calls.jsonl",
]

SUPERSEDED_COMPLETE_DIRS = [
    "experiments/nmi_extension_v1/results/deepseek_matched/known_jump",
    "experiments/nmi_extension_v1/results/deepseek_matched/heldout_jump",
    "experiments/nmi_extension_v1/results/phi_constrained/known_jump",
    "experiments/nmi_extension_v1/results/phi_constrained/heldout_jump",
    "experiments/nmi_extension_v1/results/phi_repair/known_jump",
    "experiments/nmi_extension_v1/results/phi_repair/heldout_jump",
]

UNTRACKED_PARTIAL_DIRS = [
    "experiments/nmi_extension_v1/results/deepseek_native/known_jump",
    "experiments/nmi_extension_v1/results/phi_budget/known_control",
]


def run_git(*args: str) -> bytes:
    return subprocess.check_output(["git", *args], cwd=ROOT)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def require_clean_tracked_tree() -> None:
    subprocess.run(["git", "diff", "--quiet"], cwd=ROOT, check=True)
    subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=ROOT, check=True)


def tracked_files() -> list[str]:
    return sorted(item.decode() for item in run_git("ls-files", "-z").split(b"\0") if item)


def expanded_extra_files() -> list[str]:
    paths = list(HISTORICAL_CALL_LEDGERS)
    for directory in [*SUPERSEDED_COMPLETE_DIRS, *UNTRACKED_PARTIAL_DIRS]:
        base = ROOT / directory
        if not base.is_dir():
            raise FileNotFoundError(f"required archive directory missing: {directory}")
        paths.extend(
            str(path.relative_to(ROOT))
            for path in sorted(base.rglob("*"))
            if path.is_file() and path.name != ".DS_Store"
        )
    missing = [path for path in paths if not (ROOT / path).is_file()]
    if missing:
        raise FileNotFoundError(f"required archive files missing: {missing}")
    return sorted(set(paths))


def build() -> Path:
    require_clean_tracked_tree()
    commit = run_git("rev-parse", "HEAD").decode().strip()
    short = commit[:12]
    tracked = tracked_files()
    tracked_set = set(tracked)
    extras = [path for path in expanded_extra_files() if path not in tracked_set]
    records = []
    for provenance, paths in (("tracked", tracked), ("large-local-artifact", extras)):
        for relative in paths:
            path = ROOT / relative
            records.append(
                {
                    "path": relative,
                    "provenance": provenance,
                    "sha256": sha256(path),
                    "size_bytes": path.stat().st_size,
                }
            )
    manifest = {
        "schema_version": "nmi-reviewer-deposit-v1",
        "release_commit": commit,
        "historical_call_ledgers": HISTORICAL_CALL_LEDGERS,
        "superseded_complete_directories": SUPERSEDED_COMPLETE_DIRS,
        "partial_run_directories": [
            *UNTRACKED_PARTIAL_DIRS,
            "experiments/nmi_extension_v1/results/_incomplete/phi_budget/known_jump_attempt_001_executor_session_terminated",
        ],
        "model_weights_included": False,
        "files": records,
    }
    manifest_bytes = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    destination = OUTPUT_DIR / f"nmi-reviewer-deposit-{short}.tar.gz"
    prefix = f"novelty-seeking-agent-{short}"
    with tarfile.open(destination, "w:gz", compresslevel=6) as archive:
        for record in records:
            archive.add(
                ROOT / record["path"], arcname=f"{prefix}/{record['path']}", recursive=False
            )
        info = tarfile.TarInfo(f"{prefix}/ARCHIVE_MANIFEST.json")
        info.size = len(manifest_bytes)
        info.mode = 0o644
        archive.addfile(info, io.BytesIO(manifest_bytes))

    checksum = sha256(destination)
    destination.with_suffix(destination.suffix + ".sha256").write_text(
        f"{checksum}  {destination.name}\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "archive": str(destination),
                "archive_sha256": checksum,
                "files": len(records),
                "large_local_files": len(extras),
                "release_commit": commit,
                "size_bytes": destination.stat().st_size,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return destination


def verify(archive_path: Path) -> None:
    with tarfile.open(archive_path, "r:gz") as archive:
        manifest_member = next(
            member
            for member in archive.getmembers()
            if member.name.endswith("/ARCHIVE_MANIFEST.json")
        )
        manifest_handle = archive.extractfile(manifest_member)
        if manifest_handle is None:
            raise ValueError("manifest could not be read")
        manifest = json.load(manifest_handle)
        prefix = manifest_member.name.removesuffix("/ARCHIVE_MANIFEST.json")
        members = {member.name: member for member in archive.getmembers() if member.isfile()}
        for record in manifest["files"]:
            member = members.get(f"{prefix}/{record['path']}")
            if member is None:
                raise ValueError(f"archive member missing: {record['path']}")
            handle = archive.extractfile(member)
            if handle is None:
                raise ValueError(f"archive member unreadable: {record['path']}")
            digest = hashlib.sha256()
            while block := handle.read(1024 * 1024):
                digest.update(block)
            if digest.hexdigest() != record["sha256"] or member.size != record["size_bytes"]:
                raise ValueError(f"archive member mismatch: {record['path']}")
    print(
        json.dumps(
            {
                "archive": str(archive_path),
                "files_verified": len(manifest["files"]),
                "release_commit": manifest["release_commit"],
                "status": "complete_verified",
            },
            indent=2,
            sort_keys=True,
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    if args.verify:
        verify(args.verify.resolve())
    else:
        build()


if __name__ == "__main__":
    main()
