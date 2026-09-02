# Objective Completion Audit

Audit date: 2026-09-02. Source contract: the 52-section user specification attached to this project. This audit distinguishes required evidence, optional extensions, and disclosed deviations. It does not infer completion merely from the AJ5 verdict.

## Requirement–evidence matrix

| § | Requirement | Authoritative evidence | Audit status |
|---:|---|---|---|
| 1 | Single `gblinux` RTX 4090; no DGX, >14B, multi-GPU, or fine-tuning | Frozen configs, model/runtime manifests, ledger hardware audit, raw-call manifests | Required scope satisfied |
| 2 | Dedicated Git repository and required directory skeleton | Git history from `ce48487`; README, ledger, docs/src/tests/artifacts/reports/configs; private GitHub remote | Satisfied |
| 3–4 | Formal incumbent-space escape; no semantic novelty endpoint | Formal specification, typed `LanguageSpec`, deterministic gate code, final metrics | Satisfied |
| 5 | LLM-free procedural World Engine with simulation, interventions, oracle, escape, controls | `worlds.py`, `oracle.py`, `gates.py`, engine artifacts and 36 world-engine tests | Satisfied |
| 6 | J0–J5 including prospective freeze and independent falsification | `executable.py`; 10,800 replayed commitments; confirmatory gate table | Satisfied |
| 7 | Exact/bounded incumbent oracle for each primary family | Exhaustive oracle certificates for 1,600 engine worlds and every confirmatory replay | Satisfied |
| 8 | Typed, serializable, canonical, hashable representation DSL with all named kinds | `representation.py` and representation tests | Satisfied |
| 9 | Separate `G_H` and `G_R` | `hypothesis_genome.py`, `mutations.py`, 1,800-row genome validation showing zero graph-hash/J1 changes for `G_H` | Satisfied |
| 10 | All 22 generic representation operators with provenance | `MutationOperator`, 22 parameterized tests, 17,224-row mutation trace with arguments/seeds/parent/child hashes | Satisfied |
| 11 | Six to eight procedural families | Eight families, 50 confirmatory seeds each | Satisfied |
| 12–13 | Same-scale no-jump controls and randomized worlds/splits/hashes | 800 engine controls, 200 confirmatory controls; manifests and split-hash tests | Satisfied |
| 14–16 | Calibrated frozen 8–14B instruct model; no reasoning model; frozen manifest | Qwen rejection, Phi-4 free/supplied/spontaneous pilots, freeze commit `895ebb9` | Satisfied |
| 17 | LLM never judges truth | All verdict fields produced by deterministic evaluator; replay equality | Satisfied |
| 18 | B0–B5 interfaces | Unified runner and 3,600 primary world-condition cells | Satisfied, with limitations below |
| 19 | Equal LLM-call/token-cap/candidate/intervention envelope and cost frontier | Exact 6/3/3 per cell; equal 4,200-token capacity; `compute_quality_frontier.parquet` | Satisfied; actual EOS token totals differ and are reported |
| 20 | P0/P1/P2 proposal–reasoning factorial | 400 jump + 200 control worlds per source | Satisfied |
| 21 | Structural quality-diversity archive, not embedding diversity | B5 distinct selection, stable executable-theory archive, 1,800 retained bin entries, occupancy 3 in all 600 worlds | Satisfied as retention/accounting; no online archive effect |
| 22–23 | Objective survival stages and outcome-blind maximum-separation experiment design | Fitter, gate table, exact designer, commitment replay | Satisfied |
| 24 | JSR, FJR, AP, cost, CF gain, proposal gap, structural coverage | Condition/factorial/frontier/per-family artifacts and final report | Satisfied |
| 25 | Secondary semantic/lexical diagnostics | Explicitly optional and intentionally omitted | Optional, not run |
| 26 | P0–P3 staged pilots | Engine, oracle competence, spontaneous difficulty, and budget pilots in ledger/artifacts | Satisfied |
| 27 | Preregistration before confirmatory results | Commit `895ebb9118ffd0046825b88868621f2a70f69f61` and freeze manifest | Satisfied |
| 28 | 400–800 jump and 200–400 controls | 400 jump + 200 no-jump worlds | Satisfied at permitted lower bound |
| 29 | World/decoding replication, hierarchical family analysis, seed sensitivity | Paired family-stratified bootstrap, per-family table, five seed blocks | Satisfied |
| 30 | Avoid template-only claims; optional held-out structural family | All eight families retained; operator-alignment limitation audited; no AJ6 | Required claim control satisfied; optional held-out family not run |
| 31 | Semantic, invalid, unnecessary-latent, overcomplicated negative controls | 2,400-row `negative_controls.parquet`; 0/600 accepted in each category | Satisfied as deterministic supplementary controls |
| 32–33 | A1–A6 and external structured versus LLM-selected comparison | Ablation table; A6 matched secondary run; factorial and B1/B4 comparison | Satisfied; A3 structurally null as preregistered |
| 34–35 | Twenty-point Reviewer #2 and frozen AJ0–AJ6 verdict tree | Reviewer report, claim matrix, `final_verdict.json` | Satisfied; narrow AJ5, AJ6 unavailable |
| 36–38 | Runtime audit, 8–14B model, compact structured context | Ledger, frozen Docker/model manifests, prompt v10 and 4096 context | Satisfied |
| 39 | Per-call prompt/output/token/latency/model/provenance logs | Six raw JSONL traces, 36,000 lines, SHA-256/size/line manifest; raw files gitignored | Satisfied |
| 40 | Canonical tabular/manifests/verdict artifacts | All named canonical files plus confirmatory variants and reproducibility manifest | Satisfied |
| 41–42 | Required reports and Figures 1–7 | Four reports and seven validated SVGs | Satisfied |
| 43 | Prohibited claims avoided | Final report, Reviewer audit, README | Satisfied |
| 44 | Literature positioning across requested adjacent fields | `docs/literature-audit.md` | Satisfied |
| 45 | Unit tests before/for major components | 112 collected tests after audit; replay and analysis regressions included | Satisfied |
| 46 | Staged execution order | Ledger and commit sequence show engine → validation → calibration → preregistration → confirmatory → audit → verdict | Scientifically satisfied; mutation code was co-developed before the first engine artifact but engine validation was rerun before any LLM call |
| 47–49 | Compute-failure and stop policies | Single-host batch execution, no rescue changes, exact oracle/local adequacy/FJR checks | Satisfied |
| 50–52 | Narrow two-question interpretation and full execution rather than proposal-only | Final report, artifacts, replay, private pushed repository | Satisfied |

## Condition-fidelity audit

- **B0:** direct typed-graph output, followed by shared realization/reasoning. It had 494/1,200 invalid proposal slots; these remained failures.
- **B1:** independent high-temperature compact mutation plans from the same generic vocabulary, with 176/1,200 fallbacks.
- **B2:** the graph vocabulary was frozen exactly. Its two stages are interpretation then shared realization/reasoning; it is a bounded agentic baseline, not an open-ended tool-using agent.
- **B3:** confirmatory runs changed within-language equation value attributes. The supplementary `G_H` implementation validates value mutation, value crossover, and attribute exchange; all leave the representation hash unchanged and J1 false.
- **B4:** external typed mutations sampled with replacement.
- **B5:** structurally distinct candidates sampled without replacement, all retained in a stable structural/prediction archive, followed by the independent J5 falsification gate. B5 did not outperform B4; no archive or falsifier mechanism claim is made.

## Evidence integrity

- Expected preregistered calls: 32,400; observed: 32,400.
- Triggered A6 calls: 3,600; observed: 3,600.
- Replayed primary candidates: 10,800/10,800, zero gate mismatches.
- Confirmatory mutation/proposal records: 17,224 rows with deterministic provenance fields.
- Negative controls: 2,400 rows, zero accepted.
- Git preregistration and final result commits are both present on `origin/master`.

## Remaining non-claims, not hidden work

The objective labels held-out structural-family generalization and semantic diagnostics as optional. Neither was run. Consequently AJ6, universal abduction, real-science transfer, stronger-model robustness, archive benefit, falsifier benefit, crossover benefit, and exact actual-token equality are not claimed. These are future studies, not missing evidence for the narrow completed AJ5 project.
