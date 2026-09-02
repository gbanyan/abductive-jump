# Research ledger

All times use Asia/Taipei (UTC+08:00). Entries are append-only except to correct an explicitly identified clerical error.

## 2026-09-02 01:05 +08:00 — Project initiation and compute audit

- Read the complete project specification before experimentation.
- Confirmed the working directory was empty and not already a repository; adopted it as the dedicated project rather than creating a competing directory.
- Connected to the mandated primary host `gblinux`.
- Observed host `GBLinux`, NVIDIA GeForce RTX 4090, 24,564 MiB VRAM, driver 595.84, and reported CUDA 13.2.
- Default remote Python is 3.14.4. `torch` did not import successfully in the audit command, and neither `vllm` nor `llama-cli` was found on the default PATH. Environment installation/selection is therefore an open calibration task, not silently assumed.
- Confirmed no DGX, multi-GPU, fine-tuning, or >14B model will be used for this phase.
- Created the repository skeleton before scientific experimentation.

## Frozen decision boundaries established at initiation

- Engine validity, local adequacy, exact/bounded incumbent oracle, unambiguous structural escape, prospective freezing, and controlled false-jump rate remain hard gates.
- Negative outcomes AJ0–AJ4 are valid endpoints and will not trigger post-confirmatory redesign.
- The representation DSL and mutation operators will be generic and family-independent; world-family generators may encode ground truth, but proposal operators may not inspect it.

## 2026-09-02 01:12 +08:00 — Literature and formal-boundary audit

- Audited primary sources spanning LLM program evolution (FunSearch, ShinkaEvolve), open-ended agent evolution (Darwin Gödel Machine), AI-scientist systems, causal identification, program synthesis/symbolic regression, representation invention, and Zahavy's abductive-jump position.
- Fixed the candidate contribution as prospective, oracle-relative representation escape plus proposal-versus-reasoning decomposition—not generic LLM creativity or “LLM + genetic algorithm.”
- Wrote the initial typed-graph, frozen-language membership, provenance, blindness, and J0–J5 contracts in `docs/formal-specification.md` before engine code.

## 2026-09-02 01:15 +08:00 — Engine-only pilot P0

- Implemented the canonical typed representation graph, frozen incumbent-language membership checker, separated hypothesis/representation concepts, finite exact incumbent oracle, prospective prediction commitment, J0–J5 evaluator, structural quality-diversity archive, budget accounting, and all 22 required generic structural operators with complete provenance.
- Implemented eight procedural families and matched no-jump controls. Randomization covers parameters, opaque lexical labels, nuisance graph structure/measurements, samples, interventions, and split hashes. Public world views redact family, truth, validation, test outcomes, and falsification data.
- Ran 61 unit/integration tests successfully and passed Ruff with no findings.
- Ran P0 with 100 seeds × 8 families × jump/no-jump = 1,600 worlds. Every incumbent oracle was exhaustive and exact; every world passed J0; supplied ground truth passed J0–J5 in 800/800 jump worlds and was accepted in 0/800 no-jump worlds.
- Recorded 1,600 unique ground-truth candidate hashes and 800 unique matched split hashes. Jump/no-jump pairs intentionally share a split policy for comparison.
- Materialized the world manifest, ground truth, oracle certificates, gate results, and no-jump tables as Parquet plus `reports/world-engine-validation.md`.
- Interpretation boundary: P0 demonstrates engine self-consistency and gate separability only. It does not establish LLM difficulty, proposal reachability, absence of template leakage, or a representation-mutation advantage.

## 2026-09-02 02:16 +08:00 — Calibration interface and model audit

- Added executable bounded expression ASTs, typed structural-support checks, prospective one-intervention commitments, prompt/output hashing, full call replay logs, B0–B5 and P0–P2 condition identifiers, and a family-blind external mutation portfolio.
- Found and repaired pilot-only interface defects before freeze: semantic world IDs, incomplete lexicalization, publicly exposed simulator latent state, ambiguous recursive AST examples, supplied graph IDs misaligned with public variables, non-identifiable state/property observational designs, and experiment prompts lacking incumbent predictions.
- Revalidated the engine after each repair. Current suite: 88 passing tests; P0 remains 800/800 ground-truth jump success and 0/800 no-jump acceptance with exact oracles.
- Qwen2.5-14B-Instruct-AWQ revision `539535859b135b0244c91f3e59816150c8056698` failed the eight-family oracle-mutation free-realization screen (0/8) and was rejected before freeze.
- Switched, per calibration policy, to Microsoft Phi-4 revision `2db69c1c3e91a05d2c64a3185acfbaf36f744e25`, still 14B/single-4090/frozen-weight. Free realization reached only 2/8.
- Introduced a shared family-blind deterministic hypothesis-genome fitter. This deliberately narrows the estimand to representation proposal under exact within-representation realization. The fitter itself passes all eight ground-truth families in tests.
- With supplied correct representation, fitted expression, an exact candidate-vs-incumbent separation table that contains no outcomes, a no-op distractor, and exactly one allowed experiment choice, Phi-4 passed 8/8 oracle worlds.
- An initial two-stage spontaneous scan passed 0/8 (proposal JSON parsed in 6/8). This is below the desired non-floor calibration band, so the primary model/config and benchmark are not frozen. Additional spontaneous/sample/external-proposal calibration is required.
- Preserved negative and intermediate calibration traces; no confirmatory study has been launched.

## 2026-09-02 02:23 +08:00 — Proposal-floor and external-reachability calibration

- Expanded spontaneous Phi-4 proposals to 24 worlds across three world seeds and low/high-temperature decoding. Proposal JSON parsed in 21/24, but no candidate escaped the frozen incumbent language (J1 = 0/24) and validated success remained 0/24.
- Extended the family-blind external portfolio from eight to nine typed variants using only generic node/relation mutations and generic function/regime attributes (square transform, affine context, sign contrast). The proposer still receives only `PublicWorld`, never family or truth.
- Ran 14,400 deterministic candidate evaluations across 800 jump and 800 matched no-jump worlds. Portfolio reachability was 800/800 jump worlds; false acceptance was 0/800 controls.
- This is explicitly a reachability ceiling, not a B4/B5 result. It does not include matched LLM calls, candidate selection constraints, or confirmatory budgets, and the alignment between generic variants and procedural families remains a Reviewer #2 threat.

## 2026-09-02 03:07 +08:00 — Matched-proposal and supplied-representation calibration

- Added a machine-readable equal-budget contract covering completion-token capacity, calls, candidate evaluations, and interventions. Actual use remains separately logged; unused capacity may not be reassigned to extra candidates.
- Replaced the sample-matched condition's verbose full-graph output with a compact plan of at most three choices from the same 22 generic typed mutation operators. The plan is executed by the audited mutation engine, so this is the preregistration candidate for the critical “LLM chooses mutation” comparison rather than a new family-specific operator.
- Corrected the deterministic realization solver for rank-deficient observational designs by using a deterministic RREF solution with free coefficients set to zero. This handles observational equivalence without turning incompatible candidates into exact fits. Prompts now explicitly distinguish exact from non-exact fitted realizations.
- Revised the structured-output prompt to v9 with a 160-token brevity instruction. On eight development worlds, nine externally proposed representations per world plus Phi-4 reasoning parsed in 72/72 slots and produced at least one prospectively validated jump in every family (8/8 worlds; 9/72 candidates).
- On the same eight-family development set, nine independent high-temperature LLM mutation plans per world parsed and completed reasoning in 51/72 slots but produced 0/72 validated jumps. Gate counts were J1 28/72, J2 20/72, J3 15/72, J4 2/72, J5 0/72. This localizes the failure beyond syntax: some self-proposals escaped and discriminated but did not survive prospective falsification.
- The first external v9 attempt exposed sparse Parquet columns and pre-call rank-deficiency failures. It was superseded before freeze; the corrected rerun retains all 72 calls and sparse error fields. No confirmatory data have been generated.
- Current suite: 100 tests pass and Ruff reports no findings. Model, budgets, condition runner, confirmatory seeds, and thresholds remain unfrozen pending no-jump and throughput calibration.

## 2026-09-02 03:09 +08:00 — Unified condition and budget pilot

- Implemented a common B0–B5 runner. Each condition uses three slots; each slot always receives two LLM calls, one deterministic candidate evaluation, and one prospectively committed intervention. Invalid scientific outputs consume their slot; HTTP/infrastructure failures abort the run.
- B2 retains the incumbent graph. B3 changes only an equation value attribute that remains inside the frozen language. B4 samples the nine-member external typed portfolio with replacement. B5 selects structurally distinct portfolio members without replacement and records archive occupancy. All use the same deterministic realization and exact outcome-blind intervention designer.
- The first eight-family runner attempt stopped because a syntactically parsed B0 graph contained dangling edges. Moved graph validation into the phase-one failure boundary; the malformed candidate now falls back to the incumbent and receives no extra opportunity. The aborted directory is excluded from results.
- Corrected rerun: 288/288 calls, 144 candidate rows, and identical per-cell resources. Development JSR was B0 0/8, B1 0/8, B2 0/8, B3 0/8, B4 1/8, B5 3/8. This is not confirmatory.
- Matched no-jump rerun: 288/288 calls; FJR was 0/8 for every condition, and no candidate passed J4 or J5.
- Added the P0/P1/P2 factorial on a separate development seed with the same two-call reasoner path. JSR was P0 0/8, P1 4/8, P2 8/8. P2 supplies only the correct typed representation, not its equation or outcomes.
- Throughput at concurrency 16 makes the minimum permitted confirmatory scale feasible on the mandated single RTX 4090. Candidate budget three is retained: it avoids the nine-candidate external ceiling while producing multi-family development successes.
- Current suite: 105 tests pass and Ruff reports no findings. No confirmatory seed has been queried.

## 2026-09-02 03:10 +08:00 — Preregistration freeze

- Clerical correction: the immediately preceding entry was initially stamped `03:34`; host time showed this was impossible. Its header was corrected to `03:09`. Its scientific content is unchanged.
- Froze `docs/abductive-jump-preregistration.md` and all four confirmatory configs in commit `895ebb9118ffd0046825b88868621f2a70f69f61` before any confirmatory model request.
- Re-audited the live server: `microsoft/phi-4` on the mandated `gblinux` host, vLLM image digest `sha256:607442e407b0fea97f8a132a78b787c121a996dd4de181fa08e8da06e71ec2db`.
- Recorded config hashes in `artifacts/preregistration-freeze.json`. The Git worktree was clean at the freeze check.
- The next model request using seeds 10000–10049 or 20000–20024 begins confirmatory inference; from that point families, seeds, operators, thresholds, budgets, model, and prompts cannot change to rescue results.

## 2026-09-02 11:10 +08:00 — Confirmatory completion, replay, and verdict

- Completed all four frozen shards on `gblinux`: 14,400 primary jump calls, 7,200 primary control calls, 7,200 factorial jump calls, and 3,600 factorial control calls. All expected rows and equal-budget invariants matched exactly; no infrastructure shard rerun was required.
- Primary JSR: B0 1/400, B1 1/400, B2 0/400, B3 0/400, B4 142/400, B5 142/400. Every primary condition had FJR 0/200. B4 and B5 each succeeded in all eight families.
- Factorial JSR: P0 0/400, P1 142/400, P2 400/400. All factorial FJR values were 0/200.
- Replayed 10,800 primary candidates from raw outputs and frozen seeds. Reconstructed graph, expression, exact intervention, prediction, and commitment; every J0–J5 value matched. Materialized canonical candidate, mutation, and intervention artifacts.
- Corrected two analysis-only defects with regression tests: replay initially mixed public/internal variable names for the diagnostic prediction export, and the first bootstrap draft included control seeds in JSR resampling. Frozen outputs, gates, and raw rates were unaffected.
- Ran the preregistered triggered A6 secondary ablation with identical per-world budget: random untyped mutation JSR 18/400 (4.5%), FJR 0/200. A1/A2/A3 showed no archive, falsifier, or crossover contribution; A4 value-only was 0%; A5 LLM-chosen mutation was 0.25%.
- The 10,000-replicate family-stratified paired bootstrap and Holm correction support all eight B4/B5 comparisons against B0–B3. Differences were 0.3525–0.355; adjusted p-values were `0.00079992`. P1−P0 and P2−P0 adjusted p-values were `0.00019998`. B4/B5 FJR Wilson upper bound was 0.01885.
- Frozen verdict: **AJ5**. AJ6 is unavailable because no structural family was held out. The claim is narrowed to structured external proposal coverage in the tested worlds; archive/falsifier benefits and general autonomous discovery are not supported.
