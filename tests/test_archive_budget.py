import pytest

from abductive_jump.archive import ArchiveEntry, QualityDiversityArchive
from abductive_jump.budget import BudgetAccount, BudgetExceeded, BudgetLimit
from abductive_jump.worlds import generate_world


def test_archive_uses_structural_bins_and_keeps_best_fit():
    candidate = generate_world("state_invention", 1).truth
    archive = QualityDiversityArchive()
    assert archive.offer(ArchiveEntry(candidate, 2.0, ("a",), (1, 0)))
    assert archive.offer(ArchiveEntry(candidate, 1.0, ("a",), (1, 0)))
    assert not archive.offer(ArchiveEntry(candidate, 3.0, ("a",), (1, 0)))
    assert archive.occupancy == 1


def test_budget_is_atomic_and_enforces_every_primary_dimension():
    account = BudgetAccount(BudgetLimit(100, 2, 3, 1))
    account.charge(llm_tokens=90, llm_calls=1, candidate_evaluations=2, interventions=1)
    with pytest.raises(BudgetExceeded):
        account.charge(llm_tokens=11)
    assert account.llm_tokens == 90
    with pytest.raises(ValueError):
        account.charge(llm_tokens=-1)

