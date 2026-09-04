# NMI Evidence Source Map

Verified 4 September 2026. The hierarchy used here is: frozen preregistration; canonical raw artifact or manifest; deterministic synthesis script; final phase report; Reviewer #2 report; research ledger; summary prose. Canonical artifacts prevail over prose.

| Claim | Exact number | Source file | Rows/worlds | Script | Commit | Verified? |
| --- | ---: | --- | ---: | --- | --- | --- |
| AJ5 primary population | 400 jump; 200 no-jump worlds across 8 families | `docs/abductive-jump-preregistration.md`; `artifacts/world_manifest.parquet` | 600 worlds | `experiment.py` | `895ebb9` freeze | Yes |
| Direct LLM JSR | 1/400 (0.25%) | `artifacts/condition_summary.parquet` | 400 worlds | `analysis.py` | `dd6e82c` | Yes |
| Sample-matched LLM JSR | 1/400 (0.25%) | `artifacts/condition_summary.parquet` | 400 worlds | `analysis.py` | `dd6e82c` | Yes |
| Fixed-space agent JSR | 0/400 (0%) | `artifacts/condition_summary.parquet` | 400 worlds | `analysis.py` | `dd6e82c` | Yes |
| Attribute/value mutation JSR | 0/400 (0%) | `artifacts/condition_summary.parquet` | 400 worlds | `analysis.py` | `dd6e82c` | Yes |
| Representation mutation JSR | 142/400 (35.5%) | `artifacts/condition_summary.parquet` | 400 worlds | `analysis.py` | `dd6e82c` | Yes |
| Representation mutation plus QD JSR | 142/400 (35.5%) | `artifacts/condition_summary.parquet` | 400 worlds | `analysis.py` | `dd6e82c` | Yes |
| AJ5 family coverage | B4 and B5 each succeed in 8/8 families | `artifacts/per_family_results.parquet` | 48 condition-family rows | `analysis.py` | `dd6e82c` | Yes |
| AJ5 no-jump result | 0/200 per condition; Wilson 95% upper bound 0.0188453 | `artifacts/condition_summary.parquet` | 1,200 condition-world rows | `analysis.py` | `dd6e82c` | Yes |
| Proposal–reasoning factorial | P0 0/400; P1 142/400; P2 400/400 | `artifacts/proposal_reasoning_factorial.parquet` | 1,800 rows | `analysis.py` | `dd6e82c` | Yes |
| AJ5 primary comparisons | all 8 unadjusted P=9.999e-5; Holm P=7.9992e-4 | `artifacts/confirmatory_comparisons.parquet` | 8 tests | `analysis.py` | `dd6e82c` | Yes |
| AJ5 dose response | B4: 53/400, 101/400, 142/400; B5: 58/400, 96/400, 142/400 at 1–3 slots | `artifacts/compute_quality_frontier.parquet` | 6 macro rows | `analysis.py` | `dd6e82c` | Yes |
| AJ5 replay | 10,800/10,800 candidates; 0 mismatches | `artifacts/replay-validation.json` | 10,800 candidates | `replay.py` | `dd6e82c` | Yes |
| AJ5 inference traces | 32,400 preregistered; 3,600 triggered A6 | `artifacts/reproducibility-manifest.json` | 36,000 calls | `reproducibility.py` | `dd6e82c` | Yes |
| CJ5 populations | 400 known and 100 held-out jump; 200 known and 100 held-out no-jump worlds | four compositional run audits | 800 worlds × 7 conditions | `compositional_run_audit.py` | `be3cf3b` | Yes |
| Structured generic composition JSR | 400/400 known; 100/100 held out | `artifacts/compositional_jump_results.parquet` | 500 worlds | `compositional_analysis.py` | `be3cf3b` | Yes |
| Single generic rewrite JSR | 0/400 known; 0/100 held out | `artifacts/compositional_jump_results.parquet` | 500 worlds | `compositional_analysis.py` | `be3cf3b` | Yes |
| Atomic high-level reference JSR | 131/400 known; 0/100 held out | `artifacts/compositional_jump_results.parquet` | 500 worlds | `compositional_analysis.py` | `be3cf3b` | Yes |
| Random primitive composition JSR | 52/400 known; 13/100 held out | `artifacts/compositional_jump_results.parquet` | 500 worlds | `compositional_analysis.py` | `be3cf3b` | Yes |
| LLM self-composition JSR | 0/400 known; 0/100 held out | `artifacts/compositional_jump_results.parquet` | 500 worlds | `compositional_analysis.py` | `be3cf3b` | Yes |
| C3 versus random | +0.87 known, 95% bootstrap CI [0.845, 0.895]; +0.87 held out, CI [0.80, 0.93]; Holm P=0.00029997 for each | `artifacts/compositional_comparisons.parquet` | 400 and 100 paired worlds | `compositional_analysis.py` | `be3cf3b` | Yes |
| CJ5 no-jump result | C3 0/300; combined Wilson 95% upper bound 0.012643; every condition 0 false jumps | `artifacts/no_jump_depth_controls.parquet`; `artifacts/final_compositional_verdict.json` | 300 worlds per condition | `compositional_analysis.py` | `be3cf3b` | Yes |
| Successful C3 depth | all 500 successful worlds have a depth-4 candidate; all validated C3 candidates have ancestry depth 4 | `artifacts/compositional_candidates.parquet` | 500 worlds; 450 validated known-family candidate rows plus 100 held-out rows | `compositional_analysis.py` | `be3cf3b` | Yes |
| Bounded reachability | 90/90 reachable; 0/17,280 depth-one jumps | `artifacts/minimum_edit_depth.parquet`; `artifacts/depth_one_admissibility.parquet` | 90 worlds; 17,280 candidates | `composition_reachability.py` | `7ecb977` | Yes |
| Retained jump gain | rho_J=3.053435; 95% bootstrap CI [2.684564, 3.539823] | `artifacts/final_compositional_verdict.json` | 400 paired known-family worlds | `compositional_analysis.py` | `be3cf3b` | Yes |
| CJ5 replay | 16,800/16,800 candidates; 0 mismatches; 35,533 ancestry rows | `artifacts/compositional-replay-validation.json` | 16,800 candidates | `compositional_replay.py` | `be3cf3b` | Yes |
| CJ5 inference traces | 33,600 exact unique calls | `artifacts/compositional-reproducibility-manifest.json` | 33,600 calls | `compositional_reproducibility.py` | `be3cf3b` | Yes |
| Held-out seal | unlock only after both known-family shards were terminal and audited | `research-ledger.md`; `artifacts/compositional-execution-source-audit.json` | chronology | ledger and verifier | `27ee542` unlock | Yes |
| Historical Phi-4 C_self response attrition | 1,200/1,200 responses returned and non-empty; 0/1,200 strict complete JSON; 0/19,200 executable plan opportunities; all 1,200 responses reached the 700-token completion cap | `experiments/nmi_minimal_sensitivity_v1/offline/historical_cself_attrition.json`; historical `llm_calls.jsonl` and `llm_self_plans.parquet` | 400 worlds, 1,200 responses, 19,200 plans | `scripts/analyze_historical_cself_attrition.py` | `320eb29` protocol freeze | Yes |
| Model-free C3 replay | 500/500 jump successes and 0/300 controls are unchanged when the model response is replaced by an empty explanation | `artifacts/nmi_component_audit.json`; `docs/nmi_component_audit.md` | 800 worlds | `scripts/audit_nmi_components.py` | post-confirmatory audit | Yes |
| Fair grammar-constrained autonomous sensitivity | 15/96 worlds pass J1--J5; 21 validated candidates all use `multi_argument_function` | `experiments/nmi_fair_interface_v1/analysis/report.md`; `validated_signature_distribution.csv` | 96 worlds, 8 families | fair-interface analysis | post-confirmatory sensitivity | Yes |
| Fair sensitivity versus historical random composition | fair 15/96; C_rand 16/96; paired outcomes: 66 neither, 15 C_rand only, 14 fair only, 1 both | `experiments/nmi_fair_interface_v1/analysis/paired_crand_comparison.csv` | same 96 worlds | deterministic paired join | post-confirmatory sensitivity | Yes |
| Completed superseded broad-extension shards | DeepSeek matched: 0/400 known and 0/100 held out; Phi constrained: 0/400 and 0/100; Phi repair: 0/400 and 0/100 | `docs/publication/NMI_SUPERSEDED_EXTENSION_DISCLOSURE.md`; raw ledgers in `experiments/nmi_extension_v1/results/` | six completed shards | validation/replay scripts listed in disclosure | superseded extension | Yes |
| Realizer audit aligned replay | all 3,288 archived candidate slots reproduce their gates and world verdicts with zero mismatches; zero model calls | `experiments/nmi_realizer_audit_v1/results/validation.json` | 36,168 candidate-policy rows; 12,056 world-policy rows | `scripts/run_nmi_realizer_audit_v1.py`; `scripts/verify_nmi_realizer_audit_v1.py` | `7753db8` protocol freeze | Yes |
| Motif-disabled counterfactual | C3 0/400 known and 0/100 held out; C_rand 0/400 and 0/100; grammar-constrained DeepSeek 0/96 | `experiments/nmi_realizer_audit_v1/analysis/condition_summary.csv`; `report.md` | 1,096 worlds from fixed archived candidates | `scripts/analyze_nmi_realizer_audit_v1.py` | `7753db8` protocol freeze | Yes |
| Role/action-blind binding | C3 347/400 known and 100/100 held out; C_rand 57/400 and 13/100; grammar-constrained DeepSeek 8/96 | `experiments/nmi_realizer_audit_v1/analysis/condition_summary.csv`; `per_family.csv` | 1,096 worlds from fixed archived candidates | `scripts/analyze_nmi_realizer_audit_v1.py` | `7753db8` protocol freeze | Yes |

Partial or infrastructure-terminated shards remain excluded from inferential claims. No partial result may be promoted into a manuscript claim.

No headline number may enter the manuscript unless it appears above or is added with equivalent canonical evidence.
