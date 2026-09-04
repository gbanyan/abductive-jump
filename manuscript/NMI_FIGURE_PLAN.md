# Main figure plan

## Visual system

Use a colour-blind-safe Okabe–Ito palette, Arial/Helvetica, 5–7 pt at final size, vector output, and direct labels where possible. Conditions should retain the same colours across figures. Show world-level counts and 95% intervals; do not imply candidate rows are independent replicates.

## Figure 1 — A prospective assay for bounded representation escape

**Format:** 180 mm, four panels.

- **a:** Observations compatible with the incumbent oracle and an escaped representation.
- **b:** Frozen incumbent grammar versus typed genome mutation; highlight canonical membership failure.
- **c:** Timeline: propose → fit observations → freeze intervention → observe outcome → separate held-out falsification → deterministic replay.
- **d:** J0–J5 gate diagram with thresholds and “all gates required.”

**Source:** preregistrations, DSL schema and evaluator code. No inferred result.

## Figure 2 — Typed proposals and their gate attrition

**Format:** 180 mm, four panels.

- **a:** AJ5 JSR using semantic condition names, counts over 400 and stratified bootstrap 95% CIs. Retain B0–B5 only in Methods and source data.
- **b:** Proposal-source comparison using semantic labels, with the same three-slot/two-call path.
- **c:** One-, two- and three-slot dose curves for B4 and B5; report calls/tokens separately.
- **d:** Cumulative candidate attrition J0→J5 for B4 and B5.

**Primary values:** B0 1, B1 1, B2 0, B3 0, B4 142, B5 142 of 400; P0 0, P1 142, P2 400 of 400; B4 53/101/142 and B5 58/96/142 across slots.

## Figure 3 — Generic search with fixed motif realization

**Format:** 180 mm, three panels.

- **a:** Atomic AJ5 operator versus 29 generic primitives and four-step ancestry.
- **b:** Known-family CJ5 JSR for C0, C1, C2, C3, C_self, C_rand and C5.
- **c:** Retained jump gain rho with bootstrap interval and C3 per-family small multiples. State that the shared motif-to-basis realizer is fixed and family-aligned.

**Primary values:** 0, 131, 0, 400, 0, 52 and 400 of 400; rho 3.053 [2.685, 3.540]. Visually separate C1/C5 reference ceilings because operation semantics differ.

## Figure 4 — Component attribution and executable proposal

**Format:** 180 mm, four panels.

- **a:** Archived deterministic-search verdicts versus model-free replay, with 2,400/2,400 candidate agreement and pooled 500 jump worlds.
- **b:** Aligned versus motif-disabled world success for deterministic search, random composition and grammar-constrained model proposals.
- **c:** Paired comparison of grammar-constrained model proposals and random composition on the same 96 worlds.
- **d:** Cumulative candidate attrition to J3 under motif-disabled replay, showing that most candidates remain structurally valid but lose prospective discrimination.

The caption states that model-free and realizer counterfactuals are post-confirmatory attribution analyses, candidate rows are not independent replicates, and the n=96 model/random comparison is a fixed sensitivity panel. Detailed precision, token-cap, repair, signature-mask and per-family diagnostics move to Extended Data and Supplementary Information.

## Figure 5 — One complete prospective escape

**Format:** 180 mm, single worked-example flow.

Show correlated observations, cubic incumbent, four local rewrites, triadic candidate, frozen intervention predictions, revealed outcome and a separate held-out falsification case.

## Supplementary Table 1 — Position relative to adjacent discovery evaluations

Columns: executable hypothesis, hypothesis-space boundary, structural non-membership certificate, prospective test, held-out check, component attribution, deterministic replay and model/domain breadth. This table is not a main display item.

## Legend requirements

Each legend begins with a short title sentence, defines JSR/FJR and every interval, states exact world n, names the resampling/test procedure and tails, and identifies which panels are schematics. Targeted sensitivity panels emphasize counts, Wilson intervals, paired world-level differences and family-descriptive results without candidate-level significance tests. Keep each under 250 words.
