# NMI revision and extension audit

Status: 3 September 2026. This audit uses archived artifacts and deterministic replay only; it runs no new language-model inference.

## Findings that change the manuscript

1. **C3 does not require language-model output.** The frozen C3 path deterministically constructs and ranks representations, fits the expression and selects the maximum-separation intervention. The model-returned representation, expression and intervention are overwritten; only `explanation` remains, and it is absent from J0–J5. A model-free replay matched 2,400/2,400 candidate verdicts, retained 500/500 jump-world successes and produced 0/300 control false jumps.
2. **C_self is a serialization result.** All 38,400 confirmatory plan records failed `invalid_schema:plans_must_be_a_list`; no four-step plan reached structural evaluation. The 0/500 world score cannot support conceptual-proposal failure.
3. **The no-jump null is non-trivial only through J3.** For C3 controls, 800/900 candidates passed J0–J1, 567 passed through J2 and 283 passed through J3. None passed J4. Because control truth is inside the exact incumbent language, strict improvement is impossible under noiseless evaluation. Report 0/300 as an exact-simulator specificity check, not an empirical noisy-science false-positive rate.
4. **Family breadth is limited.** C3 is 100% in every one of eight known generators and one conceptually adjacent held-out generator. Seeds estimate within-generator reliability; they are not independent structural families.
5. **The freeze evidence is content evidence, not independent preregistration proof.** AJ5 and CJ5 commits are publicly retrievable, but both are unsigned and no registry, signed tag or transparency-log timestamp was located. Use “prospectively specified” and “commit-frozen”.

## Completed revision package

- Reframed the title and abstract around the prospective assay and typed deterministic search.
- Added the model-free component audit and candidate-level J0–J5 attrition.
- Added a nearest-work comparison covering PiEvo, Model Discovery Agent and HypoArena.
- Corrected the two 2026 Nature citations.
- Added a worked held-out example and redrew aggregate figures.
- Produced a clean manuscript PDF that begins with the title and abstract, separate from the discussion overview.

## Experiments still required for the stronger NMI claim

These are not claimed as completed:

1. Redesign the reasoning path so model-generated scientific content survives into the committed theory; compare full system, minus-model, deterministic reasoner and oracle representation.
2. Compare at least one stronger open model and one frontier model under raw JSON, grammar-constrained decoding and validator-feedback repair.
3. Freeze at least three independently authored held-out families, including a noisy or stochastic mechanistic simulation, distractor primitives, deeper paths and partial observability.
4. Report model/interface gate attrition and a unified compute ledger for fitter evaluations, operations, tokens and wall time.

These choices change cost, API exposure and benchmark design and therefore require author authorization before execution.
