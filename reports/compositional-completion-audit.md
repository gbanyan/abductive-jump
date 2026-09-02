# Compositional Representation Jump — Completion Audit

This is the requirement-by-requirement evidence index for the pre-registered final
generalization/falsification phase. `COMPLETE` means the named authoritative evidence exists
and has been checked. `PENDING` is intentionally not treated as satisfied. The table is updated
only at phase boundaries; it does not use partial confirmatory outcomes.

| Spec | Requirement | Status | Authoritative evidence |
| ---: | --- | --- | --- |
| 0 | Preserve the frozen AJ5 result and bounded interpretation | COMPLETE | `reports/abductive-jump-final.md`; antecedent commit `dd6e82c` |
| 1 | Test generic construction of a validated representation jump | PENDING | Final replay, statistics, and verdict |
| 2 | Distinguish menu selection from compositional search | PENDING | C0/C1/C2/C3/C_self/C_rand confirmatory comparisons |
| 3 | Remove semantic high-level operators and accept falsification | COMPLETE | `artifacts/high_level_operator_exclusions.json`; preregistration §§2–3 |
| 4 | Reuse frozen Phi-4 model, revision, quantization, engine, and policy | COMPLETE | Frozen configs and `artifacts/compositional-preregistration-freeze.json` |
| 5 | Audit the existing AJ5 state before preregistration | COMPLETE | `docs/compositional-jump-existing-state-audit.md` |
| 6 | Exclude family-aligned high-level operators | COMPLETE | `artifacts/high_level_operator_exclusions.json` |
| 7 | Define a generic low-level rewrite language | COMPLETE | `src/abductive_jump/generic_primitives.py`; `artifacts/generic_primitive_manifest.json` |
| 8 | Enforce primitive admissibility and prevent atomic answer operators | COMPLETE | 29 operator unit tests; `artifacts/depth_one_admissibility.parquet` (0/17,280 jumps) |
| 9 | Record deterministic composition graph and ancestry | COMPLETE | `src/abductive_jump/composition_search.py`; replay schema tests |
| 10 | Freeze depth and require genuine multi-step success | COMPLETE | Frozen depth four; preregistration §10; final success check pending under §§22/34 |
| 11 | Match breadth/depth evaluation opportunity | COMPLETE | C2 and C3 each have 192 primitive evaluations per world in frozen configs |
| 12 | Decompose high-level oracle targets into primitive witnesses | COMPLETE | `artifacts/composition_reachability.parquet` |
| 13 | Report bounded minimum construction distance | COMPLETE | `artifacts/minimum_edit_depth.parquet`; limits disclosed in preregistration |
| 14 | Retain all eight existing AJ5 families | COMPLETE | Existing confirmatory config and world manifest generation tests |
| 15 | Prospectively seal one structural held-out family | COMPLETE | `triadic_relation_reification` frozen before pilot inference |
| 16 | Evaluate temporal-state preference without reusing exposed structure | COMPLETE | Rejection rationale in preregistration: AJ5 had already exposed state |
| 17 | Select and justify an admissible alternative held-out family | COMPLETE | Independent arity-three reified-relation generator and preregistration §§15–17 |
| 18 | Run depth-matched no-jump controls | PENDING | Existing and held-out control shards plus FJR analysis |
| 19 | Implement all registered conditions | COMPLETE | C0, C1, C2, C3, C_self, C_rand, C5 in `src/abductive_jump/conditions.py` and runner tests |
| 20 | Execute critical C3 comparisons against matched baselines | PENDING | Final paired tests and Holm correction |
| 21 | Estimate retained jump gain rho_J with uncertainty | PENDING | `final_compositional_verdict.json` and per-family artifact |
| 22 | Require validated multi-step ancestry and replay | PENDING | Confirmatory candidates and deterministic replay audit |
| 23 | Test held-out success prospectively | PENDING | Held-out shard remains locked until existing reconstruction and control are terminal |
| 24 | Run same-vocabulary LLM self-composition control | PENDING | Confirmatory C_self rows and `llm_selected_composition.parquet` |
| 25 | Run matched random-primitive baseline | PENDING | Confirmatory C_rand rows and `random_primitive_control.parquet` |
| 26 | Keep the search mechanism frozen and outcome blind | COMPLETE | `src/abductive_jump/composition_search.py` frozen before confirmatory calls |
| 27 | Prevent family labels, target distance, and semantic fitness leakage | COMPLETE | Search API/code audit; target witnesses isolated in reachability module |
| 28 | Commit preregistration before new-phase inference | COMPLETE | Commit `65f2087`; hash manifest and correction record `7ecb977` |
| 29 | Restrict pilot to existing-family seeds and make no post-pilot rescue | COMPLETE | Corrected pilot audit; held-out run directories absent before unlock |
| 30 | Run registered confirmatory scale | PENDING | Four terminal shard audits; expected 33,600 calls |
| 31 | Enforce equal registered compute opportunity | PENDING | Run audits must show zero budget mismatches for every shard |
| 32 | Produce all registered primary and safety metrics | PENDING | Final analysis artifacts |
| 33 | Report the menu-dependence falsification outcome without rescue | PENDING | Final report and verdict |
| 34 | Apply the preregistered CJ0–CJ5 verdict tree | PENDING | `artifacts/final_compositional_verdict.json` plus Reviewer #2 disposition |
| 35 | Reconsider bounded AJ6 language only if CJ5 survives review | PENDING | Final claim matrix and report |
| 36 | Perform all 20 Reviewer #2 attacks; allow downgrade only | PENDING | `reports/compositional-representation-jump-reviewer2.md` |
| 37 | Materialize every required artifact | PENDING | Reproducibility verifier required-file check |
| 38 | Produce all seven registered figures | PENDING | `reports/figures/compositional/figure1-*.svg` through `figure7-*.svg` |
| 39 | Keep interpretation bounded to supplied structural primitives | PENDING | Final report wording audit |
| 40 | If composition fails, report vocabulary dependence and stop | PENDING | Outcome-contingent final report branch |
| 41 | Follow the registered execution order, ledger, commit, and push | PENDING | `research-ledger.md`, run audits, Git history, clean synchronized branch |
| 42 | Enforce anti-hindsight rules for held-out failure | PENDING | Frozen hashes, ledger chronology, and absence of post-outcome implementation changes |
| 43 | Answer menu dependence and prospective held-out generalization | PENDING | Final report, Reviewer #2 report, claim matrix, and verdict JSON |

## Terminal checks

Completion additionally requires: all four raw traces have their exact registered line counts;
all selected candidates replay; every required artifact and figure exists and is nonempty; the
full test and lint suites pass; tracked outputs are hashed; the remote model service is stopped
and GPU memory is released; and local/remote `master` agree with a clean worktree.
