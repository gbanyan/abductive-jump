# AIJ numerical audit

No model inference or new experimental population was run. Historical artifacts are read-only. Empirical assertions and manual protocol review are separate checks.

Automated checks: **244 passed, 0 failed**.

| Claim | Verified value | Canonical source |
|---|---|---|
| B0_DIRECT_LLM success | `1` | `artifacts/condition_summary.parquet` |
| B0_DIRECT_LLM worlds | `400` | `artifacts/condition_summary.parquet` |
| B0_DIRECT_LLM controls | `(200, 0.0)` | `artifacts/condition_summary.parquet` |
| B1_SAMPLE_MATCHED success | `1` | `artifacts/condition_summary.parquet` |
| B1_SAMPLE_MATCHED worlds | `400` | `artifacts/condition_summary.parquet` |
| B1_SAMPLE_MATCHED controls | `(200, 0.0)` | `artifacts/condition_summary.parquet` |
| B2_FIXED_SPACE_AGENT success | `0` | `artifacts/condition_summary.parquet` |
| B2_FIXED_SPACE_AGENT worlds | `400` | `artifacts/condition_summary.parquet` |
| B2_FIXED_SPACE_AGENT controls | `(200, 0.0)` | `artifacts/condition_summary.parquet` |
| B3_ATTRIBUTE_MUTATION success | `0` | `artifacts/condition_summary.parquet` |
| B3_ATTRIBUTE_MUTATION worlds | `400` | `artifacts/condition_summary.parquet` |
| B3_ATTRIBUTE_MUTATION controls | `(200, 0.0)` | `artifacts/condition_summary.parquet` |
| B4_REPRESENTATION_MUTATION success | `142` | `artifacts/condition_summary.parquet` |
| B4_REPRESENTATION_MUTATION worlds | `400` | `artifacts/condition_summary.parquet` |
| B4_REPRESENTATION_MUTATION controls | `(200, 0.0)` | `artifacts/condition_summary.parquet` |
| B5_FULL_SYSTEM success | `142` | `artifacts/condition_summary.parquet` |
| B5_FULL_SYSTEM worlds | `400` | `artifacts/condition_summary.parquet` |
| B5_FULL_SYSTEM controls | `(200, 0.0)` | `artifacts/condition_summary.parquet` |
| P0_LLM factorial | `(400, 0)` | `artifacts/proposal_reasoning_factorial.parquet` |
| P1_EXTERNAL factorial | `(400, 142)` | `artifacts/proposal_reasoning_factorial.parquet` |
| P2_ORACLE factorial | `(400, 400)` | `artifacts/proposal_reasoning_factorial.parquet` |
| C0 known/heldout | `(400, 0, 100, 0)` | `artifacts/compositional_cost_frontier.parquet` |
| C1 known/heldout | `(400, 131, 100, 0)` | `artifacts/compositional_cost_frontier.parquet` |
| C2 known/heldout | `(400, 0, 100, 0)` | `artifacts/compositional_cost_frontier.parquet` |
| C3 known/heldout | `(400, 400, 100, 100)` | `artifacts/compositional_cost_frontier.parquet` |
| C_RAND known/heldout | `(400, 52, 100, 13)` | `artifacts/compositional_cost_frontier.parquet` |
| C_SELF known/heldout | `(400, 0, 100, 0)` | `artifacts/compositional_cost_frontier.parquet` |
| C3/random SECONDARY_EXISTING estimate | `0.87` | `artifacts/compositional_comparisons.parquet` |
| C3/random SECONDARY_EXISTING ci_low | `0.845` | `artifacts/compositional_comparisons.parquet` |
| C3/random SECONDARY_EXISTING ci_high | `0.895` | `artifacts/compositional_comparisons.parquet` |
| C3/random HELDOUT estimate | `0.87` | `artifacts/compositional_comparisons.parquet` |
| C3/random HELDOUT ci_low | `0.8` | `artifacts/compositional_comparisons.parquet` |
| C3/random HELDOUT ci_high | `0.93` | `artifacts/compositional_comparisons.parquet` |
| B0 cumulative gates | `[65, 22, 4, 1, 1]` | `artifacts/nmi_gate_attrition.parquet` |
| B1 cumulative gates | `[546, 375, 118, 1, 1]` | `artifacts/nmi_gate_attrition.parquet` |
| B4 cumulative gates | `[823, 573, 270, 154, 154]` | `artifacts/nmi_gate_attrition.parquet` |
| B5 cumulative gates | `[838, 562, 262, 145, 145]` | `artifacts/nmi_gate_attrition.parquet` |
| B4 control attrition | `[600, 112, 0]` | `artifacts/nmi_gate_attrition.parquet` |
| B5 control attrition | `[600, 110, 0]` | `artifacts/nmi_gate_attrition.parquet` |
| C3 control attrition | `[900, 283, 0]` | `artifacts/nmi_gate_attrition.parquet` |
| C3 controls J1/J2 | `[800, 567]` | `artifacts/nmi_gate_attrition.parquet` |
| C3 replay candidate_gate_matches | `2400` | `artifacts/nmi_component_audit.json` |
| C3 replay candidate_rows | `2400` | `artifacts/nmi_component_audit.json` |
| C3 replay jump_successes | `500` | `artifacts/nmi_component_audit.json` |
| C3 replay jump_worlds | `500` | `artifacts/nmi_component_audit.json` |
| C3 replay control_worlds | `300` | `artifacts/nmi_component_audit.json` |
| C3 replay false_jumps | `0` | `artifacts/nmi_component_audit.json` |
| artifacts/replay-validation.json verified_theories | `10800` | `artifacts/replay-validation.json` |
| artifacts/compositional-replay-validation.json verified_candidates | `16800` | `artifacts/compositional-replay-validation.json` |
| artifacts/compositional-replay-validation.json ancestry_rows | `35533` | `artifacts/compositional-replay-validation.json` |
| artifacts/compositional-replay-validation.json mismatches | `0` | `artifacts/compositional-replay-validation.json` |
| experiments/nmi_minimal_sensitivity_v1/analysis/replay_report.json candidate_rows | `2772` | `experiments/nmi_minimal_sensitivity_v1/analysis/replay_report.json` |
| experiments/nmi_minimal_sensitivity_v1/analysis/replay_report.json mismatches | `0` | `experiments/nmi_minimal_sensitivity_v1/analysis/replay_report.json` |
| experiments/nmi_minimal_sensitivity_v1/analysis/replay_report.json model_calls_made | `0` | `experiments/nmi_minimal_sensitivity_v1/analysis/replay_report.json` |
| experiments/nmi_fair_interface_v1/results/deepseek_fair_cself/replay_report.json candidate_rows | `288` | `experiments/nmi_fair_interface_v1/results/deepseek_fair_cself/replay_report.json` |
| experiments/nmi_fair_interface_v1/results/deepseek_fair_cself/replay_report.json mismatches | `0` | `experiments/nmi_fair_interface_v1/results/deepseek_fair_cself/replay_report.json` |
| experiments/nmi_fair_interface_v1/results/deepseek_fair_cself/replay_report.json model_calls_made | `0` | `experiments/nmi_fair_interface_v1/results/deepseek_fair_cself/replay_report.json` |
| Historical responses/plan opportunities | `[400, 1200, 19200]` | `experiments/nmi_minimal_sensitivity_v1/offline/historical_cself_attrition.json` |
| Historical cap/strict JSON | `[1200, 1200, 0]` | `experiments/nmi_minimal_sensitivity_v1/offline/historical_cself_attrition.json` |
| Grammar plan_schema_valid | `4608` | `experiments/nmi_fair_interface_v1/analysis/analysis.json` |
| Grammar executable | `3939` | `experiments/nmi_fair_interface_v1/analysis/analysis.json` |
| Grammar J1 | `236` | `experiments/nmi_fair_interface_v1/analysis/analysis.json` |
| Grammar J2 | `236` | `experiments/nmi_fair_interface_v1/analysis/analysis.json` |
| Grammar J3 | `21` | `experiments/nmi_fair_interface_v1/analysis/analysis.json` |
| Grammar J4 | `21` | `experiments/nmi_fair_interface_v1/analysis/analysis.json` |
| Grammar J5 | `21` | `experiments/nmi_fair_interface_v1/analysis/analysis.json` |
| deliberation calls/tokens | `[288, 1179648]` | `experiments/nmi_fair_interface_v1/analysis/analysis.json` |
| serialization calls/tokens | `[288, 574538]` | `experiments/nmi_fair_interface_v1/analysis/analysis.json` |
| 96-world paired table | `[66, 15, 14, 1, 16, 15, 96]` | `experiments/nmi_fair_interface_v1/analysis/paired_crand_comparison.csv` |
| Selected executable signature counts | `{'incumbent_basis': 258, 'bound_relation': 1, 'multi_argument_function': 21}` | `experiments/nmi_fair_interface_v1/analysis/validated_signature_distribution.csv` |
| historical_phi4_4bit_cself sensitivity successes | `0` | `experiments/nmi_minimal_sensitivity_v1/analysis/world_summary.csv` |
| phi4_4bit_budget_cself sensitivity successes | `0` | `experiments/nmi_minimal_sensitivity_v1/analysis/world_summary.csv` |
| phi8_cself sensitivity successes | `0` | `experiments/nmi_minimal_sensitivity_v1/analysis/world_summary.csv` |
| deepseek_matched_cself sensitivity successes | `0` | `experiments/nmi_minimal_sensitivity_v1/analysis/world_summary.csv` |
| deepseek_native_cself sensitivity successes | `0` | `experiments/nmi_minimal_sensitivity_v1/analysis/world_summary.csv` |
| phi8_cself_repair sensitivity successes | `0` | `experiments/nmi_minimal_sensitivity_v1/analysis/world_summary.csv` |
| deepseek_p2 sensitivity successes | `3` | `experiments/nmi_minimal_sensitivity_v1/analysis/world_summary.csv` |
| phi8_cself calls/tokens | `(576, 231773)` | `experiments/nmi_minimal_sensitivity_v1/analysis/compute_ledger.csv` |
| deepseek_matched_cself calls/tokens | `(576, 237792)` | `experiments/nmi_minimal_sensitivity_v1/analysis/compute_ledger.csv` |
| deepseek_native_cself calls/tokens | `(576, 2249518)` | `experiments/nmi_minimal_sensitivity_v1/analysis/compute_ledger.csv` |
| phi8_cself_repair calls/tokens | `(864, 433373)` | `experiments/nmi_minimal_sensitivity_v1/analysis/compute_ledger.csv` |
| deepseek_p2 calls/tokens | `(120, 485312)` | `experiments/nmi_minimal_sensitivity_v1/analysis/compute_ledger.csv` |
| phi4_4bit_budget_cself calls/tokens | `(576, 528976)` | `experiments/nmi_minimal_sensitivity_v1/analysis/compute_ledger.csv` |
| Native length/stop | `{'length': 518, 'stop': 58}` | `experiments/nmi_minimal_sensitivity_v1/analysis/compute_ledger.csv` |
| P2 capped calls | `116` | `experiments/nmi_minimal_sensitivity_v1/analysis/compute_ledger.csv` |
| phi4_4bit_budget_cself_full plan_schema_valid | `4642` | `experiments/nmi_minimal_sensitivity_v1/analysis/phi_budget_gate_attrition.csv` |
| phi4_4bit_budget_cself_full executable | `9` | `experiments/nmi_minimal_sensitivity_v1/analysis/phi_budget_gate_attrition.csv` |
| phi4_4bit_budget_cself_heldout plan_schema_valid | `1289` | `experiments/nmi_minimal_sensitivity_v1/analysis/phi_budget_gate_attrition.csv` |
| phi4_4bit_budget_cself_heldout executable | `0` | `experiments/nmi_minimal_sensitivity_v1/analysis/phi_budget_gate_attrition.csv` |
| Fixed-panel budget schema | `993` | `experiments/nmi_minimal_sensitivity_v1/analysis/gate_attrition.csv` |
| P2 parse_valid | `4` | `experiments/nmi_minimal_sensitivity_v1/analysis/gate_attrition.csv` |
| P2 executable | `4` | `experiments/nmi_minimal_sensitivity_v1/analysis/gate_attrition.csv` |
| P2 J1 | `4` | `experiments/nmi_minimal_sensitivity_v1/analysis/gate_attrition.csv` |
| P2 J2 | `4` | `experiments/nmi_minimal_sensitivity_v1/analysis/gate_attrition.csv` |
| P2 J3 | `3` | `experiments/nmi_minimal_sensitivity_v1/analysis/gate_attrition.csv` |
| P2 J4 | `3` | `experiments/nmi_minimal_sensitivity_v1/analysis/gate_attrition.csv` |
| P2 J5 | `3` | `experiments/nmi_minimal_sensitivity_v1/analysis/gate_attrition.csv` |
| C3 known blind binding | `347` | `experiments/nmi_realizer_audit_v1/analysis/condition_summary.csv` |
| C3 heldout blind binding | `100` | `experiments/nmi_realizer_audit_v1/analysis/condition_summary.csv` |
| C_rand known blind binding | `57` | `experiments/nmi_realizer_audit_v1/analysis/condition_summary.csv` |
| C_rand heldout blind binding | `13` | `experiments/nmi_realizer_audit_v1/analysis/condition_summary.csv` |
| DeepSeek_grammar fixed_known_panel blind binding | `8` | `experiments/nmi_realizer_audit_v1/analysis/condition_summary.csv` |
| C3 signature loss relation_arity_3 | `100` | `experiments/nmi_realizer_audit_v1/analysis/condition_summary.csv` |
| C3 signature loss unobserved_dependency | `100` | `experiments/nmi_realizer_audit_v1/analysis/condition_summary.csv` |
| C3 signature loss bound_relation | `50` | `experiments/nmi_realizer_audit_v1/analysis/condition_summary.csv` |
| C3 signature loss multi_argument_function | `50` | `experiments/nmi_realizer_audit_v1/analysis/condition_summary.csv` |
| C3 signature loss self_composed_function | `50` | `experiments/nmi_realizer_audit_v1/analysis/condition_summary.csv` |
| C3 signature loss temporally_indexed_recurrence | `50` | `experiments/nmi_realizer_audit_v1/analysis/condition_summary.csv` |
| C3 signature loss unobserved_selector | `50` | `experiments/nmi_realizer_audit_v1/analysis/condition_summary.csv` |
| C3 signature loss shared_rule_binding | `0` | `experiments/nmi_realizer_audit_v1/analysis/condition_summary.csv` |
| realizer rows | `36168` | `experiments/nmi_realizer_audit_v1/results/candidate_results.parquet` |
| realizer rows | `12056` | `experiments/nmi_realizer_audit_v1/results/world_results.parquet` |
| C3 incumbent substitution J2 | `1168` | `experiments/nmi_realizer_audit_v1/analysis/gate_attrition.csv` |
| C3 incumbent substitution J3 | `0` | `experiments/nmi_realizer_audit_v1/analysis/gate_attrition.csv` |
| C_rand incumbent substitution J2 | `1040` | `experiments/nmi_realizer_audit_v1/analysis/gate_attrition.csv` |
| C_rand incumbent substitution J3 | `0` | `experiments/nmi_realizer_audit_v1/analysis/gate_attrition.csv` |
| DeepSeek_grammar incumbent substitution J2 | `236` | `experiments/nmi_realizer_audit_v1/analysis/gate_attrition.csv` |
| DeepSeek_grammar incumbent substitution J3 | `0` | `experiments/nmi_realizer_audit_v1/analysis/gate_attrition.csv` |
| Panel ordered seeds | `[30014, 30012, 30029, 30025, 30011, 30023, 30000, 30032, 30001, 30037, 30002, 30015]` | `experiments/nmi_minimal_sensitivity_v1/panel_manifest.json` |
| Panel cardinality | `96` | `experiments/nmi_minimal_sensitivity_v1/panel_manifest.json` |
| P2 panel | `40` | `experiments/nmi_minimal_sensitivity_v1/panel_manifest.json` |
| Historical generation | `{'max_tokens': 700, 'temperature': 0.2, 'top_p': 0.95}` | `configs/confirmatory-primary-jump.json` |
| Historical context/temperature | `(4096, 0.7)` | `configs/confirmatory-primary-jump.json` |
| Gate thresholds | `{'delta_cf': 0.1, 'delta_falsification': 0.1, 'epsilon_candidate_obs': 1e-12, 'epsilon_falsification': 1e-12, 'epsilon_obs': 1e-12, 'min_prediction_separation': 0.5}` | `configs/confirmatory-primary-jump.json` |
| Control worlds/cases | `[(200, 1125, 0), (200, 1125, 0), (100, 500, 0)]` | `scripts/audit_nmi_control_comparator.py` |
| Worked example outcomes | `[40000, 2268.0, 1620.0]` | `manuscript/figures/aij/source_data.json` |
| historical_phi4_4bit_cself causal_ambiguity | `(0, 12)` | `experiments/nmi_minimal_sensitivity_v1/analysis/per_family.csv` |
| historical_phi4_4bit_cself coordinate_transform | `(0, 12)` | `experiments/nmi_minimal_sensitivity_v1/analysis/per_family.csv` |
| historical_phi4_4bit_cself hidden_regimes | `(0, 12)` | `experiments/nmi_minimal_sensitivity_v1/analysis/per_family.csv` |
| historical_phi4_4bit_cself latent_common_cause | `(0, 12)` | `experiments/nmi_minimal_sensitivity_v1/analysis/per_family.csv` |
| historical_phi4_4bit_cself meta_law | `(0, 12)` | `experiments/nmi_minimal_sensitivity_v1/analysis/per_family.csv` |
| historical_phi4_4bit_cself property_to_relation | `(0, 12)` | `experiments/nmi_minimal_sensitivity_v1/analysis/per_family.csv` |
| historical_phi4_4bit_cself state_invention | `(0, 12)` | `experiments/nmi_minimal_sensitivity_v1/analysis/per_family.csv` |
| historical_phi4_4bit_cself unification | `(0, 12)` | `experiments/nmi_minimal_sensitivity_v1/analysis/per_family.csv` |
| phi4_4bit_budget_cself causal_ambiguity | `(0, 12)` | `experiments/nmi_minimal_sensitivity_v1/analysis/per_family.csv` |
| phi4_4bit_budget_cself coordinate_transform | `(0, 12)` | `experiments/nmi_minimal_sensitivity_v1/analysis/per_family.csv` |
| phi4_4bit_budget_cself hidden_regimes | `(0, 12)` | `experiments/nmi_minimal_sensitivity_v1/analysis/per_family.csv` |
| phi4_4bit_budget_cself latent_common_cause | `(0, 12)` | `experiments/nmi_minimal_sensitivity_v1/analysis/per_family.csv` |
| phi4_4bit_budget_cself meta_law | `(0, 12)` | `experiments/nmi_minimal_sensitivity_v1/analysis/per_family.csv` |
| phi4_4bit_budget_cself property_to_relation | `(0, 12)` | `experiments/nmi_minimal_sensitivity_v1/analysis/per_family.csv` |
| phi4_4bit_budget_cself state_invention | `(0, 12)` | `experiments/nmi_minimal_sensitivity_v1/analysis/per_family.csv` |
| phi4_4bit_budget_cself unification | `(0, 12)` | `experiments/nmi_minimal_sensitivity_v1/analysis/per_family.csv` |
| phi8_cself causal_ambiguity | `(0, 12)` | `experiments/nmi_minimal_sensitivity_v1/analysis/per_family.csv` |
| phi8_cself coordinate_transform | `(0, 12)` | `experiments/nmi_minimal_sensitivity_v1/analysis/per_family.csv` |
| phi8_cself hidden_regimes | `(0, 12)` | `experiments/nmi_minimal_sensitivity_v1/analysis/per_family.csv` |
| phi8_cself latent_common_cause | `(0, 12)` | `experiments/nmi_minimal_sensitivity_v1/analysis/per_family.csv` |
| phi8_cself meta_law | `(0, 12)` | `experiments/nmi_minimal_sensitivity_v1/analysis/per_family.csv` |
| phi8_cself property_to_relation | `(0, 12)` | `experiments/nmi_minimal_sensitivity_v1/analysis/per_family.csv` |
| phi8_cself state_invention | `(0, 12)` | `experiments/nmi_minimal_sensitivity_v1/analysis/per_family.csv` |
| phi8_cself unification | `(0, 12)` | `experiments/nmi_minimal_sensitivity_v1/analysis/per_family.csv` |
| deepseek_matched_cself causal_ambiguity | `(0, 12)` | `experiments/nmi_minimal_sensitivity_v1/analysis/per_family.csv` |
| deepseek_matched_cself coordinate_transform | `(0, 12)` | `experiments/nmi_minimal_sensitivity_v1/analysis/per_family.csv` |
| deepseek_matched_cself hidden_regimes | `(0, 12)` | `experiments/nmi_minimal_sensitivity_v1/analysis/per_family.csv` |
| deepseek_matched_cself latent_common_cause | `(0, 12)` | `experiments/nmi_minimal_sensitivity_v1/analysis/per_family.csv` |
| deepseek_matched_cself meta_law | `(0, 12)` | `experiments/nmi_minimal_sensitivity_v1/analysis/per_family.csv` |
| deepseek_matched_cself property_to_relation | `(0, 12)` | `experiments/nmi_minimal_sensitivity_v1/analysis/per_family.csv` |
| deepseek_matched_cself state_invention | `(0, 12)` | `experiments/nmi_minimal_sensitivity_v1/analysis/per_family.csv` |
| deepseek_matched_cself unification | `(0, 12)` | `experiments/nmi_minimal_sensitivity_v1/analysis/per_family.csv` |
| deepseek_native_cself causal_ambiguity | `(0, 12)` | `experiments/nmi_minimal_sensitivity_v1/analysis/per_family.csv` |
| deepseek_native_cself coordinate_transform | `(0, 12)` | `experiments/nmi_minimal_sensitivity_v1/analysis/per_family.csv` |
| deepseek_native_cself hidden_regimes | `(0, 12)` | `experiments/nmi_minimal_sensitivity_v1/analysis/per_family.csv` |
| deepseek_native_cself latent_common_cause | `(0, 12)` | `experiments/nmi_minimal_sensitivity_v1/analysis/per_family.csv` |
| deepseek_native_cself meta_law | `(0, 12)` | `experiments/nmi_minimal_sensitivity_v1/analysis/per_family.csv` |
| deepseek_native_cself property_to_relation | `(0, 12)` | `experiments/nmi_minimal_sensitivity_v1/analysis/per_family.csv` |
| deepseek_native_cself state_invention | `(0, 12)` | `experiments/nmi_minimal_sensitivity_v1/analysis/per_family.csv` |
| deepseek_native_cself unification | `(0, 12)` | `experiments/nmi_minimal_sensitivity_v1/analysis/per_family.csv` |
| phi8_cself_repair causal_ambiguity | `(0, 12)` | `experiments/nmi_minimal_sensitivity_v1/analysis/per_family.csv` |
| phi8_cself_repair coordinate_transform | `(0, 12)` | `experiments/nmi_minimal_sensitivity_v1/analysis/per_family.csv` |
| phi8_cself_repair hidden_regimes | `(0, 12)` | `experiments/nmi_minimal_sensitivity_v1/analysis/per_family.csv` |
| phi8_cself_repair latent_common_cause | `(0, 12)` | `experiments/nmi_minimal_sensitivity_v1/analysis/per_family.csv` |
| phi8_cself_repair meta_law | `(0, 12)` | `experiments/nmi_minimal_sensitivity_v1/analysis/per_family.csv` |
| phi8_cself_repair property_to_relation | `(0, 12)` | `experiments/nmi_minimal_sensitivity_v1/analysis/per_family.csv` |
| phi8_cself_repair state_invention | `(0, 12)` | `experiments/nmi_minimal_sensitivity_v1/analysis/per_family.csv` |
| phi8_cself_repair unification | `(0, 12)` | `experiments/nmi_minimal_sensitivity_v1/analysis/per_family.csv` |
| deepseek_p2 causal_ambiguity | `(0, 5)` | `experiments/nmi_minimal_sensitivity_v1/analysis/per_family.csv` |
| deepseek_p2 coordinate_transform | `(1, 5)` | `experiments/nmi_minimal_sensitivity_v1/analysis/per_family.csv` |
| deepseek_p2 hidden_regimes | `(2, 5)` | `experiments/nmi_minimal_sensitivity_v1/analysis/per_family.csv` |
| deepseek_p2 latent_common_cause | `(0, 5)` | `experiments/nmi_minimal_sensitivity_v1/analysis/per_family.csv` |
| deepseek_p2 meta_law | `(0, 5)` | `experiments/nmi_minimal_sensitivity_v1/analysis/per_family.csv` |
| deepseek_p2 property_to_relation | `(0, 5)` | `experiments/nmi_minimal_sensitivity_v1/analysis/per_family.csv` |
| deepseek_p2 state_invention | `(0, 5)` | `experiments/nmi_minimal_sensitivity_v1/analysis/per_family.csv` |
| deepseek_p2 unification | `(0, 5)` | `experiments/nmi_minimal_sensitivity_v1/analysis/per_family.csv` |
| Grammar family causal_ambiguity | `(0, 12)` | `experiments/nmi_fair_interface_v1/analysis/per_family.csv` |
| Grammar family coordinate_transform | `(0, 12)` | `experiments/nmi_fair_interface_v1/analysis/per_family.csv` |
| Grammar family hidden_regimes | `(0, 12)` | `experiments/nmi_fair_interface_v1/analysis/per_family.csv` |
| Grammar family latent_common_cause | `(0, 12)` | `experiments/nmi_fair_interface_v1/analysis/per_family.csv` |
| Grammar family meta_law | `(9, 12)` | `experiments/nmi_fair_interface_v1/analysis/per_family.csv` |
| Grammar family property_to_relation | `(0, 12)` | `experiments/nmi_fair_interface_v1/analysis/per_family.csv` |
| Grammar family state_invention | `(0, 12)` | `experiments/nmi_fair_interface_v1/analysis/per_family.csv` |
| Grammar family unification | `(6, 12)` | `experiments/nmi_fair_interface_v1/analysis/per_family.csv` |
| Binding C3 causal_ambiguity | `50` | `experiments/nmi_realizer_audit_v1/analysis/per_family.csv` |
| Binding C3 coordinate_transform | `50` | `experiments/nmi_realizer_audit_v1/analysis/per_family.csv` |
| Binding C3 hidden_regimes | `26` | `experiments/nmi_realizer_audit_v1/analysis/per_family.csv` |
| Binding C3 latent_common_cause | `50` | `experiments/nmi_realizer_audit_v1/analysis/per_family.csv` |
| Binding C3 meta_law | `21` | `experiments/nmi_realizer_audit_v1/analysis/per_family.csv` |
| Binding C3 property_to_relation | `50` | `experiments/nmi_realizer_audit_v1/analysis/per_family.csv` |
| Binding C3 state_invention | `50` | `experiments/nmi_realizer_audit_v1/analysis/per_family.csv` |
| Binding C3 triadic_relation_reification | `100` | `experiments/nmi_realizer_audit_v1/analysis/per_family.csv` |
| Binding C3 unification | `50` | `experiments/nmi_realizer_audit_v1/analysis/per_family.csv` |
| Binding DeepSeek_grammar causal_ambiguity | `0` | `experiments/nmi_realizer_audit_v1/analysis/per_family.csv` |
| Binding DeepSeek_grammar coordinate_transform | `0` | `experiments/nmi_realizer_audit_v1/analysis/per_family.csv` |
| Binding DeepSeek_grammar hidden_regimes | `0` | `experiments/nmi_realizer_audit_v1/analysis/per_family.csv` |
| Binding DeepSeek_grammar latent_common_cause | `0` | `experiments/nmi_realizer_audit_v1/analysis/per_family.csv` |
| Binding DeepSeek_grammar meta_law | `5` | `experiments/nmi_realizer_audit_v1/analysis/per_family.csv` |
| Binding DeepSeek_grammar property_to_relation | `0` | `experiments/nmi_realizer_audit_v1/analysis/per_family.csv` |
| Binding DeepSeek_grammar state_invention | `0` | `experiments/nmi_realizer_audit_v1/analysis/per_family.csv` |
| Binding DeepSeek_grammar unification | `3` | `experiments/nmi_realizer_audit_v1/analysis/per_family.csv` |
| Superseded complete shards | `8` | `experiments/nmi_extension_v1/results/EXTENSION_TERMINATED.json` |
| Excluded deepseek_matched known_jump worlds | `(400, 0)` | `experiments/nmi_extension_v1/results/deepseek_matched/known_jump/world_results.parquet` |
| Excluded deepseek_matched known_jump plans | `(19200, 0)` | `experiments/nmi_extension_v1/results/deepseek_matched/known_jump/llm_self_plans.parquet` |
| Excluded deepseek_matched heldout_jump worlds | `(100, 0)` | `experiments/nmi_extension_v1/results/deepseek_matched/heldout_jump/world_results.parquet` |
| Excluded deepseek_matched heldout_jump plans | `(4800, 0)` | `experiments/nmi_extension_v1/results/deepseek_matched/heldout_jump/llm_self_plans.parquet` |
| Excluded phi_constrained known_jump worlds | `(400, 0)` | `experiments/nmi_extension_v1/results/phi_constrained/known_jump/world_results.parquet` |
| Excluded phi_constrained known_jump plans | `(19200, 28)` | `experiments/nmi_extension_v1/results/phi_constrained/known_jump/llm_self_plans.parquet` |
| Excluded phi_constrained heldout_jump worlds | `(100, 0)` | `experiments/nmi_extension_v1/results/phi_constrained/heldout_jump/world_results.parquet` |
| Excluded phi_constrained heldout_jump plans | `(4800, 1)` | `experiments/nmi_extension_v1/results/phi_constrained/heldout_jump/llm_self_plans.parquet` |
| Excluded phi_repair known_jump worlds | `(400, 0)` | `experiments/nmi_extension_v1/results/phi_repair/known_jump/world_results.parquet` |
| Excluded phi_repair known_jump plans | `(38400, 0)` | `experiments/nmi_extension_v1/results/phi_repair/known_jump/llm_self_plans.parquet` |
| Excluded phi_repair heldout_jump worlds | `(100, 0)` | `experiments/nmi_extension_v1/results/phi_repair/heldout_jump/world_results.parquet` |
| Excluded phi_repair heldout_jump plans | `(9600, 0)` | `experiments/nmi_extension_v1/results/phi_repair/heldout_jump/llm_self_plans.parquet` |
| Excluded partial call records | `404` | `experiments/nmi_extension_v1/results/deepseek_native/known_jump/llm_calls.jsonl` |
| Excluded partial call records | `1043` | `experiments/nmi_extension_v1/results/phi_budget/known_control/llm_calls.jsonl` |
| Excluded partial call records | `202` | `experiments/nmi_extension_v1/results/_incomplete/phi_budget/known_jump_attempt_001_executor_session_terminated/llm_calls.jsonl` |
| Excluded throughput pilot | `(31, 8, 15)` | `experiments/nmi_fair_interface_v1/operational_pilots/serial_runner_excluded/llm_calls.jsonl` |
| Timeout-only shard 0 | `4` | `experiments/nmi_fair_interface_v1/operational_pilots/starved_parallel_shards_excluded/shard_0/llm_calls.jsonl.transport-errors` |
| Timeout-only shard 2 | `4` | `experiments/nmi_fair_interface_v1/operational_pilots/starved_parallel_shards_excluded/shard_2/llm_calls.jsonl.transport-errors` |
| Timeout-only shard 3 | `4` | `experiments/nmi_fair_interface_v1/operational_pilots/starved_parallel_shards_excluded/shard_3/llm_calls.jsonl.transport-errors` |
| Initial metadata mismatches | `576` | `experiments/nmi_fair_interface_v1/results/deepseek_fair_cself/initial_replay_report.json` |
| Corrected manifests | `4` | `experiments/nmi_fair_interface_v1/results/deepseek_fair_cself/verification_correction_001.json` |
| DeepSeek runtime deliberation | `('0.25.2.dev0+g752a3a504.d20260714', 'fp8-weights+nvfp4-kv-cache')` | `experiments/nmi_fair_interface_v1/results/deepseek_fair_cself/verification_correction_001.json` |
| DeepSeek runtime serialization | `('0.25.2.dev0+g752a3a504.d20260714', 'fp8-weights+nvfp4-kv-cache')` | `experiments/nmi_fair_interface_v1/results/deepseek_fair_cself/verification_correction_001.json` |
| Phi8 runtime | `transformers-4.56.1+bitsandbytes-0.47.0` | `experiments/nmi_minimal_sensitivity_v1/results/phi8_cself/summary.json` |
| Freeze commit 27ee542 | `True` | `Git object database` |
| Freeze commit 320eb29b33ddaed596b0fe7b3f1d5895c706f311 | `True` | `Git object database` |
| Freeze commit 4606413 | `True` | `Git object database` |
| Freeze commit 65f20874e16bddf8a7ae36996395ff52b27153b7 | `True` | `Git object database` |
| Freeze commit 6bab5fb | `True` | `Git object database` |
| Freeze commit 7753db8 | `True` | `Git object database` |
| Freeze commit 7ecb977 | `True` | `Git object database` |
| Freeze commit 895ebb9118ffd0046825b88868621f2a70f69f61 | `True` | `Git object database` |
| Freeze commit a65974f | `True` | `Git object database` |
| Freeze commit ae1ede683fdef09f2bf60f6e1052b60394ad6cf8 | `True` | `Git object database` |
| Freeze commit b6e1561 | `True` | `Git object database` |
| Freeze commit f846c89287e379fe313551c47765c24f2abf4959 | `True` | `Git object database` |

## Manual numerical/protocol review

Main Sections 3–4: gate thresholds and validity prerequisites checked against executable.py/gates.py; comparator selection against oracle.py; opportunity counts against frozen configs. The validity prerequisite V(T) was made explicit during this audit. Main Section 5 and figure captions: counts, intervals and denominators checked above. Percentages are arithmetic from world/plan counts, not candidate-level inferential estimates.

Supplement S1–S8: seed ranges, 29/28 primitive distinction, 48 × four-step paths, three retained slots, 16 plans/slot, nine realizer signatures and thresholds checked against configs, protocol files, generic primitive manifest and composition.py. S9–S10: archived call counts and bootstrap settings checked against historical summaries, analysis.py and compositional_analysis.py; tail quantities retain their non-P interpretation.

Supplement S11–S17: panel seeds, token counts, attrition, replay, per-family cells and signature effects checked against the analysis CSV/JSON and frozen protocol/runtime manifests. Operational counts and excluded runs are additionally audited in the accompanying source inventory. Commit hashes and version strings are identifiers, not experimental estimates. References and dates are handled by the citation audit.

No empirical estimate required a new experiment. The inherited phrase 'DOI archive' was corrected to the actual public preservation archive; no DOI deposit is claimed. The main-text runtime cross-reference was corrected from S11 to S15.

## Input SHA-256

- `artifacts/compositional-replay-validation.json`: `54b6a1d2c4a67ff4a049911c4c3f63f3ee26795b062e31a781b6175cd6ceba21`
- `artifacts/compositional_comparisons.parquet`: `229cea78f02e52888e5404e91110db3c4051f7af6246ac9449de8c71879cc156`
- `artifacts/compositional_cost_frontier.parquet`: `ffbf03364fc176d361c623e8e7c5689f85d6f9f16cb03efda695d62bc879c07a`
- `artifacts/condition_summary.parquet`: `b9a098697e6bc51fdaf2b4d12e6539653d2e1c249b22e8ea963fd7cbfbe88700`
- `artifacts/nmi_component_audit.json`: `8db13020a227460556fac04897f8af115fe4621cd202bba239af6179a16fc447`
- `artifacts/nmi_gate_attrition.parquet`: `cbb9de97b97ab2e53cd2c50c0f017eb1345fc96a8cd4b133cd19dcb97cb51a16`
- `artifacts/proposal_reasoning_factorial.parquet`: `2981b9f51a9799d08ccef0ad0a823902f9f1850d700fc9d44c3c65983e57f9c8`
- `artifacts/replay-validation.json`: `bf9bd3dfcc0d9874006ed16739bae075dbad25ce727dd9b86be88744a0c24d09`
- `configs/confirmatory-primary-jump.json`: `9c83d26b5faf4d3795d99949c5f4aae2762f66f1454e7f8a93d24444ea9d0699`
- `experiments/nmi_extension_v1/results/EXTENSION_TERMINATED.json`: `67ce3fadf877f685f52e75e3b4307201e89c82da39036fe3342f9ab483d03457`
- `experiments/nmi_extension_v1/results/_incomplete/phi_budget/known_jump_attempt_001_executor_session_terminated/llm_calls.jsonl`: `4c6abe366e695f8e3649af0362533f28372bdccf52d5b6149aed35317dbadadc`
- `experiments/nmi_extension_v1/results/deepseek_matched/heldout_jump/llm_self_plans.parquet`: `048bbd95f408aadeac6d760f71f09238627da9ba2d454fcc5e308ee293e3cae3`
- `experiments/nmi_extension_v1/results/deepseek_matched/heldout_jump/world_results.parquet`: `a92bb692f4e271a93d86acc3c5092eb8cf33110176077683642529368d1de4ac`
- `experiments/nmi_extension_v1/results/deepseek_matched/known_jump/llm_self_plans.parquet`: `c42c58f89b5b92415a51e30954f62079c34ed2df0e6026813177faede8cd449d`
- `experiments/nmi_extension_v1/results/deepseek_matched/known_jump/world_results.parquet`: `d33e4d9f70e7f171248fae1681824a59b91a0b31de331ff8fa560d5b9be22511`
- `experiments/nmi_extension_v1/results/deepseek_native/known_jump/llm_calls.jsonl`: `2e01fa25ba5ba2a1df17551139294240677a03ba7b1dd86ad3bb32d89b388473`
- `experiments/nmi_extension_v1/results/phi_budget/known_control/llm_calls.jsonl`: `53bde76ea42f494026e5d240cb31ece486c6ba28710dec4a809e62c564fd62cc`
- `experiments/nmi_extension_v1/results/phi_constrained/heldout_jump/llm_self_plans.parquet`: `71e06d3eb7aac7bee261f41205669d9cc7e67f8e34c549c3ec0800212f0d6c0a`
- `experiments/nmi_extension_v1/results/phi_constrained/heldout_jump/world_results.parquet`: `c226291514f6c63bf48c7afc2b13fbe41a701ff653ce46630b0a33f77123a539`
- `experiments/nmi_extension_v1/results/phi_constrained/known_jump/llm_self_plans.parquet`: `02a73f25cf5918f300ef2b946738c8d16ab0082581db926216f1282e45c1917f`
- `experiments/nmi_extension_v1/results/phi_constrained/known_jump/world_results.parquet`: `a167011e3cfd9e829a262b67f29b8c8e252dca16b4058ba774871816e21d8e0a`
- `experiments/nmi_extension_v1/results/phi_repair/heldout_jump/llm_self_plans.parquet`: `0b858bc75fbd91e2462a58e8571d4c36595f5dd8675076e7162c5a133270af20`
- `experiments/nmi_extension_v1/results/phi_repair/heldout_jump/world_results.parquet`: `47ad560770ecdb1daaac4735cd019600c348de1e5b71e649aa3ab431bc66108c`
- `experiments/nmi_extension_v1/results/phi_repair/known_jump/llm_self_plans.parquet`: `3748673514514019bcdd331abf422058ac88da5d4b8f197a03b7eb6dda1a52d5`
- `experiments/nmi_extension_v1/results/phi_repair/known_jump/world_results.parquet`: `6fbe864a8cd4d11b38c9bc3aa7bfc7873e6f4dfb8654848c2b30d8acbd0de1ab`
- `experiments/nmi_fair_interface_v1/analysis/analysis.json`: `36c20cbc7baeda3af22fb7f13ff39ecb0af448770ba24a75f6ed80c6cbd165bc`
- `experiments/nmi_fair_interface_v1/analysis/paired_crand_comparison.csv`: `ae52d73a18346cf00d4b9830f353869723cf5da9ccec5e26c8fa8b7f51fa0280`
- `experiments/nmi_fair_interface_v1/analysis/per_family.csv`: `2c39449027951e241f328ae2f285544486efd26fea49ab8d18c2ac5b04612832`
- `experiments/nmi_fair_interface_v1/analysis/validated_signature_distribution.csv`: `4d8463dcbdca4e77a80b08b874faab37f6352982d00476487187d1c5df118dce`
- `experiments/nmi_fair_interface_v1/operational_pilots/serial_runner_excluded/llm_calls.jsonl`: `519e7f2b530c40a0b37f12a486dbb0fa5b08ac60a09557b51d57b7903ba888a8`
- `experiments/nmi_fair_interface_v1/operational_pilots/starved_parallel_shards_excluded/shard_0/llm_calls.jsonl.transport-errors`: `d4d89ea54dd66a22a6411ac61f28766c1ab408cd88821f3caed28401756872c0`
- `experiments/nmi_fair_interface_v1/operational_pilots/starved_parallel_shards_excluded/shard_2/llm_calls.jsonl.transport-errors`: `6423cc052e5c0ad8e4efc883f468e40679c85b7cb844f33bb337100cc7a41640`
- `experiments/nmi_fair_interface_v1/operational_pilots/starved_parallel_shards_excluded/shard_3/llm_calls.jsonl.transport-errors`: `94a50a7c8613e5bc9174e949612b6563988f896012b18a8141f8ecac7b20d82d`
- `experiments/nmi_fair_interface_v1/results/deepseek_fair_cself/initial_replay_report.json`: `d45d0066d4bb4791d4b4d5360dcfecb9757fa4551fd6d2c1d562a30b95154fbd`
- `experiments/nmi_fair_interface_v1/results/deepseek_fair_cself/replay_report.json`: `ece57c06e0518f4fad1101c298ff706c8e6e3ffffc6d84d68214204cb54a57a2`
- `experiments/nmi_fair_interface_v1/results/deepseek_fair_cself/verification_correction_001.json`: `2d939e3bffd39824ffec87de7825459c4d25b2bd9f8a5199f031d6839b637d94`
- `experiments/nmi_minimal_sensitivity_v1/analysis/compute_ledger.csv`: `1f654caeb3dac1d7bb01818bdec7e4f74280281bd8f0f7c02abf99f477e321f7`
- `experiments/nmi_minimal_sensitivity_v1/analysis/gate_attrition.csv`: `9a4e3bb6e61403f11ca82273055c2d7766e86ad08d8ba1416e554205e0099880`
- `experiments/nmi_minimal_sensitivity_v1/analysis/per_family.csv`: `799374a531aa141fc3736e7a5e575c2be70a2ba7f9b3d5117a569814b999caca`
- `experiments/nmi_minimal_sensitivity_v1/analysis/phi_budget_gate_attrition.csv`: `b32f2711626b05263b9989d3b0e0c391ebb9ea7d64631c2598fd2b8a29d29841`
- `experiments/nmi_minimal_sensitivity_v1/analysis/replay_report.json`: `580e5b8b21e0366d2da7fe0b28383e63de3101cd6198d9777feb87233600ac18`
- `experiments/nmi_minimal_sensitivity_v1/analysis/world_summary.csv`: `0ba2d121beb644100287cc7b9e0722cc4ab1f29ff4a3a44cfdaf247e5b7cefbf`
- `experiments/nmi_minimal_sensitivity_v1/offline/historical_cself_attrition.json`: `4da8832b950d7a186504dbe136c1ac4e7a09e93122eaa0f68ab40fa849821626`
- `experiments/nmi_minimal_sensitivity_v1/panel_manifest.json`: `2db121341f79c41c1c53cf4b61d4deba2af475f297dba0dc3106924e09b522b9`
- `experiments/nmi_minimal_sensitivity_v1/results/phi8_cself/summary.json`: `eaefa3b3344fea9da4f34411e3e73f7514088e31c6441c6afd844bcfcac13ba8`
- `experiments/nmi_realizer_audit_v1/analysis/condition_summary.csv`: `4daeb3c5bfd1663e91f86b530bce3a74e6864e8e2226b893c20d6c89dbc118d6`
- `experiments/nmi_realizer_audit_v1/analysis/gate_attrition.csv`: `248bc5124f915407128b08d806f6ccc846aafa7b7318a481849be77c5f141140`
- `experiments/nmi_realizer_audit_v1/analysis/per_family.csv`: `d3f3ac7e2d2f87927ae79424bbc31c71b66dbfcc92888eae54fa35b5629fe866`
- `experiments/nmi_realizer_audit_v1/results/candidate_results.parquet`: `202d52c7fee2a162bc84567e7cda00cadf919b30d1f0c662bc59e2c41367cbd1`
- `experiments/nmi_realizer_audit_v1/results/world_results.parquet`: `de8bf3ef53769d4a9d07d7059109540688f95a660d00a8580255ad96d6d0107c`
- `manuscript/figures/aij/source_data.json`: `ee1c8bc139fa76a00cc1a8bdcd8c501f1d545952f29fd53947287e31bb57ca4e`
