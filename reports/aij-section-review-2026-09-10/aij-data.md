# AIJ data-correctness review (reviewer: aij-data)

Date: 2026-09-10
Domain: Data correctness. Trace numerical claims, denominators, conditions, uncertainty and figure/table captions to frozen source artifacts.
Scope reviewed: `manuscript/AIJ_MANUSCRIPT.md`, `manuscript/AIJ_SUPPLEMENTARY_METHODS.md`, `manuscript/figures/aij/figure_1..7*.png` and `source_data.json`, `manuscript/AIJ_EVIDENCE_RECORD_EXAMPLE.json`, and the supporting artifacts listed under Evidence.

## HEAD and package state

- HEAD: `0214bc592aa55c92e5aaeffd298fbe22b07f3e3c` (branch `nmi-minimal-targeted-sensitivity-v1`).
- Tag `aij-review-package-v1` resolves to the same commit (`0214bc5`). `git diff aij-review-package-v1 HEAD -- manuscript/AIJ_MANUSCRIPT.md manuscript/AIJ_SUPPLEMENTARY_METHODS.md` is empty.
- Working tree has uncommitted NMI-side changes and untracked extension logs only; nothing under `manuscript/AIJ_*` is modified.
- Tag `nmi-github-submission-v4` resolves locally to `9ebf0dc`; the archive name `nmi-preservation-archive-9ebf0dc548a5.tar.gz` in S20 and `docs/publication/AIJ_REPRODUCTION.md` matches that prefix.

## Method

- Recomputed counts directly from parquet/CSV/JSON artifacts using pyarrow in `.venv` (no pandas installed; pyarrow 25.0.1).
- Read `scripts/build_aij_figures.py` and viewed all seven figure PNGs.
- Checked every cited source line reference in S4, S19 and S20 with `sed`.
- Ran one offline, deterministic, model-free script (`scripts/audit_nmi_control_comparator.py`) because its output is not archived in the repository. No model experiment was run; no artifact was modified.
- Prior `reports/AIJ_*` files were treated as background only, not as verification evidence.

## Bottom line

Every numerical claim traced in the main text, supplement, tables and figure captions reproduces from the frozen artifacts. No must-fix data errors were found. The five actionable items below concern traceability and wording precision, not contradictions.

## Verified claims, by section

### Title / abstract
- 400 jump worlds; B4 and B5 each 142/400; B0 and B1 each 1/400: `artifacts/candidate_theories.parquet` (10,800 rows), world-level recomputation.
- C3 400/400 known and 100/100 held-out: `artifacts/compositional_candidates.parquet` (16,800 rows), `artifacts/compositional_cost_frontier.parquet`.
- 2,400 candidate verdicts reproduced: `artifacts/nmi_component_audit.json` (`candidate_gate_matches` 2400, `jump_successes` 500/500, `false_jumps` 0/300).
- Grammar-constrained 15/96 vs random 16/96 on same panel: `experiments/nmi_fair_interface_v1/analysis/paired_crand_comparison.csv`.

### Introduction, Related Work (Sections 1-2)
- No numerical claims in this domain. Not reviewed for citation accuracy (outside domain).

### Formal framework (Section 3, Table 1, Figure 1)
- Thresholds: J0/J2 1e-12, J3 0.5, J4 delta 0.1, J5 1e-12 and delta 0.1 match `configs/confirmatory-primary-jump.json` (`gate_thresholds`) and `src/abductive_jump/executable.py` (evaluate_executable gate expressions).
- Lexicographic (observation loss, canonical JSON) comparator selection: `src/abductive_jump/oracle.py:19-21`.
- V(T) conjoined with each of J1-J5: `executable.py` evaluate_executable (`not invalid and ...` on every gate).
- Figure 1 is a schematic; text consistent with Section 3.3.

### Methods (Section 4, Tables 3)
- Eight families x 50 jump / 25 control (AJ5); CJ5 known 50/25 per family plus 100/100 triadic: seed ranges recomputed from candidate tables: AJ5 jump 10000-10049 (50), control 20000-20024 (25); CJ5 known jump 30000-30049, known control 50000-50024, held-out jump 40000-40099, held-out control 60000-60099. Matches S2.
- B1 mutation plans one to three operations: `src/abductive_jump/proposals.py:22-31` (`1 <= len(plan) <= max_steps`, max_steps 3); `conditions.py:72-73` (`max_steps` 3).
- B1 temperature 0.7 vs B0 0.2: `primary_experiment.py:122-123` sets `generation["temperature"] = config["sample_temperature"]` for B1; `configs/confirmatory-primary-jump.json` has `"sample_temperature": 0.7` and generation temperature 0.2. Factorial P0 uses the B1 path (`artifacts/confirmatory/factorial-jump/llm_calls.jsonl` records 2,400 B1_SAMPLE_MATCHED calls) and `configs/confirmatory-factorial-jump.json` has `sample_temperature` 0.7.
- Nine-member portfolio: `proposals.py` `plans` tuple (LATENT_VARIABLE, INVARIANT, REGIME sign_flip, RELATION additive_linear, STATE_VARIABLE additive_state, FUNCTION square, FUNCTION affine_context, CAUSAL_EDGE, TRANSITION) = 9, matching S4.
- 29 generic primitives: `GenericPrimitive` enum has 29 members; `artifacts/generic_primitive_manifest.json` `operators` = 29. 28 without crossover: `fair_interface.py:153,198` excludes SUBGRAPH_CROSSOVER.
- 48 branches, 16 plans per slot, 192 candidate evaluations: `configs/compositional-confirmatory-existing.json` (`search_breadth` 48, `self_plans_per_slot` 16, `primitive_operation_budget` 192); `compositional_jump_results.parquet` `candidate_evaluations` = 192 for C0, C2, C3, C_rand, C_self; 3 for C1 and C5.
- Nine realizer signatures and bases in Table 3 / S8: `src/abductive_jump/compositional_realization.py:77-165` (relation_arity_3 triadic_product; temporally_indexed_recurrence x + history sums; unobserved_dependency raw proxy; unobserved_selector regime-signed; bound_relation scalar vars; self_composed_function; shared_rule_binding x + context; multi_argument_function x, x*context; incumbent_basis first two scalars).
- Phi-4 `microsoft/phi-4` revision `2db69c1c3e91a05d2c64a3185acfbaf36f744e25`, vLLM `vllm/vllm-openai:v0.10.2` (engine_version 0.10.2), `bitsandbytes-4bit`, context 4096, max_tokens 700, temperature 0.2, top_p 0.95: `artifacts/confirmatory/primary-jump/summary.json`, `artifacts/compositional/confirmatory-existing/summary.json`, `artifacts/compositional/confirmatory-heldout/summary.json`.
- DeepSeek `deepseek-ai/DeepSeek-V4-Flash-Vision-Exp` revision `86f746b36186f0e567729a5c06a8c918caba82a9`, vLLM `0.25.2.dev0+g752a3a504.d20260714`, FP8 weights / NVFP4 KV cache: found in `experiments/nmi_minimal_sensitivity_v1/protocol.json`, configs and `experiments/nmi_fair_interface_v1` configs. Transformers 4.56.1 and bitsandbytes 0.47.0 for Phi-4 8-bit: `experiments/nmi_minimal_sensitivity_v1/configs/phi8_cself.json`, `phi8_cself_repair.json`, `protocol.json`.
- Panel: 12 seeds `30014, 30012, 30029, 30025, 30011, 30023, 30000, 30032, 30001, 30037, 30002, 30015`; P2 positive control uses first five, n=40: `experiments/nmi_minimal_sensitivity_v1/panel_manifest.json`.
- Repair trigger 0.25 and triggered: `experiments/nmi_minimal_sensitivity_v1/protocol.json:77-78`.
- Realizer audit: 3,288 slots ((400+100)x3x2 + 96x3), 11 policies, 36,168 candidate-policy rows, 12,056 world-policy rows: `experiments/nmi_realizer_audit_v1/results/candidate_results.parquet` (36,168), `world_results.parquet` (12,056), `summary.json`, `validation.json` (`complete_verified`, zero model calls, zero aligned mismatches).
- Statistics: `BOOTSTRAP_REPLICATES = 10_000`, `BOOTSTRAP_SEED = 20_260_902`, seed XOR sum of character codes of concatenated labels, `p_one_sided = (count<=0 + 1)/(n + 1)`, Holm step-down: `src/abductive_jump/analysis.py:17-18,55,70,91-97`; CJ5 `compositional_analysis.py:19-20,78,93-113,122-130`.
- Family-stratified paired bootstrap resamples seeds within family with equal family weight: `analysis.py:40-68`.

### Results 5.1 (worked example, Figure 2)
- Regenerated `generate_heldout_world(40000)`: world id `h-52dfdb7df153f50fdcb0`; observations (x,z,w)=(6,6,6)->1944, (1,1,1)->9, (2,2,2)->72; incumbent program `cubic_x` k=9; test-0 sets z=7 with x=w=6, incumbent 1944, truth 2268; fals-0 sets z=5, incumbent 1944, truth 1620; a second falsification case fals-1 (w=0 -> 0) exists, matching the caption.
- Archived C3 slot 0 candidate (`artifacts/compositional/confirmatory-heldout/candidate_results.parquet`, `artifacts/compositional_candidates.parquet`): theory hash `def8cd0b...efabe`, signature `relation_arity_3`, expression `9 * ((dax * suv) * wug)`, 6 nodes, 7 edges, ancestry REIFY_EDGE_AS_NODE, CHANGE_ARITY, BIND_ARGUMENT, BIND_ARGUMENT, escape reasons on Relation count/kind/arguments, all J0-J5 true, oracle_cf_loss 104976 = 324^2, candidate losses 0.
- C3 control attrition 900 / 800 / 567 / 283 / 0: `artifacts/nmi_gate_attrition.parquet` and recomputed (known control 500/467/183 + held-out control 300/100/100).
- B4/B5 control through J3 112/110 with 0 at J4: same table.
- Comparator exactness: rerun of `scripts/audit_nmi_control_comparator.py` printed 200 worlds / 1,125 cases, 200 / 1,125, 100 / 500 with `exact_mismatches` 0 and `max_absolute_error` 0.0 (AJ5 1,125; CJ5 1,625). See aij-data-01.

### Results 5.2 (Table 4, Figure 3)
- B4 823/573/270/154; B5 838/562/262/145; B0 65/22/4/1; B1 546/375/118/1: `nmi_gate_attrition.parquet` and recomputed from `candidate_theories.parquet`.
- 35.5% for B4 and B5; bootstrap CI B4 [0.31, 0.4025], B5 [0.31, 0.40]: `artifacts/condition_summary.parquet`.
- Factorial 0/400, 142/400, 400/400: `artifacts/proposal_reasoning_factorial.parquet` (P0_LLM, P1_EXTERNAL, P2_ORACLE).
- Figure 3 whiskers use `jsr_ci_low/high` from `condition_summary.parquet`, produced by `_bootstrap_rate` (family-stratified bootstrap), matching the caption. Panel (b) uses `through_j0..j5` from `nmi_gate_attrition.parquet`.

### Results 5.3 (Table 5, Figure 4)
- C3 vs C_rand estimate 0.87 with CI [0.845, 0.895] (known) and [0.80, 0.93] (held-out): `artifacts/compositional_comparisons.parquet`.
- C_rand 52/400 and 13/100; C1 131/400 (figure); C0, C2, C_self 0: `compositional_cost_frontier.parquet` and recomputation.

### Results 5.4 (Table 6, Figure 5)
- 2,400/2,400 verdicts, 500/500 jump, 0/300 control: `artifacts/nmi_component_audit.json`.

### Results 5.5 (Figure 6)
- Historical C_self: 1,200 non-empty responses, 1,200 at the 700-token cap, strict whole-response JSON 0, 19,200 `plans_must_be_a_list` errors: `experiments/nmi_minimal_sensitivity_v1/offline/historical_cself_attrition.json`.
- Legacy-interface conditions all 0/96 (Wilson 0-3.8%), five paired contrasts all 96 joint failures: `experiments/nmi_minimal_sensitivity_v1/analysis/world_summary.csv`, `paired_world_differences.csv`.
- Grammar-constrained: 4,608/4,608 schema-valid, 3,939 executable (85.5%), 280/288 slots, 236 J1-J2, 21 J3-J5, 15/96 (15.6%, Wilson 9.7-24.2%), meta-law 9/12, unification 6/12: `experiments/nmi_fair_interface_v1/analysis/gate_attrition.csv`, `per_family.csv`, `world_summary.csv`.
- Random 16/96; paired 66/15/14/1: `paired_crand_comparison.csv`.
- P2 3/40 (7.5%, Wilson 2.6-19.9%), coordinate 1/5, hidden regimes 2/5, 4 parse-valid/executable/J1-J2, 3 J3-J5, 116/120 at cap: minimal `world_summary.csv`, `per_family.csv`, `gate_attrition.csv`, `compute_ledger.csv` (finish_reasons length 116, stop 4).

### Results 5.6 (Figure 7)
- Blind binding: C3 347/400 and 100/100; C_rand 57/400 and 13/100; DeepSeek 8/96: `experiments/nmi_realizer_audit_v1/analysis/condition_summary.csv`.
- C3 losses confined to hidden_regimes 26/50 and meta_law 21/50 (53 lost = `paired_transitions.csv` aligned_only 53): `per_family.csv`.
- Masks: relation_arity_3 removes 100 held-out; unobserved_dependency removes 100 known (causal_ambiguity 50 + latent_common_cause 50); bound_relation, multi_argument_function, self_composed_function, temporally_indexed_recurrence, unobserved_selector each 50; shared_rule_binding 0; DeepSeek multi_argument_function 15 -> 0: `condition_summary.csv`, `per_family.csv`, `paired_transitions.csv`. Figure 7(b) computed from these in `build_aij_figures.py:146`.
- DeepSeek blind binding 5/12 meta-law and 3/12 unification (S17): `per_family.csv`.

### Results 5.7
- AJ5 10,800/10,800: `candidate_theories.parquet` `replay_verified` sum = 10,800 of 10,800 rows.
- CJ5 16,800/16,800 with 35,533 ancestry records, 0 mismatches: `artifacts/compositional-replay-validation.json`; `artifacts/composition_ancestry.parquet` has 35,533 rows.
- J0 true for all 10,800 AJ5 and 16,800 CJ5 candidate rows (S3 "no such confirmatory failure occurred").

### Discussion, Limitations, Conclusion
- Numbers reused from Results (15/96, C3 saturation, single held-out family); consistent with the verified values.

### Supplement and declarations
- S9 call counts: AJ5 21,600 primary (10,800 candidates x 2) + 10,800 factorial (`proposal_reasoning_factorial.parquet` llm_calls_used sum) = 32,400; A6 2,400 + 1,200 = 3,600 (`artifacts/confirmatory/ablation-a6-*/summary.json`); CJ5 33,600 (`compositional_jump_results.parquet` llm_calls sum over 800 worlds x 7 conditions). See aij-data-03.
- S10 comparator cases 1,125 / 1,125 / 500: verified by rerun (see 5.1).
- S11 freeze commits `895ebb9...`, `65f2087...`, `7ecb977`, `27ee542`, `ae1ede6...`, `320eb29...`, `f846c89...`, `4606413`, `b6e1561`, `a65974f`, `6bab5fb`, `7753db8` all exist (`git cat-file -t` = commit). Tags map: nmi-phi4-frozen-2026-09 -> ae1ede6; nmi-extension-v1-protocol-freeze -> 4606413; nmi-minimal-sensitivity-v1-protocol-freeze -> 320eb29; amendment-001 -> f846c89; fair-interface protocol-freeze -> b6e1561; shard-freeze -> a65974f; sequential-shards -> 6bab5fb; realizer-audit protocol-freeze -> 7753db8. Branch `nmi-phi4-frozen-archive-2026-09` exists locally and on origin.
- S11 superseded table recomputed from `experiments/nmi_extension_v1/results/*/*_jump/{world_results,llm_self_plans}.parquet`: matched DeepSeek 0/400, 0/100, executable 0/19,200, 0/4,800; phi_constrained (strict-schema) 0/400, 0/100, executable 28/19,200, 1/4,800; phi_repair 0/400, 0/100, executable 0/38,400, 0/9,600. Eight completed shards; `EXTENSION_TERMINATED.json` status superseded, 8 verified shards before stop.
- S11 partial runs: `deepseek_native/known_jump/llm_calls.jsonl` 404 lines; `phi_budget/known_control/llm_calls.jsonl` 1,043 lines; `_incomplete/phi_budget/known_jump_attempt_001_executor_session_terminated/llm_calls.jsonl` 202 lines.
- S12 token totals 231,773 / 237,792 / 2,249,518 / 433,373 / 485,312 / 528,976; calls 576/576/576/864/120/576; native finish reasons length 518, stop 58; 2,772 replay rows with 0 mismatches: minimal `compute_ledger.csv`, `replay_report.json`.
- S12 Phi-budget: 993/4,608 schema-valid, 0 executable (panel); 4,642/19,200 schema-valid, 9 executable, one candidate failing J1 (0/1); held-out 1,289/4,800 and 0: `gate_attrition.csv`, `phi_budget_gate_attrition.csv`.
- S12 Phi-4 8-bit 4,608 JSON-extractable, 0 schema-valid; DeepSeek matched 4,480 non-list + 128 missing: `gate_attrition.csv`, `artifacts/nmi_interface_contract_audit.json`.
- S13: 288 matched responses all use `source`/`target`/`type` keys, strict JSON 0, native reasoning 288 with no answer content: `artifacts/nmi_interface_contract_audit.json`. Throughput pilot 31 calls with 15 non-empty outputs: `experiments/nmi_fair_interface_v1/operational_pilots/serial_runner_excluded/llm_calls.jsonl`. Three starved shards with 4 transport-error records each: `operational_pilots/starved_parallel_shards_excluded/shard_{0,2,3}/llm_calls.jsonl.transport-errors` (4 lines each; the 600-s timeout value itself was not grep-matched in those records, see unresolved).
- S14: 81/15/0/0 with +0.156 for each of three references: `paired_world_differences.csv`; validated signature distribution 21 multi_argument_function, 1 bound_relation, 258 incumbent_basis: `validated_signature_distribution.csv`; deliberation 1,179,648 and serialization 574,538 completion tokens, 288 cap hits vs 0: `compute_ledger.csv`; 576 initial metadata mismatches on `engine`: `results/deepseek_fair_cself/initial_validation.json` (`replay_mismatches` 576, examples `...:deliberation:engine`, `...:serialization:engine`) and `verification_correction_001.json`.
- S17 motif_disabled attrition 1,168/1,500, 1,040/1,500, 236/288 through J2 and 0 at J3: realizer `gate_attrition.csv`.
- S4 B1 audit: 1,200 + 600 candidate rows with `final_representation_hash_matches` 1,200 and 600: `reports/AIJ_CONTRACT_AUDIT.json` (`b1`). S19 name-boundary: 600 AJ5 and 800 CJ5 worlds, `hidden_only_allowlist_names` 0: same file (`variable_names`).
- Cited code lines verified: `conditions.py:196`, `primary_experiment.py:179`, `proposals.py:22`, `representation.py:78` (validate) and `:128` (membership_failures), `expressions.py:17` (validate, max_nodes 64, max_depth 12), `executable.py:69` (allowed_variables), `:109` (theory_consistency), `:143` (freeze_theory), `:166` (evaluate_executable), `compositional_experiment.py:493-590`.
- S20 evidence record: seeds 614800001 / 614800002, ledger lines 6 and 20, phase-one unscaled product `dax*suv*wug`, phase-two `USE_SUPPLIED_REPRESENTATION` / `USE_SUPPLIED_FITTED_EXPRESSION` / test-0, coefficient 9.0, prediction 2268, archived theory hash `def8cd0b...efabe`, replay theory hash changed with gates unchanged, original timestamp and digest null: `manuscript/AIJ_EVIDENCE_RECORD_EXAMPLE.json`. Reproduction commands and archive name: `docs/publication/AIJ_REPRODUCTION.md:15-19`. `LICENSE_SCOPE.md` exists.

## Actionable items

### aij-data-01 (should-fix, traceability)
- Location: Section 5.1, "An offline check verifies that the selected comparator exactly matches every scored control outcome: 1,125 intervention/falsification cases in 200 AJ5 controls and 1,625 in 300 CJ5 controls." and S10 first paragraph.
- Evidence: `scripts/audit_nmi_control_comparator.py` prints JSON to stdout and asserts zero mismatches; no output file is stored in the repository. I reran it (offline, deterministic, no model calls) and obtained 200/1,125, 200/1,125, 100/500 with zero mismatches, so the claim is correct but only reproducible, not archived.
- Proposed change (S10, after "…and 500 in 100 held-out CJ5 controls."): add "The archived output is `reports/AIJ_CONTROL_COMPARATOR_AUDIT.json`." and commit that output. Alternative if no new file is wanted: "The check is rerun from `scripts/audit_nmi_control_comparator.py`; its output is not archived separately."

### aij-data-02 (optional, precision)
- Location: S16, "CJ5 sign-flip tests flip paired world differences under the null, use the finite-replicate correction `(extreme+1)/(replicates+1)` and apply Holm correction within each prospectively specified comparison family."
- Evidence: `src/abductive_jump/compositional_analysis.py:93-113` uses exact enumeration over all 2^k sign patterns when at most 20 paired differences are non-zero (`p_value = extreme / (1 << len(nonzero))`, no +1 correction), and 10,000 random flips with the stated correction otherwise. Every reported contrast has at least 87 discordant worlds (C3-C1 269, C3-C_rand 348, others 400 or 100/87), so the stated formula applied to all reported values. Wording is accurate for reported tests but incomplete as a method description.
- Proposed wording: "CJ5 sign-flip tests flip paired world differences under the null; they use exact enumeration when at most 20 paired differences are non-zero and otherwise 10,000 random sign flips with the finite-replicate correction `(extreme+1)/(replicates+1)`, and apply Holm correction within each prospectively specified comparison family. All reported contrasts used the random-flip branch."

### aij-data-03 (optional, clarity)
- Location: S9, "AJ5 therefore executed 32,400 prospectively specified calls plus 3,600 A6 calls."
- Evidence: 32,400 = 21,600 primary calls (600 worlds x 6 conditions x 3 slots x 2 calls) + 10,800 factorial calls (`proposal_reasoning_factorial.parquet` llm_calls_used sum over 1,800 world-source rows). The sentence does not state that the factorial is included, and the preceding sentence describes only per-cell allocation.
- Proposed wording: "AJ5 therefore executed 32,400 prospectively specified calls (21,600 across B0-B5 and 10,800 in the three-source factorial) plus 3,600 A6 calls."

### aij-data-04 (optional, clarity)
- Location: S20, "This compact excerpt contains actual record values; it is not the full schema-valid record:" followed by the JSON block.
- Evidence: the excerpt keys `raw_call_lines`, `action`, `prediction`, `coefficient`, `archived_theory_hash`, `original_timestamp`, `original_digest`, `replay.model_calls` do not exist verbatim in `manuscript/AIJ_EVIDENCE_RECORD_EXAMPLE.json`; the corresponding values live at `raw_calls[].line`, `fields.action.value`, `fields.prediction.value`, `fields.parameters.value`, `commitment.archived_theory_hash`, `commitment.original_timestamp.value`, `commitment.original_digest.value`, `replay.value.model_calls`. All values are correct.
- Proposed wording: "This compact excerpt paraphrases field paths and reproduces actual record values; it is not the full schema-valid record:"

### aij-data-05 (optional, wording)
- Location: Section 4.4, "served by vLLM 0.10.2 with dynamic bitsandbytes 4-bit quantization".
- Evidence: run manifests record `quantization: bitsandbytes-4bit` only; the word "dynamic" is not evidenced in `artifacts/confirmatory/*/summary.json` or `configs/confirmatory-primary-jump.json`. Unverified rather than contradicted.
- Proposed wording: "served by vLLM 0.10.2 with bitsandbytes 4-bit quantization" (retain "dynamic" only if a serving flag can be cited).

## Sections checked with no issues

Title/abstract; Section 3 and Table 1; Section 4.1-4.3, 4.5 and Table 3; Sections 5.1-5.7, Tables 4-6, Figures 2-7; Sections 6-8; Data and Code availability (local consistency only); S1-S8, S11-S15, S17-S19; declarations. Sections 1-2 and S18 contain no data claims in this domain.

## Unresolved checks and coverage limits

- Remote GitHub release `nmi-github-submission-v4` and the preservation archive checksum were not fetched; only the local tag and the archive name prefix were checked. Unverified.
- The 2,400-verdict deletion replay was verified from `artifacts/nmi_component_audit.json`, not by rerunning `scripts/audit_nmi_components.py`.
- The "600-s timeout" value for the three starved shards (S13) was not matched by grep inside the transport-error records; only the count of four records per shard was verified. Unverified.
- "dynamic" quantization (aij-data-05) unverified.
- Reference accuracy, related-work characterizations, prose quality and the PDF build are outside this domain and were not reviewed.
- tokensave MCP was unavailable (connection closed); source inspection used targeted `rg`/`sed`.

## Three most consequential findings

1. All headline and supplementary numbers, denominators, intervals, figure values and cited code lines trace to frozen artifacts with no contradictions found.
2. aij-data-01: the comparator-exactness check (1,125 / 1,625 cases) is reproducible but its output is not archived in the repository.
3. aij-data-02: the S16 sign-flip description omits an exact-enumeration code branch that was not used for any reported value.

## Evidence index (local paths)

- `artifacts/candidate_theories.parquet`, `artifacts/nmi_gate_attrition.parquet`, `artifacts/condition_summary.parquet`, `artifacts/confirmatory_comparisons.parquet`, `artifacts/proposal_reasoning_factorial.parquet`, `artifacts/per_family_results.parquet`
- `artifacts/compositional_candidates.parquet`, `artifacts/compositional_comparisons.parquet`, `artifacts/compositional_cost_frontier.parquet`, `artifacts/compositional_jump_results.parquet`, `artifacts/composition_ancestry.parquet`, `artifacts/compositional-replay-validation.json`, `artifacts/compositional/confirmatory-heldout/candidate_results.parquet`
- `artifacts/nmi_component_audit.json`, `artifacts/nmi_interface_contract_audit.json`, `artifacts/generic_primitive_manifest.json`
- `artifacts/confirmatory/{primary-jump,primary-control,factorial-jump,ablation-a6-jump,ablation-a6-control}/summary.json`, `artifacts/confirmatory/{primary-jump,primary-control,factorial-jump}/llm_calls.jsonl`
- `configs/confirmatory-primary-jump.json`, `configs/confirmatory-factorial-jump.json`, `configs/compositional-confirmatory-existing.json`
- `experiments/nmi_minimal_sensitivity_v1/{panel_manifest.json,protocol.json}`, `analysis/*`, `offline/historical_cself_attrition.json`, `configs/phi8_cself*.json`
- `experiments/nmi_fair_interface_v1/analysis/*`, `results/deepseek_fair_cself/{validation.json,initial_validation.json,verification_correction_001.json}`, `operational_pilots/*`
- `experiments/nmi_realizer_audit_v1/analysis/*`, `results/{candidate_results.parquet,world_results.parquet,summary.json,validation.json}`
- `experiments/nmi_extension_v1/results/*/*_jump/*.parquet`, `results/EXTENSION_TERMINATED.json`, partial ledgers listed above
- `manuscript/AIJ_EVIDENCE_RECORD_EXAMPLE.json`, `manuscript/figures/aij/*.png`, `manuscript/figures/aij/source_data.json`, `scripts/build_aij_figures.py`, `scripts/audit_nmi_control_comparator.py`, `reports/AIJ_CONTRACT_AUDIT.json` (used only for the S4/S19 audit-count claims it is itself cited for)
- `src/abductive_jump/{oracle,executable,expressions,representation,conditions,primary_experiment,proposals,compositional_experiment,compositional_realization,generic_primitives,fair_interface,analysis,compositional_analysis}.py`
- `docs/publication/AIJ_REPRODUCTION.md`, `LICENSE_SCOPE.md`
