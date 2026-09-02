# Compositional Representation Jump — Completion Audit

This is the requirement-by-requirement evidence index for the pre-registered final
generalization/falsification phase. `COMPLETE` means the named authoritative evidence exists
and has been checked. `PENDING` is intentionally not treated as satisfied. The table is updated
only at phase boundaries; it does not use partial confirmatory outcomes.

| Spec | Requirement | Status | Authoritative evidence |
| ---: | --- | --- | --- |
| 0 | Preserve the frozen AJ5 result and bounded interpretation | COMPLETE | `reports/abductive-jump-final.md`; antecedent commit `dd6e82c` |
| 1 | Test generic construction of a validated representation jump | COMPLETE | `artifacts/compositional_candidates.parquet`; `artifacts/final_compositional_verdict.json` |
| 2 | Distinguish menu selection from compositional search | COMPLETE | `artifacts/compositional_comparisons.parquet`; C0/C1/C2/C3/C_self/C_rand results |
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
| 18 | Run depth-matched no-jump controls | COMPLETE | Both control shard audits; `artifacts/no_jump_depth_controls.parquet` |
| 19 | Implement all registered conditions | COMPLETE | C0, C1, C2, C3, C_self, C_rand, C5 in `src/abductive_jump/conditions.py` and runner tests |
| 20 | Execute critical C3 comparisons against matched baselines | COMPLETE | `artifacts/compositional_comparisons.parquet`; 10,000 paired replicates and Holm correction |
| 21 | Estimate retained jump gain rho_J with uncertainty | COMPLETE | `artifacts/final_compositional_verdict.json`; `artifacts/compositional_per_family.parquet` |
| 22 | Require validated multi-step ancestry and replay | COMPLETE | `artifacts/composition_ancestry.parquet`; 16,800/16,800 replay validation |
| 23 | Test held-out success prospectively | COMPLETE | Held-out reconstruction/control audits; unlock chronology in `research-ledger.md` |
| 24 | Run same-vocabulary LLM self-composition control | COMPLETE | `artifacts/llm_selected_composition.parquet`; C_self 0/400 existing and 0/100 held out |
| 25 | Run matched random-primitive baseline | COMPLETE | `artifacts/random_primitive_control.parquet`; C_rand 13% existing and held out |
| 26 | Keep the search mechanism frozen and outcome blind | COMPLETE | `src/abductive_jump/composition_search.py` frozen before confirmatory calls |
| 27 | Prevent family labels, target distance, and semantic fitness leakage | COMPLETE | Search API/code audit; target witnesses isolated in reachability module |
| 28 | Commit preregistration before new-phase inference | COMPLETE | Commit `65f2087`; hash manifest and correction record `7ecb977` |
| 29 | Restrict pilot to existing-family seeds and make no post-pilot rescue | COMPLETE | Corrected pilot audit; held-out run directories absent before unlock |
| 30 | Run registered confirmatory scale | COMPLETE | Four passing shard audits; exactly 33,600 unique calls |
| 31 | Enforce equal registered compute opportunity | COMPLETE | All four run audits report zero primary budget mismatches |
| 32 | Produce all registered primary and safety metrics | COMPLETE | `artifacts/compositional_jump_results.parquet`; cost, family, control, and comparison artifacts |
| 33 | Report the menu-dependence falsification outcome without rescue | COMPLETE | `reports/compositional-representation-jump-final.md`; `artifacts/final_compositional_verdict.json` |
| 34 | Apply the preregistered CJ0–CJ5 verdict tree | COMPLETE | Data verdict CJ5; Reviewer #2 disposition CJ5 |
| 35 | Reconsider bounded AJ6 language only if CJ5 survives review | COMPLETE | `artifacts/final_compositional_claim_matrix.csv`; strictly procedural AJ6-candidate wording |
| 36 | Perform all 20 Reviewer #2 attacks; allow downgrade only | COMPLETE | `reports/compositional-representation-jump-reviewer2.md` |
| 37 | Materialize every required artifact | COMPLETE | Required tables, reports, audits, replay files, and figures are present and nonempty |
| 38 | Produce all seven registered figures | COMPLETE | `reports/figures/compositional/figure1-*.svg` through `figure7-*.svg` |
| 39 | Keep interpretation bounded to supplied structural primitives | COMPLETE | Final report Limits and Final claim; Reviewer #2 final boundary |
| 40 | If composition fails, report vocabulary dependence and stop | COMPLETE | Outcome-contingent branch not triggered: C3 passed registered CJ4/CJ5 gates |
| 41 | Follow the registered execution order, ledger, commit, and push | COMPLETE | `research-ledger.md`, four run audits, and commits through `7cf4bb9`; final artifact commit follows verification |
| 42 | Enforce anti-hindsight rules for held-out failure | COMPLETE | Frozen hashes, unlock chronology, source audit, and no post-outcome implementation changes |
| 43 | Answer menu dependence and prospective held-out generalization | COMPLETE | Final report, Reviewer #2 report, claim matrix, and verdict JSON |

## Terminal checks

Completion additionally requires: all four raw traces have their exact registered line counts;
all selected candidates replay; every required artifact and figure exists and is nonempty; the
full test and lint suites pass; tracked outputs are hashed; the remote model service is stopped
and GPU memory is released; and local/remote `master` agree with a clean worktree.
