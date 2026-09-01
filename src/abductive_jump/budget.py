from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class BudgetLimit:
    llm_tokens: int
    llm_calls: int
    candidate_evaluations: int
    interventions: int


@dataclass(slots=True)
class BudgetAccount:
    limit: BudgetLimit
    llm_tokens: int = 0
    llm_calls: int = 0
    candidate_evaluations: int = 0
    interventions: int = 0

    @property
    def used(self) -> BudgetLimit:
        return BudgetLimit(
            self.llm_tokens,
            self.llm_calls,
            self.candidate_evaluations,
            self.interventions,
        )

    @property
    def remaining(self) -> BudgetLimit:
        return BudgetLimit(
            self.limit.llm_tokens - self.llm_tokens,
            self.limit.llm_calls - self.llm_calls,
            self.limit.candidate_evaluations - self.candidate_evaluations,
            self.limit.interventions - self.interventions,
        )

    def canonical_dict(self) -> dict[str, dict[str, int]]:
        def payload(value: BudgetLimit) -> dict[str, int]:
            return {
                "llm_tokens": value.llm_tokens,
                "llm_calls": value.llm_calls,
                "candidate_evaluations": value.candidate_evaluations,
                "interventions": value.interventions,
            }

        return {"limit": payload(self.limit), "used": payload(self.used), "remaining": payload(self.remaining)}

    def charge(self, *, llm_tokens: int = 0, llm_calls: int = 0, candidate_evaluations: int = 0, interventions: int = 0) -> None:
        values = (llm_tokens, llm_calls, candidate_evaluations, interventions)
        if any(v < 0 for v in values):
            raise ValueError("budget charges must be non-negative")
        proposed = (
            self.llm_tokens + llm_tokens,
            self.llm_calls + llm_calls,
            self.candidate_evaluations + candidate_evaluations,
            self.interventions + interventions,
        )
        ceilings = (self.limit.llm_tokens, self.limit.llm_calls, self.limit.candidate_evaluations, self.limit.interventions)
        if any(actual > ceiling for actual, ceiling in zip(proposed, ceilings)):
            raise BudgetExceeded(f"charge {proposed} exceeds {ceilings}")
        self.llm_tokens, self.llm_calls, self.candidate_evaluations, self.interventions = proposed


class BudgetExceeded(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class EqualBudgetContract:
    """A preregistrable per-world resource envelope shared by all conditions.

    Token matching is by generated-token *capacity*. Actual generated tokens are
    retained separately and must be reported; a method may not spend unused
    capacity on extra calls, candidates, or interventions.
    """

    candidate_slots: int
    calls_per_slot: int
    max_completion_tokens_per_call: int
    interventions_per_candidate: int = 1

    def __post_init__(self) -> None:
        if min(
            self.candidate_slots,
            self.calls_per_slot,
            self.max_completion_tokens_per_call,
            self.interventions_per_candidate,
        ) <= 0:
            raise ValueError("all equal-budget dimensions must be positive")

    @property
    def limit(self) -> BudgetLimit:
        return BudgetLimit(
            llm_tokens=(
                self.candidate_slots
                * self.calls_per_slot
                * self.max_completion_tokens_per_call
            ),
            llm_calls=self.candidate_slots * self.calls_per_slot,
            candidate_evaluations=self.candidate_slots,
            interventions=self.candidate_slots * self.interventions_per_candidate,
        )

    def canonical_dict(self) -> dict[str, Any]:
        return {
            "candidate_slots": self.candidate_slots,
            "calls_per_slot": self.calls_per_slot,
            "max_completion_tokens_per_call": self.max_completion_tokens_per_call,
            "interventions_per_candidate": self.interventions_per_candidate,
            "derived_limit": {
                "llm_tokens": self.limit.llm_tokens,
                "llm_calls": self.limit.llm_calls,
                "candidate_evaluations": self.limit.candidate_evaluations,
                "interventions": self.limit.interventions,
            },
        }
