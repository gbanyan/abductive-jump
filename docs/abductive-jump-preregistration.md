# Abductive Jump Confirmatory Preregistration

Status: frozen before any confirmatory model call. The Git commit containing this document is the preregistration identifier. All pilot seeds are excluded from confirmatory ranges.

## Question and estimand

The primary question is whether structured external mutation of representational primitives enables a frozen LLM to reach prospectively validated explanations outside a locally adequate incumbent hypothesis language more often than matched direct, sampled, fixed-space, and value-mutation search. The unit of replication is a procedurally generated world. A world succeeds for a condition when at least one of its three prospectively committed candidates passes every deterministic gate J0–J5.

The claim is limited to validated representation escape in these procedural worlds. Semantic novelty, lexical novelty, model confidence, and human interest never enter a gate or primary statistic.

## Frozen engine and population

- Eight primary families: latent common cause, unification, hidden regimes, property-to-relation, state invention, coordinate transform, causal ambiguity, and meta-law.
- Jump population: seeds 10000–10049 in every family, 400 worlds total.
- Matched no-jump controls: seeds 20000–20024 in every family, 200 worlds total.
- Every family must retain an exhaustive incumbent-space oracle and pass J0. Failure of oracle verification or public-data redaction makes the benchmark invalid (AJ0); it is not an exclusion used to improve results.
- Calibration/model-selection seeds (41, 51, 61, 71, 1101–1103 and earlier engine seeds) are not confirmatory seeds.
- All eight families were used during development, so AJ6 held-out-structural-family generalization is unavailable in this study and cannot be claimed.

## Frozen model and runtime

- Host: `gblinux`; one NVIDIA RTX 4090 (24,564 MiB). No other GPU, multi-GPU execution, fine-tuning, LoRA, RL, or cross-world adaptation.
- Model: `microsoft/phi-4`, revision `2db69c1c3e91a05d2c64a3185acfbaf36f744e25`, frozen weights.
- Quantization: vLLM dynamic bitsandbytes 4-bit.
- Engine: vLLM OpenAI server 0.10.2; image `vllm/vllm-openai:v0.10.2`, digest `sha256:607442e407b0fea97f8a132a78b787c121a996dd4de181fa08e8da06e71ec2db`.
- Context limit 4096. Base temperature 0.2, top-p 0.95, per-call completion cap 700. B1/P0 proposal calls use temperature 0.7 as the preregistered independent-sampling manipulation. Prompt template `theory-json-v10`.
- Concurrency 16 affects scheduling only. Every request has a deterministic decoding seed. Rows are sorted canonically after completion.

## Frozen representations and proposals

The typed graph DSL, incumbent `LanguageSpec`, 22 generic mutation operators, canonical hashing, public-world redaction, shared deterministic hypothesis-genome fitter, and exact intervention designer are those in the preregistration commit. The external proposer receives only `PublicWorld`, never family, truth, validation outcomes, intervention outcomes, or falsification cases.

The nine-member external portfolio consists of generic latent, invariant, sign-contrast regime, additive relation, additive state, square function, affine-context function, causal-edge, and transition variants. B4 samples three with replacement using a seed fixed before outcomes. B5 selects three structurally distinct variants without replacement and records structural archive occupancy. B0 directly emits a typed theory graph. B1 emits at most three operations from the same generic operator vocabulary at high temperature. B2 retains the incumbent representation through repeated calls. B3 changes only within-language equation value attributes. Malformed B0/B1 output falls back to the incumbent for that slot and receives no replacement candidate.

All conditions use the same public observations, shared fitter, incumbent oracle predictions, and exact maximum-separation experiment designer. The designer sees candidate and oracle predictions for the finite public action set but no simulator outcomes. The selected intervention, candidate expression, prediction, representation hash, and split hash are frozen before evaluation. Model-selected interventions are logged only as diagnostics.

## Equal-budget contract

Every world-condition cell has exactly three candidate slots. Every slot receives exactly two LLM calls, one candidate evaluation, and one intervention commitment. Thus every cell has six calls, three evaluations, three interventions, and 4,200 completion-token capacity. Unused completion capacity cannot create calls, candidates, retries, or interventions. Actual completion tokens and latency are reported as cost outcomes; equality refers to the ex ante capacity and opportunity set, not forced padding after EOS. Wall time is secondary.

## Conditions and factorial

- B0: direct low-temperature LLM theory proposal and LLM reasoning.
- B1: three high-temperature LLM-chosen typed mutation plans and the same LLM reasoner.
- B2: repeated LLM revision and experiment reasoning with `R = R0` frozen.
- B3: external value/attribute variants within `H(R0)` plus the same LLM reasoner.
- B4: external representation mutation sampled with replacement plus the same LLM reasoner.
- B5: structurally distinct external representation mutation, diversity archive accounting, and deterministic falsification gate plus the same LLM reasoner.

The proposal–reasoning factorial runs P0 LLM, P1 external, and P2 oracle-correct representation sources on the same 400 jump and 200 control worlds with the identical three-slot/two-call reasoning path. P2 supplies the correct representation only; its equation and outcomes remain hidden.

## Gates and thresholds

- J0: incumbent oracle observation MSE ≤ `1e-12`.
- J1: candidate is DSL-valid and has at least one frozen-language membership failure.
- J2: candidate observation MSE ≤ `1e-12`.
- J3: absolute candidate/oracle prediction separation ≥ `0.5` on the committed intervention.
- J4: candidate intervention MSE < oracle intervention MSE − `0.1`.
- J5: candidate falsification MSE ≤ `1e-12` and < oracle falsification MSE − `0.1` on the independent falsification set.

A validated jump is exactly the conjunction J0∧J1∧J2∧J3∧J4∧J5. No aggregate or LLM judgment can override a failed gate.

## Outcomes and analysis

Primary outcomes are world-level JSR for jump worlds and FJR for controls. Secondary objective outcomes are abductive precision (validated candidates divided by candidates passing J0–J3), counterfactual gain, calls/tokens/evaluations/interventions per successful world, per-family JSR/FJR, structural descriptor coverage, and archive occupancy.

The primary aggregate is the equal-family macro-average. Uncertainty uses 10,000 deterministic family-stratified paired bootstrap replicates over world seeds. Within a replicate, seeds are resampled within each family and all conditions remain paired. Report percentile 95% intervals for each JSR and paired difference. Family results and ordinary pooled world intervals are also reported; candidates within a world are never treated as independent replicates.

The preregistered primary comparisons are B4−B0, B4−B1, B4−B2, B4−B3, B5−B0, B5−B1, B5−B2, and B5−B3. Holm correction at family-wise α=0.05 is applied to one-sided paired bootstrap p-values. The mechanistic factorial comparisons are P1−P0 and P2−P0 with Holm correction. FJR is reported with a two-sided Wilson 95% interval; “controlled” means its upper bound is ≤0.05 for B4 and B5.

## Exclusions and failure handling

There are no output-quality exclusions. Parse failures, invalid graphs, non-exact fits, no discriminating intervention, and failed falsification remain failures. If an HTTP, host, disk, or process failure occurs, the affected whole config shard is discarded and rerun from its frozen seeds before any condition analysis; both failure and rerun are logged. A code defect that could affect verdicts triggers an adversarial audit and full affected-config rerun, never a favorable-row patch. Families, seeds, operators, thresholds, and budgets will not change after the first confirmatory call.

## Frozen verdict tree

1. AJ0 if engine/oracle/local-adequacy/escape/prospective-freeze validity fails.
2. AJ1 if P0 is within 0.05 absolute JSR of P2 or P1 and its paired gap is not positive after correction.
3. AJ2 if B1 or B2 is within 0.05 absolute JSR of both B4 and B5, or external superiority is not supported after correction.
4. AJ3 if B3 reaches at least 80% of `max(B4, B5)` JSR or external representation-level superiority over B3 is unsupported.
5. AJ4 if representation mutation raises JSR but B4/B5 FJR upper bound exceeds 0.05.
6. AJ5 only if B4 and B5 each exceed B0–B3 after Holm correction, B4/B5 FJR are controlled, P1>P0 and P2>P0 after correction, P2 JSR≥0.80, and each of B4 and B5 succeeds in at least four families.
7. AJ6 is not available because no structural family is held out from development.

If multiple non-AJ5 clauses apply, report the earliest conservative verdict and the full claim matrix. A negative verdict is final and will not trigger model, family, budget, seed, threshold, or operator changes.

## Triggered ablations and adversarial audit

If AJ5 criteria are otherwise met, run frozen-code A1 no diversity (B4 versus B5), A2 report J4 candidates before J5, A3 remove crossover (the primary K=3 portfolio contains no crossover, so this is structurally null and must be reported as such), A4 B3 value-only, A5 B1 LLM-chosen mutation, and A6 random untyped/invalid mutation. These are mechanistic secondary analyses and cannot rescue the primary verdict.

Reviewer #2 must audit all 20 specified threats, including operator answer encoding, oracle strength, equal compute, template leakage, prospective freezing, post-hoc selection, family concentration, synthetic-world limits, and overgeneralization. Valid implementation defects require correction and complete affected rerun; conceptual limitations narrow the claim.
