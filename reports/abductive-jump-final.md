# Abductive Jump — Final Confirmatory Report

## Outcome

The preregistered verdict is **AJ5 — representation-mutation advantage**.

Under the tested procedural worlds, a frozen Phi-4 model reached prospectively validated explanations much more often when a structured external representation mutation was supplied than under matched direct generation, independent LLM sampling, fixed-space agentic revision, or value-only mutation. This is a result about validated escape from `H(R0)` in this benchmark—not general creativity, universal scientific discovery, or an architectural limit of LLMs.

Preregistration commit: `895ebb9118ffd0046825b88868621f2a70f69f61`. Primary inference used one RTX 4090 on `gblinux`, frozen `microsoft/phi-4` revision `2db69c1c3e91a05d2c64a3185acfbaf36f744e25`, vLLM 0.10.2, bitsandbytes 4-bit, and the frozen v10 prompt. All 32,400 preregistered calls completed; triggered A6 added 3,600 secondary calls.

## Primary results

| Condition | JSR (400 jump worlds) | Stratified 95% CI | FJR (200 controls) | FJR Wilson upper | Validated candidates | Abductive precision |
|---|---:|---:|---:|---:|---:|---:|
| B0 Direct LLM | 0.25% | 0–0.75% | 0% | 1.885% | 1 | 25.0% |
| B1 Sample-matched LLM | 0.25% | 0–0.75% | 0% | 1.885% | 1 | 0.85% |
| B2 Fixed-space agent | 0% | 0–0% | 0% | 1.885% | 0 | undefined |
| B3 Attribute/value mutation | 0% | 0–0% | 0% | 1.885% | 0 | undefined |
| B4 Representation mutation | 35.5% | 31.0–40.25% | 0% | 1.885% | 154 | 57.0% |
| B5 Full system | 35.5% | 31.0–40.0% | 0% | 1.885% | 145 | 55.3% |

B4 and B5 each succeeded in 142/400 worlds and in every family. Their successful-world sets were different: 26 overlapped and 258 were in the union, as expected from distinct seeded candidate draws. Per-family B4 successes ranged from 12/50 to 29/50; B5 ranged from 13/50 to 31/50. No negative family is hidden.

All eight preregistered B4/B5 comparisons against B0–B3 were positive after Holm correction. Paired family-stratified differences were 0.3525–0.355; 95% intervals were approximately 0.305–0.4025; every one-sided bootstrap p-value was `0.00009999` and every Holm-adjusted value was `0.00079992`.

Every world-condition cell used exactly six LLM calls, three candidate evaluations, and three interventions, with identical 4,200-token ex ante capacity. Actual mean completion tokens per world ranged from 818 to 1,427 because EOS was not padded. B4/B5 used fewer actual tokens than B0 and still performed better. B4 and B5 required about 2,335 and 2,364 completion tokens per successful world; B0/B1 required over 400,000 because each produced only one success.

## Proposal–reasoning decomposition

| Proposal source | JSR | Interpretation |
|---|---:|---|
| P0 LLM | 0/400 (0%) | The model rarely proposed a surviving representation. |
| P1 External structured mutation | 142/400 (35.5%) | Same reasoner, externally supplied candidate distribution. |
| P2 Oracle-correct representation | 400/400 (100%) | Reasoning ceiling once the right typed representation is supplied. |

P1−P0 was 0.355 (95% CI 0.31–0.40), and P2−P0 was 1.0 (CI 1.0–1.0); both Holm-adjusted p-values were `0.00019998`. P0/P1/P2 controls were all 0/200. This supports a proposal bottleneck under the frozen interface. It does not show that a stronger or differently trained model would retain the same gap.

## Triggered ablations

| Ablation | JSR | Reference B5 | Finding |
|---|---:|---:|---|
| A1 No diversity archive (B4) | 35.5% | 35.5% | No archive benefit. |
| A2 Before falsification gate | 35.5% | 35.5% | J5 removed no additional successful worlds. |
| A3 No crossover | 35.5% | 35.5% | Structurally null: the primary portfolio never used crossover. |
| A4 Value-only (B3) | 0% | 35.5% | Remaining in `H(R0)` cannot pass J1. |
| A5 LLM chooses mutation (B1) | 0.25% | 35.5% | Same generic vocabulary did not match external proposal coverage. |
| A6 Random untyped mutation | 4.5% | 35.5% | Random edits sometimes aligned by chance but were far weaker; FJR remained 0/200. |

The data therefore support structured representation proposal, not the extra B5 archive/falsifier machinery. The strongest mechanistic statement is that the supplied proposal distribution changes reachability. The study does not establish quality-diversity or evolutionary dynamics as necessary components.

## Replay and integrity

The four frozen primary/factorial shards contained exactly 32,400 calls. Post-run replay rebuilt all 10,800 primary candidates from raw model outputs plus frozen seeds, regenerated representations, fitted expressions, exact intervention choices, predictions, and commitments, and matched every saved J0–J5 field with zero discrepancies. The replay produced canonical `candidate_theories.parquet`, `intervention_predictions.parquet`, and `mutation_trace.parquet` artifacts.

Two analysis-layer errors were found and corrected transparently: replay initially evaluated public-name expressions on internal-name cases, and the first bootstrap implementation accidentally included control seeds in JSR resampling. Neither affected frozen model outputs or deterministic gates. Regression tests now cover both failure modes.

## Interpretation and limits

The result clears AJ5 exactly as preregistered: B4/B5 beat B0–B3 under the matched envelope, FJR is controlled, success spans all families, and P1/P2 exceed P0 with a 100% P2 ceiling.

The main limitation is operator–benchmark alignment. The nine-member external portfolio was calibrated to include generic latent, invariant, regime, relational, state, square-transform, affine-context, causal, and transition variants; these closely cover the eight generator motifs. The proposer is family-blind and samples before outcomes, but the portfolio and benchmark were co-designed and every structural family appeared in development. A6 shows that arbitrary graph edits are insufficient, yet it does not prove the portfolio would discover an unseen structural family. AJ6 is therefore unavailable, and the external process is best described as a structured proposal library rather than a general autonomous theory-invention algorithm.

B0 also had 494/1,200 invalid first-stage candidates and B1 had 176/1,200; all fell back to the incumbent as preregistered. This is partly a proposal-capability finding and partly an interface burden. P2=100% shows the downstream reasoner was adequate, but a grammar-constrained decoder or stronger model may reduce the gap.

## Figures and artifacts

- [Figure 1 — search spaces](figures/figure1-search-spaces.svg)
- [Figure 2 — JSR by condition](figures/figure2-jsr-by-condition.svg)
- [Figure 3 — JSR versus FJR](figures/figure3-jsr-vs-fjr.svg)
- [Figure 4 — proposal versus reasoning](figures/figure4-proposal-reasoning.svg)
- [Figure 5 — counterfactual gain](figures/figure5-counterfactual-gain.svg)
- [Figure 6 — cost to jump](figures/figure6-cost-to-jump.svg)
- [Figure 7 — per-family B5](figures/figure7-per-family.svg)

Machine-readable conclusions are in `artifacts/final_verdict.json` and `artifacts/final_claim_matrix.csv`; statistical tables are in `condition_summary.parquet`, `confirmatory_comparisons.parquet`, `proposal_reasoning_factorial.parquet`, and `ablation_summary.parquet`.
