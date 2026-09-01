# Pilot results

Status: P0 complete; P1/P2 calibration in progress; not confirmatory.

## P0 engine-only

- 8 procedural jump families × 100 seeds and 800 matched no-jump controls (1,600 total worlds).
- Exhaustive incumbent oracle available in every world.
- J0 local adequacy: 1,600/1,600.
- Supplied ground-truth J0–J5 success: 800/800 jump worlds.
- Ground-truth false acceptance: 0/800 no-jump worlds.
- 1,599 unique ground-truth candidate hashes and 800 matched split hashes.
- 88 unit/integration tests currently pass; Ruff passes.

These are engine self-consistency checks, not method results.

## Calibration findings

| Interface/model | Worlds | Parse | Validated J0–J5 |
|---|---:|---:|---:|
| Qwen2.5-14B-AWQ, supplied representation, free AST | 8 | 8/8 | 0/8 |
| Phi-4 14B, supplied representation, free AST | 8 | 8/8 | 2/8 |
| Phi-4, supplied representation + shared deterministic fitter + exact separation table | 8 | 8/8 | 8/8 |
| Phi-4, self-proposed representation + same fitter/reasoner | 24 | 21/24 proposal parses | 0/24 |
| External family-blind portfolio reachability (no LLM) | 800 jump + 800 control | deterministic | 800/800 jump; 0/800 control |

The free-AST failures motivated a preregistration-safe narrowing before freeze: parameter/equation fitting is a shared deterministic component, while representation proposal remains the manipulated factor. No confirmatory thresholds, families, or operators have been changed after viewing confirmatory results because no confirmatory run exists.

The external reachability ceiling uses nine typed variants, including generic square-transform, affine-context, and sign-contrast realizations. Its 100% coverage is useful for avoiding a search-space floor but creates an operator-alignment threat. Confirmatory claims require family-blind code paths, matched budgets, ablations/random typing controls, and preferably a held-out structural family; reachability alone is not evidence for B4/B5 superiority.
