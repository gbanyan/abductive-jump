# Model calibration

Status: pilot; no primary model/config is frozen and no confirmatory result has been run.

## Compute and runtime

- Host: `GBLinux`, NVIDIA RTX 4090, 24,564 MiB VRAM.
- Driver 595.84; host-reported CUDA 13.2.
- Engine: vLLM 0.10.2, container digest `sha256:607442e407b0fea97f8a132a78b787c121a996dd4de181fa08e8da06e71ec2db`.
- Context cap: 4,096 tokens. All inference used one GPU on `gblinux`; no fine-tuning or larger host was used.

## Rejected candidate: Qwen2.5-14B-Instruct-AWQ

- Official revision: `539535859b135b0244c91f3e59816150c8056698`.
- Quantization: official AWQ 4-bit.
- Eight-family free equation-realization scan: JSON parse 8/8, validated oracle-mutation success 0/8. J2 observational compatibility failed in all eight; the model repeatedly incorporated known nuisance variables or asserted arithmetic checks that were false.
- Decision: rejected under the preregistered oracle-reasoning-floor policy. Full prompts, outputs, tokens, seeds, and gate results are retained in `artifacts/pilot/calibration-oracle-scan/`.

## Candidate: Microsoft Phi-4

- Official revision: `2db69c1c3e91a05d2c64a3185acfbaf36f744e25`.
- 14B dense ordinary instruct model; dynamic bitsandbytes 4-bit under the pinned vLLM runtime.
- Free equation realization after graph-delta and nuisance-interface repairs: validated success 2/8. It fit observations more often than Qwen but remained below the required oracle competence.
- Mechanistic interface change: a family-blind deterministic realization layer now fits the hypothesis genome licensed by any supplied typed representation. It receives only public observations, the candidate graph, and known nuisance labels. The same fitter will be shared by every condition. The LLM is then responsible for coherent interpretation and prospective experiment selection; exact code supplies candidate-versus-incumbent prediction separation without simulator outcomes.
- Unit evidence: the shared fitter produces J0–J5-valid ground-truth realizations for all eight families without receiving family labels or truth programs.
- Oracle supplied representation + shared fitter, with one no-op distractor and exactly one permitted intervention choice: validated success 8/8; parse 8/8.
- Spontaneous two-stage scans (LLM proposes representation, same fitter and experiment interface): validated success 0/24 across three world seeds and two decoding regimes; no candidate passed J1. This is below the desired 5–30% calibration band and requires sampling/budget calibration before freezing.
- Family-blind external portfolio reachability, without LLM calls: at least one candidate passed J0–J5 in 800/800 jump worlds, while 0/800 matched no-jump worlds produced an accepted jump (14,400 candidates total). This is a reachability ceiling, not a condition result: it uses all nine generic typed variants and therefore does not yet measure budgeted selection or rule out operator-suite benchmark alignment.

## Interpretation

The successful oracle condition is not evidence for the primary hypothesis by itself. It establishes that the post-proposal pipeline has a high ceiling after exact within-representation coefficient fitting and exact experiment comparison. The initial spontaneous result suggests a proposal gap but is too small and too close to floor to freeze or claim. The estimand is correspondingly narrow: representation proposal under a shared exact realization scaffold, not unaided free-form equation induction.

## Next calibration gates

1. Run B1 sample-matched proposal pools to determine whether ordinary sampling escapes the J1 floor.
2. Run P1 external family-blind proposals through the identical fitter/reasoner under a matched candidate/intervention budget.
3. Finalize B0–B5 call/token/evaluation/intervention accounting.
4. Only then freeze model, prompt/parser/fitter versions, seeds, thresholds, and budgets in preregistration.
