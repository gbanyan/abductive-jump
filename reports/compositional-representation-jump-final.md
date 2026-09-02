# Compositional Representation Jump — Final Report

Preregistration commit: `65f2087`. Recorded pre-confirmatory admissibility correction:
`7ecb977`. Frozen antecedent: AJ5 at `dd6e82c`.

## Result

The preregistered data-only decision was **CJ5**. Reviewer #2 returns
**CJ5**.

The result does not modify the frozen AJ5 finding. It tests whether that advantage survives
removal of atomic family-level operators and whether it transfers to the prospectively sealed
arity-three relation family.

| Condition | Existing reconstruction JSR | Held-out JSR | Existing FJR | Held-out FJR |
| --- | ---: | ---: | ---: | ---: |
| C0 | 0/400 (0.0%) | 0/100 (0.0%) | 0/200 | 0/100 |
| C1 | 131/400 (32.8%) | 0/100 (0.0%) | 0/200 | 0/100 |
| C2 | 0/400 (0.0%) | 0/100 (0.0%) | 0/200 | 0/100 |
| C3 | 400/400 (100.0%) | 100/100 (100.0%) | 0/200 | 0/100 |
| C_self | 0/400 (0.0%) | 0/100 (0.0%) | 0/200 | 0/100 |
| C_rand | 52/400 (13.0%) | 13/100 (13.0%) | 0/200 | 0/100 |
| C5 | 400/400 (100.0%) | 100/100 (100.0%) | 0/200 | 0/100 |

## Primary tests

The two registered existing-family comparisons were:

- `C3_GENERIC_COMPOSITION-C0_FIXED_SPACE`: difference 1.0000, 95% bootstrap CI [1.0000, 1.0000], one-sided permutation p=9.999e-05, Holm p=0.00019998.
- `C3_GENERIC_COMPOSITION-C2_GENERIC_DEPTH_1`: difference 1.0000, 95% bootstrap CI [1.0000, 1.0000], one-sided permutation p=9.999e-05, Holm p=0.00019998.

Retained jump gain was `rho_J=3.0534351145038165` with bootstrap interval
`[2.684563758389262, 3.5398230088495573]`. This ratio is reported alongside its absolute
denominator because a low C1 rate can inflate it.

## Construction and safety

- Successful C3 candidate depths: [4]; all registered compositional successes require
  depth >=2.
- Replay: 16800/16800 selected candidates reproduced from frozen seeds and
  raw outputs; ancestry artifact contains 35533 record rows.
- C3 combined no-jump FJR: 0.0%, Wilson interval
  `[0.000000, 0.012643]`.
- No-jump depth artifact contains 6300 candidate-level rows.
- Successful primitive-sequence distribution is stored without semantic embeddings in
  `final_compositional_verdict.json`.

## Held-out interpretation

The held-out family was never used for LLM/search pilot inference and was not unlocked until
the known-family reconstruction and controls were terminal. It requires an arity-three
reified relation rather than AJ5's binary property relation. The broad idea of relations and
reification was not conceptually novel: both existed in the earlier DSL. The valid claim is
therefore prospective generalization to an unseen structural configuration, not invention
without prior vocabulary.

## Limits

The structured search grammar deliberately spans typed-node, function, relation, and reified
edge strata. This is far weaker than an atomic family answer, but it remains a supplied
structural prior. The deterministic fitter also maps completed graph motifs to a bounded
executable basis. Results concern representation construction under these procedural worlds,
not open-ended science, universal theory invention, or general LLM abduction.

## Final claim

Generic local rewrites were compositionally assembled into validated representations and prospectively generalized to the registered held-out structural family.
