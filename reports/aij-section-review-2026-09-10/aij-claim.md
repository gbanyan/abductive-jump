# AIJ manuscript review: aij-claim (overclaim, evidence vs conclusions, causal attribution, LLM capability, fairness of comparisons)

- Reviewer: aij-claim (one of five independent domain reviewers)
- Date: 2026-09-10
- HEAD reviewed: `0214bc592aa55c92e5aaeffd298fbe22b07f3e3c` on branch `nmi-minimal-targeted-sensitivity-v1` (uncommitted NMI-side changes present and untouched)
- Files reviewed: `manuscript/AIJ_MANUSCRIPT.md` (424 lines), `manuscript/AIJ_SUPPLEMENTARY_METHODS.md` (263 lines), `manuscript/AIJ_COVER_LETTER.md`, figures in `manuscript/figures/aij/` (figure_2_aj5, figure_3_cj5, figure_4_provenance, figure_5_interface, figure_6_realizer viewed; figure_1 and figure_7 caption arithmetic only)
- Read-only review. No manuscript, code, data or git changes were made. No experiments run. Prior `reports/AIJ_*` treated as background only.
- Tooling note: tokensave MCP failed to connect; code checks used targeted reads of `src/abductive_jump/` and pyarrow reads of frozen parquet/CSV artifacts.

## Independent verification performed (numbers reproduced from frozen artifacts)

All headline numbers in this domain reproduced from the frozen tables:

- `artifacts/condition_summary.parquet`: B0 1/400, B1 1/400, B2 0, B3 0, B4 142/400 (35.5%, CI 0.31-0.4025), B5 142/400.
- `artifacts/nmi_gate_attrition.parquet`: B0 65/22/4/1; B1 546/375/118/1; B4 823/573/270/154; B5 838/562/262/145; B4/B5 control J3 112/110, J4 0; C3 controls 800/567/283/0 of 900; C_self 0 through J1.
- `artifacts/proposal_reasoning_factorial.parquet`: P0 0/400, P1 142/400, P2 400/400 (controls 0/200 each).
- `artifacts/compositional_comparisons.parquet`: C3-C_rand 0.87 [0.845, 0.895] known, 0.87 [0.80, 0.93] held-out.
- `artifacts/nmi_component_audit.json`: 2,400/2,400 verdict matches, 500/500 jump, 0/300 control; C_self 38,400 plan records all `plans_must_be_a_list`.
- `experiments/nmi_fair_interface_v1/analysis/*`: 4,608 schema-valid, 3,939 executable, 280/288 slots, 236 J1-J2, 21 J3-J5, 15/96 (Wilson 9.7-24.2%), meta-law 9/12, unification 6/12; paired vs C_rand 66/15/14/1, C_rand 16/96; all 21 validated candidates `multi_argument_function`; 258 incumbent_basis, 1 bound_relation.
- `experiments/nmi_realizer_audit_v1/analysis/*`: blind binding C3 347/400 and 100/100; C_rand 57/400 and 13/100; DeepSeek 8/96; signature masks (triadic 100 held-out; unobserved_dependency 100 known = latent common cause 50 + causal ambiguity 50; five signatures 50 each; shared_rule_binding 0); motif_disabled 0 everywhere. Paired transitions for C_rand blind binding: aligned_only 10, counterfactual_only 15, paired difference +0.010.
- `experiments/nmi_minimal_sensitivity_v1/analysis/per_family.csv`: DeepSeek P2 1/5 coordinate_transform, 2/5 hidden_regimes, 0/5 elsewhere (3/40).
- Panel-restricted recomputation from `artifacts/compositional_jump_results.parquet` (12 panel seeds x 8 families): C_rand 16/96 = property_to_relation 10/12, coordinate_transform 3/12, meta_law 2/12, unification 1/12, others 0/12. C3 96/96.
- Row-count arithmetic: 3,288 slots = 1,500 + 1,500 + 288; 36,168 = 3,288 x 11; 12,056 = 1,096 x 11. Worked example: 9*6*6*6 = 1,944; 9*6*7*6 = 2,268; 9*6*5*6 = 1,620.

Code facts established:

- Grammar-constrained condition selects per slot the max-score plan among 16 evaluated plans: `src/abductive_jump/fair_interface_experiment.py:171-173` (same rule as C_self, `src/abductive_jump/compositional_experiment.py:477-480`). Score tuple defined at `src/abductive_jump/composition_search.py:53-74` (compatible/complete/escaped, separation > 0.5, separation, escaped, novelty, operator diversity, -loss; computed from public observations and public actions only).
- C_rand selects 3 of 48 paths by structural-hash sort with no evaluation-based ranking: `src/abductive_jump/composition_search.py:480-483`.
- AJ5 runner (all B conditions) fits the expression deterministically and overwrites the model's expression and selected intervention before evaluation: `src/abductive_jump/primary_experiment.py:200-259` (`payload["expression"] = fitted.expression.tree`; `payload["selected_intervention_ids"] = [exact_choice]`).
- Supplied-representation control declares model-authored expression, explanation and selected_intervention_ids with representation the only overwrite: `src/abductive_jump/supplied_representation_experiment.py:28,153-154`.

External sources fetched (2026-09-10):

- https://arxiv.org/abs/2608.09696v4 and https://arxiv.org/html/2608.09696v4 (Model Discovery Agent). Full text confirms a "no M-open" expansion ablation (Section 4.1) and the statement that every numeric quantity "is computed by Bayesian inference, never by the LLM" (Section 3). Call caching NOT found in fetched text (unverified).
- https://arxiv.org/abs/2609.01526 (EvoSCM). Abstract confirms revising causal structures and mechanisms, discriminative interventions, committed falsifiable predictions; no component attribution mentioned.
- https://arxiv.org/abs/2607.15766 (HypoArena / Prospective Hypothesis Discovery). Abstract confirms reconstructed pre-conclusion contexts and structured judging; no simulator execution.

## Findings

### aij-claim-01. MUST-FIX. Section 5.6 line 301; S17 line 204; Figure 7 caption (line 309).

Quote (main text): "C_rand retains 57/400 and 13/100". Quote (S17): "This policy retained 347/400 known-family and 100/100 held-out C3 worlds, 57/400 and 13/100 C_rand worlds, and 8/96 DeepSeek worlds."

Error (not editorial). Blind rebinding did not retain C_rand successes; it changed the set. Evidence: `experiments/nmi_realizer_audit_v1/analysis/paired_transitions.csv`, row `C_rand,aligned_vs_role_action_blind_binding`: both_fail 420, aligned_only 10, counterfactual_only 15, both_pass 55, paired_jsr_difference +0.01. Known-family goes 52 -> 57; held-out 13 -> 13. Figure 7a plots 52 beside 57, so the figure contradicts the verb. The inference in the next sentence ("these outcomes localize sensitivity to binding information within the archived pipeline") also needs qualification because for C_rand the intervention helped as often as it hurt.

Proposed 5.6 wording:
"Role/action-blind rebinding preserves 347/400 known-family and 100/100 held-out C3 successes, and 8/96 grammar-constrained successes. For C_rand it changes which worlds succeed rather than removing successes: 10 aligned successes are lost and 15 other worlds succeed, giving 57/400 known-family and an unchanged 13/100 held-out. C3 losses are confined to hidden-regime and meta-law worlds. Because algebra and graphs remain fixed while variable binding changes, these outcomes show that binding information affects archived verdicts in both directions within this pipeline."

Proposed S17 wording: replace "This policy retained 347/400 known-family and 100/100 held-out C3 worlds, 57/400 and 13/100 C_rand worlds, and 8/96 DeepSeek worlds." with "This policy retained 347/400 known-family and 100/100 held-out C3 worlds and 8/96 DeepSeek worlds. For C_rand it lost 10 aligned known-family successes and gained 15 others (57/400), with 13/100 held-out unchanged."

Proposed Figure 7 caption addition: "The C_rand known-family count rises under blind binding because 15 worlds succeed only under blind binding while 10 aligned successes are lost."

### aij-claim-02. SHOULD-FIX. Section 5.5 line 291; S14 line 168; Figure 6c caption (line 297).

Quote: "Random composition succeeds in 16/96 worlds on the same panel. ... The aggregate provides no model advantage over that comparator."

Fairness-of-comparison omission. The two policies differ in final selection, not only proposal source. Grammar-constrained: evaluates all 16 plans per slot and keeps the highest-scoring one (`fair_interface_experiment.py:171-173`; score from `composition_search.py:53-74`). C_rand: keeps 3 of 48 paths by structural-hash order with no evaluation (`composition_search.py:480-483`). C_rand also had 29 primitives including crossover; grammar condition 28 (manuscript line 190, S13). The manuscript discloses the analogous traversal-plus-selection confound for C3 vs C_rand (line 162, S6) but not here. Direction: the tie was obtained despite an evaluated-selection advantage for the model path, so disclosure strengthens rather than weakens the "no advantage" reading, but the asymmetry must be stated.

Proposed addition after line 291:
"The two policies are not selection-matched. The grammar-constrained path keeps the highest-scoring executable plan among 16 evaluated plans per slot, whereas C_rand keeps three of 48 paths by structural hash without evaluation and has crossover available. The absence of an aggregate advantage therefore holds despite an evaluated-selection advantage for the model path; it is not an estimate of proposal quality alone."

Add the same sentence to S14 after "Thus the model-generated plans did not exceed random composition in aggregate and showed a different family-specific motif distribution."

### aij-claim-03. SHOULD-FIX. Section 5.5 line 291; S14 line 168.

Aggregate tie conceals strongly complementary family outcomes; only the model side is reported by family. Evidence (recomputed from `artifacts/compositional_jump_results.parquet`, C_RAND_RANDOM_PRIMITIVES, jump worlds, seeds 30014, 30012, 30029, 30025, 30011, 30023, 30000, 30032, 30001, 30037, 30002, 30015): property_to_relation 10/12, coordinate_transform 3/12, meta_law 2/12, unification 1/12, causal_ambiguity 0/12, hidden_regimes 0/12, latent_common_cause 0/12, state_invention 0/12; total 16/96 matches `paired_crand_comparison.csv`. Model condition: meta_law 9/12, unification 6/12, others 0/12 (`per_family.csv`). Section 6.3 sets a symmetric-care standard, so the family-level picture should be visible with the existing descriptive caveat, alongside the single-signature dependence (all 21 validated candidates `multi_argument_function`).

Proposed S14 addition:
"C_rand's 16 panel successes were 10/12 property-to-relation, 3/12 coordinate transformation, 2/12 meta-law and 1/12 unification. The model condition exceeded random composition in meta-law and unification, and random composition exceeded the model in property-to-relation; these family counts are descriptive and all model successes depended on the single `multi_argument_function` signature."

Proposed main-text clause at line 291, after "one joint success.":
"The family distributions differ: model successes are confined to meta-law and unification, whereas most random successes are property-to-relation worlds (Supplementary S14)."

### aij-claim-04. SHOULD-FIX. Abstract line 13; Section 5.5 line 289.

Quote (abstract): "A grammar-constrained interface exposed model-authored graph proposals, yielding successes in 15 of 96 worlds versus 16 for random composition on the same panel." Quote (5.5): "The two-stage grammar-constrained interface makes all 4,608 opportunities schema-valid and 3,939 dynamically executable."

Neither claim-bearing sentence says the condition ran a different model (DeepSeek-V4-Flash-Vision-Exp) with 4,096-token budgets, whereas the historical failure and the 0/96 legacy conditions concern Phi-4 at 700 tokens. Section 4.4 and S13 are clear, but a reader of the abstract or of 5.5's grammar paragraph can take it as a repair of the same system. This affects LLM-capability inference.

Proposed abstract: "A grammar-constrained interface, run with a second model checkpoint and larger budget, exposed model-authored graph proposals, yielding successes in 15 of 96 worlds versus 16 for random composition on the same panel."

Proposed 5.5: "The two-stage grammar-constrained interface, run with the DeepSeek checkpoint at 4,096-token budgets, makes all 4,608 opportunities schema-valid and 3,939 dynamically executable."

### aij-claim-05. SHOULD-FIX. Section 4.2 lines 150-154; Table 4 (lines 220-229); Section 5.2.

In every AJ5 condition the runner fits the expression deterministically and overwrites the model's expression and selected intervention before evaluation (`src/abductive_jump/primary_experiment.py:200-259`). Main text states this only for the factorial (line 154: "The fitter and maximum-separation action selector supply values shown to the second model call and enforce them in the evaluated artifact"); S4 states it for B1 only; Table 6 omits AJ5. "B0 direct model" therefore reads as a model-authored theory path. Correct statement is stronger for the thesis: B0/B1 differ from B4/B5 only in representation source. It also grounds 6.2 line 327 ("Only the supplied-representation control establishes evaluated model-authored expressions here"), which is consistent with the code.

Proposed sentence at end of first paragraph of 4.2 (after "A separate value-only control also remains within the incumbent language."):
"In all six conditions the executable expression is fitted by the scaffold and the committed intervention is the deterministic maximum-separation action; model-authored expression or action fields are overwritten before evaluation, so the conditions differ in representation source only."

Optional Table 4 caption clause: "Expression and committed intervention are scaffold-supplied in every row."

### aij-claim-06. OPTIONAL (editorial). Abstract line 13.

Quote: "A post-hoc inference-free replay reproduced all 2,400 candidate verdicts: deterministic components supplied the evaluated theories, ranking and interventions." The colon presents replay as establishing authorship. Replay establishes verdict invariance under deletion; authorship comes from provenance/code inspection (S20 line 240 labels the transformation statements as post-hoc code inspection).

Proposed: "A post-hoc inference-free replay reproduced all 2,400 candidate verdicts, consistent with provenance showing that deterministic components supplied the evaluated theories, ranking and interventions."

### aij-claim-07. OPTIONAL (clarity). Section 5.2 line 237.

Quote: "The representation-source factorial yields 0/400 for model-proposed representations". Sits beside B0 and B1 at 1/400 each. P0 is a separate run at temperature 0.7 through the factorial code path (line 184 mentions "factorial P0 at 0.7"; S4). Apparent inconsistency for readers.

Proposed: "The representation-source factorial, a separate run whose model condition uses temperature 0.7, yields 0/400 for model-proposed representations, 142/400 for the external portfolio and 400/400 for supplied-correct representations."

### aij-claim-08. OPTIONAL, UNRESOLVED. S18 line 214.

Quote: "Model Discovery Agent explicitly separates proposal from Bayesian inference, reports an expansion-component ablation and caches calls [24]." The ablation and separation claims are VERIFIED from the arXiv v4 full text (https://arxiv.org/html/2608.09696v4: "no M-open" ablation in Section 4.1; "every numeric quantity ... is computed by Bayesian inference, never by the LLM" in Section 3). Call caching was NOT found in the fetched text (unverified; could be in an appendix or PDF). Verify against the PDF or drop "and caches calls".

## Sections checked with no issues in this domain

Title and keywords; Introduction (apart from cross-reference in aij-claim-04); 2.1, 2.2, 2.3, 2.5; 2.4 characterizations of EvoSCM and HypoArena match their abstracts; formal framework 3.1-3.4 including Tables 1 and 2 and the outcome-blind J3 statement; 4.1; 4.3 including Table 3 and held-out-basis disclosure; 4.5; 5.1 including control-comparator interpretation and worked-example arithmetic; 5.3 including the complete-policy framing of the 0.87 contrast; 5.4; 5.7; 6.1, 6.2, 6.4; Limitations; Conclusion; Data/Code availability; author contributions; funding; competing interests; generative-AI declaration; cover letter; Supplement S1-S11, S12, S13, S15, S16, S19, S20. Figures 2 (AJ5), 3 (CJ5), 5 (interface), 4 (provenance schematic) consistent with captions and tables; Figure 6 (realizer) consistent with tables but see aij-claim-01 for caption/text wording.

## Coverage limits and unresolved checks

- The 1,125 (AJ5) and 1,625 (CJ5 = 1,125 + 500) comparator-case counts were taken from the recorded script output in `reports/AIJ_NUMERICAL_CHECKS.json` and `reports/AIJ_NUMERICAL_AUDIT.md`; `scripts/audit_nmi_control_comparator.py` was NOT rerun (unverified independently).
- The S20 evidence-record reproduction (`scripts/validate_aij_evidence_record.py --reproduce`) was not executed.
- Only references 24, 25 and 26 were checked against sources; other citations not checked in this domain.
- Pre-response determinism of C3 fields (5.4 line 262) relies on the S20 code-inspection statement plus my read of the action-selection line (`compositional_experiment.py:501`); no full runtime trace inspected.
- Figures 1 and 7 not inspected beyond caption arithmetic.
- The 3/40 DeepSeek P2 raw ledger was not inspected; counts taken from the analysis CSV.
- Tokensave MCP unavailable; no `.tokensave/tokensave.db` query performed.

## Three most consequential findings

1. aij-claim-01: "retains 57/400" is a factual misdescription contradicted by Figure 7a, and it weakens the binding-sensitivity inference.
2. aij-claim-02: the grammar-vs-random comparison hides a selection-policy asymmetry that the paper discloses for the analogous C3 comparison.
3. aij-claim-03 with aij-claim-04: the "no model advantage" headline omits the model identity/budget and the complementary family-level outcomes, which is the symmetric-care standard Section 6.3 sets for itself.

## Finding count

8 findings: 1 must-fix (01), 4 should-fix (02, 03, 04, 05), 3 optional (06, 07, 08; 08 unresolved).
