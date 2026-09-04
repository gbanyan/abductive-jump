# Main figure plan

## Visual system

Use a colour-blind-safe Okabe–Ito palette, Arial/Helvetica, 5–7 pt at final size, vector output, and direct labels where possible. Conditions should retain the same colours across figures. Show world-level counts and 95% intervals; do not imply candidate rows are independent replicates.

## Figure 1 — A prospective assay for bounded representation escape

**Format:** 180 mm, four panels.

- **a:** Observations compatible with the incumbent oracle and an escaped representation.
- **b:** Frozen incumbent grammar versus typed genome mutation; highlight canonical membership failure.
- **c:** Timeline: propose → fit observations → freeze intervention → observe outcome → independent falsification → deterministic replay.
- **d:** J0–J5 gate diagram with thresholds and “all gates required.”

**Source:** preregistrations, DSL schema and evaluator code. No inferred result.

## Figure 2 — Typed proposals and their gate attrition

**Format:** 180 mm, four panels.

- **a:** AJ5 JSR for B0–B5, counts over 400 and stratified bootstrap 95% CIs.
- **b:** P0/P1/P2 proposal–reasoning factorial, identical reasoner and three-slot/two-call path.
- **c:** One-, two- and three-slot dose curves for B4 and B5; report calls/tokens separately.
- **d:** Cumulative candidate attrition J0→J5 for B4 and B5.

**Primary values:** B0 1, B1 1, B2 0, B3 0, B4 142, B5 142 of 400; P0 0, P1 142, P2 400 of 400; B4 53/101/142 and B5 58/96/142 across slots.

## Figure 3 — Generic search with fixed motif realization

**Format:** 180 mm, three panels.

- **a:** Atomic AJ5 operator versus 29 generic primitives and four-step ancestry.
- **b:** Known-family CJ5 JSR for C0, C1, C2, C3, C_self, C_rand and C5.
- **c:** Retained jump gain rho with bootstrap interval and C3 per-family small multiples. State that the shared motif-to-basis realizer is fixed and family-aligned.

**Primary values:** 0, 131, 0, 400, 0, 52 and 400 of 400; rho 3.053 [2.685, 3.540]. Visually separate C1/C5 reference ceilings because operation semantics differ.

## Figure 4 — Attribution, transfer and targeted model sensitivity

**Format:** 180 mm, four panels.

- **a:** Archived C3 verdicts versus model-free replay, with 2,400/2,400 candidate agreement and pooled 500 jump worlds.
- **b:** Held-out JSR: C0 0, C1 0, C2 0, C3 100, C_self 0, C_rand 13, C5 100 of 100.
- **c:** Targeted world-level JSR on the fixed 96-world panel: historical Phi-4 4-bit C_self at 700 tokens, the separately frozen Phi-4 4-bit 2,048-token budget sensitivity, Phi-4 8-bit C_self, DeepSeek matched C_self, DeepSeek native C_self and grammar-constrained DeepSeek C_self. Include archived C_rand 16/96 and C3 96/96 panel controls, plus the balanced 40-world DeepSeek supplied-representation positive control. Visually separate the n=40 control and identify all sensitivities as non-confirmatory.
- **d:** Response-to-verdict attrition for historical Phi-4 and the new C_self conditions: response, parse, schema, operation, arguments/types, executable, J1–J5. Mark the one-repair Phi-4 condition as a triggered sensitivity, not a replacement result. Explicitly show that fixed-panel Phi-budget reaches 993/4,608 schema-valid but 0 executable opportunities, whereas the registered matched and native interfaces fail before execution. Add the grammar-constrained cascade to distinguish grammar-guaranteed serialization from dynamic executability and downstream gates.

The new panels were unlocked only after all five original extension shards and the fair-interface extension reached `complete_verified` and deterministic replay reported zero mismatches. The caption distinguishes the original n=400 confirmatory population, its fixed 96-world historical slice, the separately frozen Phi-4 budget populations (known-family n=400 and held-out n=100), the fixed n=96 sensitivity comparisons and the n=40 positive-control subset.

## Figure 5 — Counterfactual dependence on motif semantics

**Format:** 180 mm, four panels.

- **a:** World-level JSR under aligned, motif-disabled and role/action-blind realization for C3 known-family, C3 held-out, C_rand known-family, C_rand held-out and grammar-constrained DeepSeek.
- **b:** Paired aligned-to-counterfactual world transitions, emphasizing that motif disabling removes every archived success while role/action-blind binding preserves a subset.
- **c:** Cumulative candidate attrition for motif-disabled replay. Show that 1,168/1,500 C3, 1,040/1,500 C_rand and 236/288 DeepSeek slots retain J1–J2 but none reaches J3.
- **d:** Leave-one-signature-out world losses. Identify `relation_arity_3` as necessary for all 100 held-out C3 worlds and `multi_argument_function` as necessary for all 15 grammar-constrained DeepSeek worlds.

The caption states that the audit fixes candidates originally selected under the aligned realizer, makes zero model calls and is post-confirmatory. Candidate rows are attrition units rather than independent replicates.

## Figure 6 — One complete prospective escape

**Format:** 180 mm, single worked-example flow.

Show correlated observations, cubic incumbent, four local rewrites, triadic candidate, frozen intervention predictions, revealed outcome and independent falsification.

## Table 1 — Position relative to adjacent discovery evaluations

Columns: executable hypothesis, frozen formal language, structural non-membership certificate, prospective intervention, independent falsification, proposal/reasoning separation, deterministic replay and model/domain breadth.

## Legend requirements

Each legend begins with a short title sentence, defines JSR/FJR and every interval, states exact world n, names the resampling/test procedure and tails, and identifies which panels are schematics. Targeted sensitivity panels emphasize counts, Wilson intervals, paired world-level differences and family-descriptive results without candidate-level significance tests. Keep each under 250 words.
