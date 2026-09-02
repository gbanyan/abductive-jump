# Publication consistency audit

Date: 2 September 2026

## Cross-document numerical checks

| Quantity | Canonical value | Manuscript | Figure plan | Audit result |
|---|---:|---:|---:|---|
| AJ5 B0/B1/B2/B3/B4/B5 successes | 1/1/0/0/142/142 of 400 | Match | Match | PASS |
| AJ5 controls | 0/200 per condition | Match | Summarized | PASS |
| AJ5 proposal factorial | 0/142/400 of 400 | Match | Match | PASS |
| AJ5 slot dose B4 | 53/101/142 | Match | Match | PASS |
| AJ5 slot dose B5 | 58/96/142 | Match | Match | PASS |
| CJ5 known C0/C1/C2/C3/C_self/C_rand/C5 | 0/131/0/400/0/52/400 | Match | Match | PASS |
| CJ5 held-out values | 0/0/0/100/0/13/100 | Match | Match | PASS |
| C3−C_rand known CI | 0.87 [0.845, 0.895] | Match | Implicit | PASS |
| C3−C_rand held-out CI | 0.87 [0.80, 0.93] | Match | Implicit | PASS |
| Retained gain rho | 3.053 [2.685, 3.540] | Match | Match | PASS |
| C3 combined controls | 0/300; upper 0.012643 | Match | Match | PASS |
| Depth-one alternatives | 0/17,280 | Match | Match | PASS |
| AJ5 replay | 10,800/10,800; 0 mismatch | Match | Match | PASS |
| CJ5 replay | 16,800/16,800; 0 mismatch | Match | Match | PASS |
| Calls | AJ5 32,400 + A6 3,600; CJ5 33,600 | Supplement only | Not main | PASS |
| Exclusions/reruns | 0/0 both phases | Match | Match | PASS |

## Terminology checks

- “Jump” is defined only through J0–J5 and otherwise qualified as bounded/registered: PASS.
- Depth is qualified as within the registered operator system: PASS.
- Held-out claim is structural-family generalization, not wholly novel ontology: PASS.
- Zero false jumps is accompanied by Wilson uncertainty: PASS.
- P2/C5 are described as conditional ceilings, not ordinary baselines: PASS.
- C1 operation semantics are not treated as compute equivalent to C3: PASS.
- Capability is attributed to the scaffold, not the LLM alone: PASS.

## Citation checks

- Citation ledger rows: 46.
- Main-text references: 34, within the approximate NMI guideline.
- Every broad Introduction/Discussion claim has a mapped citation class.
- Numerical results rely on project artifacts, not external citations.
- Remaining risk: some ledger records use “et al.” or “authors listed on record”; final reference-manager import and author-by-author verification are mandatory.

## Format checks

- Abstract target ≤150 words: current automated count is 150; recheck after any edit.
- Main text target ≤3,500 words excluding Methods/references/legends: current draft is within target when sections are counted correctly; recheck after author revision.
- Main displays: four figures plus one table, within six.
- Introduction has no heading; Results and Methods have topical subheadings; Discussion has no subheadings: PASS.
- Title 59 characters: PASS pending author approval.
- Figure legends/source data: PLANNED, not yet produced.

## Consistency verdict

**PASS WITH SUBMISSION-PACKAGING BLOCKERS.** No numerical contradiction was found across drafted publication documents. Bibliographic normalization, figures, immutable archive DOI and author-supplied declarations remain unresolved.
