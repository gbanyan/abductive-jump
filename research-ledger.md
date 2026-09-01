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
