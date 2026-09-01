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
| Phi-4, 9 independent compact typed mutation plans/world | 8 worlds, 72 slots | 51/72 proposal and reasoning parses | 0/8 worlds; 0/72 candidates |
| External family-blind representations + Phi-4 reasoner (v9) | 8 worlds, 72 slots | 72/72 | 8/8 worlds; 9/72 candidates |
| External family-blind portfolio reachability (no LLM) | 800 jump + 800 control | deterministic | 800/800 jump; 0/800 control |

The free-AST failures motivated a preregistration-safe narrowing before freeze: parameter/equation fitting is a shared deterministic component, while representation proposal remains the manipulated factor. No confirmatory thresholds, families, or operators have been changed after viewing confirmatory results because no confirmatory run exists.

The external reachability ceiling uses nine typed variants, including generic square-transform, affine-context, and sign-contrast realizations. Its 100% coverage is useful for avoiding a search-space floor but creates an operator-alignment threat. Confirmatory claims require family-blind code paths, matched budgets, ablations/random typing controls, and preferably a held-out structural family; reachability alone is not evidence for B4/B5 superiority.

The compact self-proposal interface exposes the same generic mutation vocabulary and accepts at most three operations. It avoids the token asymmetry of asking the model to reproduce an entire graph. Across 72 high-temperature slots it produced 51 executable plans: 28 passed J1, 20 passed J2, 15 passed J3, two passed J4, and none passed J5. In contrast, the nine externally generated candidates per world plus the same v9 reasoner yielded exactly one successful structural candidate in each family (unification yielded one additional equivalent success), with 100% JSON parsing. This is calibration evidence for a proposal gap, not a confirmatory effect.

The v9 external run used 72 calls, 8,263 completion tokens, and 109.17 summed call-seconds. The sample-matched run used 123 of a maximum 144 calls because malformed first-stage plans did not receive a reasoning call, 21,511 completion tokens, and 264.73 summed call-seconds. Confirmatory conditions therefore still require a runner that enforces identical per-world resource envelopes and does not recycle failed-slot capacity.

## P3 unified budget calibration

The unified v10 runner uses three candidate slots per world. Every B0–B5 condition receives exactly two calls per slot, a 700-completion-token cap per call, three candidate evaluations, and three prospectively frozen interventions. A malformed first-stage proposal falls back to the incumbent for that slot and still consumes its second call; infrastructure failures stop the run. Exact finite action enumeration selects maximum prediction separation before outcomes are revealed. Model-selected experiments are retained only as diagnostics.

On one new development seed in all eight families (48 world-condition cells, 288 calls), the execution invariants were exact. B0–B3 succeeded in 0/8 worlds each, B4 in 1/8, and B5 in 3/8. The four representation-mutation successes occurred in coordinate transformation, hidden regimes, meta-law, and unification. These counts are difficulty/budget calibration only. On eight matched no-jump worlds, every condition had FJR 0/8 and no candidate passed J4 or J5.

The proposal–reasoning pilot on a further disjoint development seed used the same three-slot/two-call envelope. P0 LLM proposals succeeded in 0/8 worlds, P1 external proposals in 4/8, and P2 oracle representations in 8/8. This meets the model-selection criterion: supplied-representation reasoning is at ceiling while spontaneous proposal remains below ceiling. All eight families remain in confirmatory testing; no family was selected or removed based on these pilot outcomes.
