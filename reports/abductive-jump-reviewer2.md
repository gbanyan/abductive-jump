# Reviewer #2 Adversarial Audit

Verdict after audit: **AJ5 survives, but only for the narrow comparative claim in the tested procedural worlds. AJ6 and any general discovery claim are rejected.** The archive, falsifier, and crossover mechanisms receive no empirical support.

1. **Is this merely a genetic algorithm?** No primary condition performs population evolution, selection across generations, or learned adaptation. B4/B5 sample a fixed mutation portfolio. Calling the result “evolutionary discovery” would be inaccurate; it is a proposal-distribution intervention.

2. **Does the mutation language hard-code answers?** This is the strongest valid criticism. The portfolio contains square, affine-context, sign-regime, latent, state, relation, invariant, and causal motifs closely aligned with the generators. Family identity and outcomes are hidden, K=3 sampling prevents a ceiling, and A6 random edits reach only 4.5%, but co-design remains. The claim is narrowed to this portfolio and these worlds.

3. **Do candidates genuinely leave `H(R0)`?** Yes. J1 is computed by frozen `LanguageSpec.membership_failures`; coefficient and value changes remain within-space. B2/B3 produced zero J1 successes. Replay reproduced every gate.

4. **Is the incumbent oracle strong enough?** Yes for the included families: every oracle is exact finite enumeration with a certificate, fitted only on observations. No approximate optimizer is used.

5. **Does B5 simply get more compute?** No. Every cell has six calls, three candidates, three interventions, and identical completion capacity. B4/B5 actually used fewer completion tokens than B0. Wall time is secondary.

6. **Does semantic novelty affect the verdict?** No embedding, lexical, human, or model novelty score enters J0–J5, selection, statistics, or the verdict.

7. **Is there benchmark template leakage?** Opaque node/variable names, random parameters, nuisance measurements, and disjoint seeds reduce surface leakage. Structural motifs remain recognizable and were all seen in development. This blocks a generalization claim.

8. **Might the LLM know these patterns from training?** Yes; latent confounding, state, regimes, and transforms are common concepts. Yet P0/B0/B1 were near zero while P2 was perfect, so memorized concepts did not eliminate the proposal gap under this interface. Training-data causality cannot be established.

9. **Are synthetic worlds too artificial?** Yes for external validity. Exact oracles and clean interventions enable causal attribution but simplify real science. The result is a mechanistic benchmark finding only.

10. **Are no-jump false positives excessive?** No observed false jump occurred in any primary, factorial, or A6 condition. For B4/B5, 0/200 gives a 95% Wilson upper bound of 1.885%.

11. **Is representation mutation just hyperparameter search?** Not under the frozen definition: B3 hyperparameter/value variants remain in `H(R0)` and score 0%; B4/B5 require graph kinds/relations/counts/equation families outside the incumbent language.

12. **Do external operators directly encode the ground-truth family?** They do not inspect the family at runtime, but the portfolio was designed with the family set in view. This is not fatal to the narrow condition comparison, but it is fatal to claims of open-ended invention. A held-out structural family is required next.

13. **Does the experiment designer see simulator truth?** It sees public action inputs plus candidate and exact incumbent-oracle predictions, not intervention outcomes or the truth program. Finite actions are enumerated and maximum separation is chosen before reveal.

14. **Are predictions prospectively frozen?** Yes. Candidate hash, expression, case, prediction, split hash, and commitment digest are formed before evaluator outcome access. Replay regenerated 10,800 commitments.

15. **Is candidate selection post-hoc?** No. Three slots are fixed per world. Each candidate selects one action before its outcome. World success is the preregistered “any of three” rule applied equally to every condition.

16. **Does success come from one or two families?** No. B4 and B5 each succeeded in all eight families. Per-family rates vary, and the full table—not only a macro score—is retained.

17. **Is Phi-4 simply too weak to reason?** P2 passed 400/400 worlds, so the shared reasoning/fitting interface has a 100% ceiling. This does not imply Phi-4 is generally strong; it isolates proposal failure under the benchmark.

18. **Would a stronger LLM erase the gap?** Possibly. No >14B or reasoning model was tested by policy. The conclusion is model- and interface-specific.

19. **Can proposal and reasoning bottlenecks be distinguished?** Yes within the scaffold: P0=0%, P1=35.5%, P2=100% with the same downstream reasoner. P1 is still below P2 because K=3 samples only part of a fixed portfolio.

20. **Is “LLMs cannot jump” overgeneralized?** It must not be stated. B0 and B1 each achieved one jump, P2 was perfect, and only one frozen model was studied. The supported claim is comparative reachability under tested procedural worlds.

## Additional audit findings

- **Archive mechanism unsupported:** B4 and B5 both reached 35.5%; A1 found no gain. Their successful sets differ because sampling differs, not because B5 improves aggregate rate.
- **Falsifier mechanism unsupported:** the pre-J5 and post-J5 world success rates were identical. J5 is still important as a validity gate, but it did not explain the treatment effect.
- **Crossover not tested:** A3 is null because the primary portfolio did not use crossover. No claim about crossover is allowed.
- **Interface asymmetry remains:** B0 emitted full graphs and had 41.2% fallback slots; B1 compact plans had 14.7%. External conditions had no proposal parse burden. That asymmetry is part of the proposal-source manipulation but also contributes to the effect. P2 establishes downstream competence, not interface neutrality.
- **Actual generated tokens differ:** ex ante caps, calls, evaluations, and interventions are identical, but EOS makes actual token totals unequal. Since B0 used more tokens than B4/B5, this cannot explain the external advantage; nevertheless “exact actual-token matching” should not be claimed.
- **B2 is bounded rather than fully autonomous:** it has a two-stage fixed-representation interpretation/reasoning loop but no open-ended tool feedback. The result rules out this matched scaffold, not every conceivable fixed-space agent.
- **B3 confirmatory search was a value-attribute subset:** the separate `G_H` implementation covers mutation, crossover, and exchange and proves they cannot pass J1 while the graph is frozen. The primary 0% result should not be read as an empirical ranking among all within-space optimizers.
- **QD retention was not causal:** B5 materializes three stable archive bins per world, but candidates were selected for structural distinction before evaluation. The archive did not guide a multi-generation search, and B5=B4 confirms no measurable archive effect.

No implementation defect found in this audit changes the frozen gates or primary result. The replay and bootstrap bugs were analysis-only, corrected with tests, and documented. The narrow AJ5 claim survives; claims of a general abductive learner, archive benefit, falsifier benefit, held-out generalization, or universal LLM inability do not.
