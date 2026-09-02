# NMI Publication Numerical Audit

Audit date: 2 September 2026. This audit recomputes percentages from integer counts and treats the canonical Parquet/JSON artifacts as authoritative. No model inference was run.

## AJ5

### Primary conditions

| Condition | Successful worlds | Worlds | JSR | 95% family-stratified bootstrap CI | False jumps | Controls | Wilson 95% FJR CI |
| --- | ---: | ---: | ---: | --- | ---: | ---: | --- |
| B0 direct LLM | 1 | 400 | 0.25% | [0%, 0.75%] | 0 | 200 | [0%, 1.8845%] |
| B1 sample-matched LLM | 1 | 400 | 0.25% | [0%, 0.75%] | 0 | 200 | [0%, 1.8845%] |
| B2 fixed-space agent | 0 | 400 | 0% | [0%, 0%] | 0 | 200 | [0%, 1.8845%] |
| B3 attribute/value mutation | 0 | 400 | 0% | [0%, 0%] | 0 | 200 | [0%, 1.8845%] |
| B4 representation mutation | 142 | 400 | 35.5% | [31.0%, 40.25%] | 0 | 200 | [0%, 1.8845%] |
| B5 representation mutation + QD | 142 | 400 | 35.5% | [31.0%, 40.0%] | 0 | 200 | [0%, 1.8845%] |

B4 per-family successes were 18, 29, 17, 12, 20, 13, 18 and 15 out of 50 for latent common cause, unification, hidden regimes, property-to-relation, state invention, coordinate transform, causal ambiguity and meta-law. B5 counts were 16, 31, 13, 23, 13, 17, 16 and 13. Both therefore had non-zero success in 8/8 families. B5 did not exceed B4 in aggregate.

### Preregistered comparisons

All comparisons use 10,000 deterministic family-stratified paired bootstrap replicates; candidates within worlds are not independent replicates.

| Comparison | Difference | 95% CI | Unadjusted one-sided P | Holm P |
| --- | ---: | --- | ---: | ---: |
| B4−B0 | 35.25 pp | [30.5, 39.75] pp | 0.00009999 | 0.00079992 |
| B4−B1 | 35.25 pp | [30.75, 40.0] pp | 0.00009999 | 0.00079992 |
| B4−B2 | 35.5 pp | [31.0, 40.0] pp | 0.00009999 | 0.00079992 |
| B4−B3 | 35.5 pp | [31.0, 40.0] pp | 0.00009999 | 0.00079992 |
| B5−B0 | 35.25 pp | [30.75, 39.75] pp | 0.00009999 | 0.00079992 |
| B5−B1 | 35.25 pp | [30.75, 40.0] pp | 0.00009999 | 0.00079992 |
| B5−B2 | 35.5 pp | [31.0, 40.0] pp | 0.00009999 | 0.00079992 |
| B5−B3 | 35.5 pp | [31.0, 40.25] pp | 0.00009999 | 0.00079992 |

### Proposal–reasoning factorial and dose response

P0 LLM proposal produced 0/400 jumps; P1 external proposal produced 142/400 (35.5%); P2 oracle representation produced 400/400 (100%). Each had 0/200 control false jumps. P1−P0 and P2−P0 each had unadjusted P=0.00009999 and Holm P=0.00019998.

At one, two and three mutation slots, B4 succeeded in 53/400 (13.25%), 101/400 (25.25%) and 142/400 (35.5%). B5 succeeded in 58/400 (14.5%), 96/400 (24.0%) and 142/400 (35.5%). This is a nested descriptive frontier, not an independently randomized dose experiment.

### Population, traces, replay and exclusions

- Eight families × 50 jump seeds (10000–10049) = 400 positive worlds; eight × 25 seeds (20000–20024) = 200 no-jump worlds.
- Primary jump/control traces contain 14,400 and 7,200 calls; factorial jump/control contain 7,200 and 3,600. Total preregistered inference: 32,400 calls.
- Triggered A6 jump/control contain 2,400 and 1,200 calls: 3,600 secondary calls.
- Replay matched 10,800/10,800 selected AJ5 candidates; mismatches=0.
- Confirmatory worlds excluded=0; output-quality exclusions=0; infrastructure shard reruns=0. Development attempts and pilots are retained outside confirmatory results.
- The historical completion audit reported 112 tests. The current expanded repository has more tests; 112 must be described as the phase-completion count, not the current suite size.

## CJ5

### Conditions

| Condition | Known successes/worlds | Known JSR (Wilson 95% CI) | Held-out successes/worlds | Held-out JSR (Wilson 95% CI) | False jumps/controls |
| --- | --- | --- | --- | --- | --- |
| C0 fixed space | 0/400 | 0% [0%, 0.9512%] | 0/100 | 0% [0%, 3.6993%] | 0/300 |
| C1 atomic high-level | 131/400 | 32.75% [28.334%, 37.494%] | 0/100 | 0% [0%, 3.6993%] | 0/300 |
| C2 single generic rewrite | 0/400 | 0% [0%, 0.9512%] | 0/100 | 0% [0%, 3.6993%] | 0/300 |
| C3 structured generic composition | 400/400 | 100% [99.049%, 100%] | 100/100 | 100% [96.301%, 100%] | 0/300 |
| C_self LLM composition | 0/400 | 0% [0%, 0.9512%] | 0/100 | 0% [0%, 3.6993%] | 0/300 |
| C_rand random primitives | 52/400 | 13% [10.053%, 16.651%] | 13/100 | 13% [7.757%, 20.980%] | 0/300 |
| C5 oracle representation | 400/400 | 100% [99.049%, 100%] | 100/100 | 100% [96.301%, 100%] | 0/300 |

C3 exceeded C_rand by exactly 0.87 in known families (95% paired-bootstrap CI [0.845, 0.895]) and held out (CI [0.80, 0.93]). Each unadjusted one-sided paired sign-flip P was 0.00009999; each Holm-adjusted P was 0.00029997 within its registered comparison family. Primary C3−C0 and C3−C2 differences were 1.0 with CI [1.0, 1.0] and Holm P=0.00019998. Held-out C3−C0 had P=0.00009999.

Retained jump gain was rho_J=(1−0)/(0.3275−0)=3.053435, with 10,000-replicate 95% bootstrap CI [2.684564, 3.539823]. The ratio exceeds one because C3 outperformed the atomic reference; it should always be paired with the absolute rates.

All validated C3 candidates had ancestry depth four. This is the minimum successful depth under the registered search output, not a proof of global graph-edit distance. Separate reachability work established 90/90 constructive witnesses at bounded depths 2–4 and 0/17,280 valid depth-one jumps.

### Population, traces, replay and seal

- Known reconstruction: 8 families × 50 seeds (30000–30049) = 400 worlds; known controls: 8 × 25 seeds (50000–50024) = 200.
- Held-out `triadic_relation_reification`: 100 seeds (40000–40099); held-out controls: 100 seeds (60000–60099).
- Four shards contain 16,800, 8,400, 4,200 and 4,200 exact unique calls: 33,600 total.
- Replay matched 16,800/16,800 candidates with 0 mismatches and reconstructed 35,533 ancestry rows.
- Worlds excluded=0; output-quality exclusions=0; infrastructure shard reruns=0.
- The held-out family was unlocked in commit `27ee542` only after the two known-family shards were terminal and audited. Execution source preceded the first confirmatory call and matches the recorded hashes.
- Reviewer #2 data verdict remained CJ5 after 20 attacks.

## Audit disposition

Every requested headline count and statistic is verified. No publication-critical number requires an expensive rerun. The main limitation is conceptual rather than numerical: the structured grammar and supplied primitive meta-language encode useful priors, and the held-out relation family is structurally adjacent to an earlier binary relation family.
