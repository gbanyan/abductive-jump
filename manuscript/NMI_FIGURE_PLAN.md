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

## Figure 2 — Representation proposals separate from reasoning

**Format:** 180 mm, three panels.

- **a:** AJ5 JSR for B0–B5, counts over 400 and stratified bootstrap 95% CIs.
- **b:** P0/P1/P2 proposal–reasoning factorial, identical reasoner and three-slot/two-call path.
- **c:** One-, two- and three-slot dose curves for B4 and B5; report calls/tokens separately.

**Primary values:** B0 1, B1 1, B2 0, B3 0, B4 142, B5 142 of 400; P0 0, P1 142, P2 400 of 400; B4 53/101/142 and B5 58/96/142 across slots.

## Figure 3 — Generic composition removes the atomic answer menu

**Format:** 180 mm, three panels.

- **a:** Atomic AJ5 operator versus 29 generic primitives and four-step ancestry.
- **b:** Known-family CJ5 JSR for C0, C1, C2, C3, C_self, C_rand and C5.
- **c:** Retained jump gain rho with bootstrap interval and C3 per-family small multiples.

**Primary values:** 0, 131, 0, 400, 0, 52 and 400 of 400; rho 3.053 [2.685, 3.540]. Visually separate C1/C5 reference ceilings because operation semantics differ.

## Figure 4 — Held-out transfer, specificity and audit trail

**Format:** 180 mm, four panels.

- **a:** Held-out triadic relation construction without a dedicated operator.
- **b:** Held-out JSR: C0 0, C1 0, C2 0, C3 100, C_self 0, C_rand 13, C5 100 of 100.
- **c:** Depth summary: all successful C3 candidates at registered depth four; 0/17,280 depth-one alternatives validate.
- **d:** Integrity strip: 0/300 C3 false jumps; 16,800/16,800 CJ5 replays and 10,800/10,800 AJ5 replays exact; no confirmatory exclusions or shard reruns.

## Table 1 — Controlled comparison design

Columns: condition, proposal source, allowed representation change, attempted primitive operations, final candidate slots, LLM calls per slot, prospective interventions and role. Mark C1 and C5 as reference conditions and explain their non-comparable operation semantics.

## Legend requirements

Each legend begins with a short title sentence, defines JSR/FJR and every interval, states exact world n, names the resampling/test procedure and tails, and identifies which panels are schematics. Keep each under 250 words.

