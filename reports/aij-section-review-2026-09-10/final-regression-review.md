# AIJ final regression review (aij-claim domain)

- Reviewer: aij-claim
- Date: 2026-09-10
- Baseline: HEAD `0214bc592aa55c92e5aaeffd298fbe22b07f3e3c`
- Scope: working-tree changes to `manuscript/AIJ_MANUSCRIPT.md` (+76/-60), `manuscript/AIJ_SUPPLEMENTARY_METHODS.md` (+26/-22), `manuscript/AIJ_CODE_AVAILABILITY.md`, `manuscript/AIJ_COVER_LETTER.md`, `manuscript/AIJ_DECLARATION_OF_GENERATIVE_AI.md`. Figure files under `manuscript/figures/aij/` are unmodified versus HEAD.
- Read-only. No manuscript, code, data or git changes. No experiments or model calls.

## Result

**No must-fix or should-fix regression found.** Every factual claim introduced or reworded by the edits that falls in this domain was checked against code or frozen artifacts and matches. No cross-section contradiction was introduced. Qualifiers removed from one location are retained elsewhere in the current text (listed below). Three optional notes follow; none is an error.

## Verified edited claims (evidence)

| Edited claim (location) | Evidence | Status |
|---|---|---|
| 5.6 / S17 / Fig 7 caption: C_rand blind binding loses 10 aligned known-family successes, 15 other worlds succeed, 57/400; same 13/100 held-out under both policies | `experiments/nmi_realizer_audit_v1/analysis/paired_transitions.csv` row `C_rand,aligned_vs_role_action_blind_binding`: aligned_only 10, counterfactual_only 15, both_pass 55 (42 known + 13 held-out) | Verified |
| S17: lost worlds are 3 meta-law and 7 unification; 15 latent-common-cause newly succeed | `per_family.csv` C_rand aligned vs role_action_blind_binding: meta_law 5→2, unification 7→0, latent_common_cause 0→15; per-family net changes sum exactly to 10/15, so no hidden within-family swaps | Verified |
| S17: C3 and DeepSeek have no newly successful world under blind binding | paired_transitions.csv counterfactual_only = 0 for both | Verified |
| 5.5 / S14: grammar-constrained path keeps highest-scoring executable plan of up to 16 per slot; C_rand evaluates its 48 paths but retains three by structural hash without using scores | `src/abductive_jump/fair_interface_experiment.py:171-173`; `composition_search.py:438-483` (evaluate_candidate called per step and per final path; selection sorted by structural_hash only) | Verified |
| 5.5 / S14: no crossover mention for C_rand; user correction that random_search never offers crossover | `grep CROSSOVER composition_search.py` returns nothing; `_start_actions`/`_continuation_actions` do not include it | Consistent |
| S14: C_rand panel successes property_to_relation 10/12, coordinate_transform 3/12, meta_law 2/12, unification 1/12, others 0 | recomputed from `artifacts/compositional_jump_results.parquet` restricted to the 12 panel seeds; total 16/96 matches `paired_crand_comparison.csv` | Verified |
| S14: the single joint success is a meta-law world | `experiments/nmi_fair_interface_v1/results/deepseek_fair_cself/world_results.parquet` joined with C_rand world results: joint success = (meta_law, seed 30025) | Verified |
| 4.2 / Table 4 / S4: in all six AJ5 conditions the scaffold fits the expression and selects the max-separation intervention, overwriting model fields | `src/abductive_jump/primary_experiment.py:200-259` applies to every condition; B2/B3 enter the same path via `_phase_one_representation` (lines 66-79). New text does not claim a source-only comparison across all six | Verified |
| 4.2 / S4: B5 selects three structurally distinct proposals without replacement; B4 with replacement | `src/abductive_jump/proposals.py:111-125` (`diverse=True`: shuffle and take first `slots`; else `rng.choice` with replacement) | Verified |
| S4: B3 reported under historical label A4_VALUE_ONLY, not a separate run | `src/abductive_jump/analysis.py:505-506` (A4_VALUE_ONLY jsr taken from B3) | Verified |
| S9: 32,400 = 21,600 (B0–B5) + 10,800 (factorial); 3,600 A6 calls; A6 is a triggered random-untyped graph-edit ablation archived in `artifacts/confirmatory/ablation-a6-jump` and `ablation-a6-control` | arithmetic 6×600×3×2 and 3×600×3×2; `llm_calls.jsonl` line counts 2,400 + 1,200 = 3,600; `docs/abductive-jump-preregistration.md:89` lists A6 conditional on AJ5 criteria; `proposals.py:random_untyped_proposal` docstring "A6 control: random graph edits without kind-specific structural semantics"; `analysis.py:517` label A6_RANDOM_UNTYPED | Verified |
| S16: sign-flip test returns P=1 when all differences are zero, enumerates when 1–20 non-zero, else 10,000 random flips with (extreme+1)/(replicates+1); all reported contrasts use the random branch | `src/abductive_jump/compositional_analysis.py:86-113`; every reported CJ5 contrast has ≥87 non-zero paired differences (smallest: held-out C3−C1 = 100−13... see note) | Verified (branch logic); random-branch claim consistent since all contrasts have >20 non-zero differences (known: 269–400; held-out: 87–100) |
| S10: comparator counts recorded under "Control worlds/cases" in `reports/AIJ_NUMERICAL_CHECKS.json` | JSON line 1212 `"claim": "Control worlds/cases"`, source line 1247 | Verified (script not rerun) |
| 4.4 / 5.2: factorial P0 uses temperature 0.7; 4.4 lists conditions using the DeepSeek checkpoint | consistent with S4, S11, S13 | Consistent |
| Table 1: J1 row `R∉A₀`, caption "V(T) is required for every gate J1–J5" | S19: `evaluate_executable` conjoins V(T) with J1–J5 | Consistent |
| Abstract: second checkpoint DeepSeek and larger budgets named; 15/96 vs 16/96 | matches 4.4, 5.5, S13–S14 | Consistent |
| 2.3 ref 44 LLM-SR: model proposes equation skeletons, parameters optimized against data | ICLR 2025 abstract (https://proceedings.iclr.cc/paper_files/paper/2025/hash/28df8e730c054c5331855fd4d5403ba9-Abstract-Conference.html) | Verified |
| 2.4 ref 45 Shi et al.: constrained completion excluding a canonical Kan-extension default | arXiv 2608.26187v2 abstract | Verified |
| Ref 22 changed to ICML 2026 position paper | https://icml.cc/virtual/2026/poster/67091 lists "Position: LLMs can't jump", Tom Zahavy, position-paper track | Verified |
| Ref 43 Langley et al. 1987 DOI | https://doi.org/10.7551/mitpress/6090.001.0001 redirects to MIT Press "Scientific Discovery: Computational Explorations of..." (redirect target not fetched) | Consistent (title/DOI); page content unverified |
| S18 "caches calls [24]" retained | user reports confirmation in MDA appendix H; not re-fetched here | Accepted per user; unverified by me |

Correction to the S16 row above: the smallest non-zero count among reported contrasts is held-out C3−C_rand (87 non-zero differences); all others are ≥100 or ≥269. All exceed 20, so the random-flip branch applies to every reported contrast, as S16 states.

## Dropped qualifiers checked (retained elsewhere)

- 2.2 removed "functional inexpressibility" caveat → retained in 3.2 and Limitations ("J1 is not a semantic expressivity theorem").
- 3.3 removed "zero control rate checks construction-specific consistency" → retained verbatim in 5.1.
- 5.3 removed hold-out scope paragraph → retained in 4.3 ("not discovery of an unseen algebraic form"), Figure 4 caption, Abstract and Limitations.
- 4.5 removed "many seeds ... do not establish breadth" → retained in Limitations.
- 5.7 removed "not independent experimental replication" → retained in Limitations.
- Limitations removed "Public Git freezes also lack an independent registry timestamp" → retained in 4.1 and S11.
- 5.5 removed "not the absence of an internally useful conceptual proposal" → retained in 6.3.
- S12 removed "not a reliable ceiling" → retained in Limitations ("sparse and interface-limited").
- 6.4 / S20 removed "does not certify scientific novelty" → retained in Table 2 caption.

## Optional notes (not errors)

1. Figure 4 caption "supplied meta-language (Table 3)": the new 4.3 sentence defines the meta-language as 29 primitives plus nine signatures, whereas Table 3 lists only the signatures. Optional: "(Section 4.3, Table 3)".
2. 4.4 "the historical self-composition prompt and parser of Section 4.3": the prompt and parser are described in S13/S16, not 4.3. Optional cross-reference change.
3. 5.3 now states the held-out saturation without a local qualifier; the qualifier sits in 4.3 and the Figure 4 caption directly below. Acceptable as is.

## Coverage limits

- The comparator audit script and the S20 `--reproduce` validation were not rerun.
- MDA appendix H (call caching) not re-fetched; accepted per user statement.
- Ref 43 page content behind the DOI redirect not fetched.
- Figures not re-inspected because they are unmodified versus HEAD.
- tokensave MCP unavailable; checks used targeted file reads and pyarrow.
