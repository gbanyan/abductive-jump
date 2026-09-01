from __future__ import annotations

from dataclasses import dataclass


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

