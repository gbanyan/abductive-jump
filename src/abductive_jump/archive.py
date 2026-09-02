from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from dataclasses import dataclass, field

from .representation import Representation, structural_descriptor
from .worlds import Candidate


@dataclass(frozen=True, slots=True)
class ArchiveEntry:
    candidate: Candidate
    observed_loss: float
    ancestry: tuple[str, ...] = ()
    prediction_signature: tuple[int, ...] = ()

    @property
    def descriptor(self) -> tuple[tuple[str, int], ...]:
        base = dict(structural_descriptor(self.candidate.representation))
        base["ancestry_depth"] = len(self.ancestry)
        base["prediction_signature_hash"] = int(
            hashlib.sha256(
                json.dumps(self.prediction_signature, separators=(",", ":")).encode()
            ).hexdigest()[:16],
            16,
        )
        return tuple(sorted(base.items()))


@dataclass(slots=True)
class QualityDiversityArchive:
    """One best observed-fit candidate per entirely structural descriptor bin."""

    bins: dict[tuple[tuple[str, int], ...], ArchiveEntry] = field(default_factory=dict)

    def offer(self, entry: ArchiveEntry) -> bool:
        previous = self.bins.get(entry.descriptor)
        if previous is None or (entry.observed_loss, entry.candidate.candidate_hash) < (
            previous.observed_loss,
            previous.candidate.candidate_hash,
        ):
            self.bins[entry.descriptor] = entry
            return True
        return False

    @property
    def occupancy(self) -> int:
        return len(self.bins)

    def snapshot(self) -> Mapping[tuple[tuple[str, int], ...], ArchiveEntry]:
        return dict(self.bins)


@dataclass(frozen=True, slots=True)
class TheoryArchiveEntry:
    representation: Representation
    theory_hash: str
    observed_loss: float
    ancestry: tuple[str, ...] = ()
    prediction_signature: tuple[int, ...] = ()

    @property
    def descriptor(self) -> tuple[tuple[str, int], ...]:
        base = dict(structural_descriptor(self.representation))
        base["ancestry_depth"] = len(self.ancestry)
        base["prediction_signature_hash"] = int(
            hashlib.sha256(
                json.dumps(self.prediction_signature, separators=(",", ":")).encode()
            ).hexdigest()[:16],
            16,
        )
        return tuple(sorted(base.items()))


@dataclass(slots=True)
class TheoryQualityDiversityArchive:
    bins: dict[tuple[tuple[str, int], ...], TheoryArchiveEntry] = field(
        default_factory=dict
    )

    def offer(self, entry: TheoryArchiveEntry) -> bool:
        previous = self.bins.get(entry.descriptor)
        if previous is None or (entry.observed_loss, entry.theory_hash) < (
            previous.observed_loss,
            previous.theory_hash,
        ):
            self.bins[entry.descriptor] = entry
            return True
        return False

    @property
    def occupancy(self) -> int:
        return len(self.bins)

    def snapshot(
        self,
    ) -> Mapping[tuple[tuple[str, int], ...], TheoryArchiveEntry]:
        return dict(self.bins)
