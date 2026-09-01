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
