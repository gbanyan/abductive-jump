# NMI Claim Matrix

## Directly supported

- In eight procedural world families, direct LLM proposal and matched additional sampling each produced 1/400 validated jumps, while fixed-space search and value-only mutation produced 0/400.
- External representation-level mutation produced 142/400 validated jumps in both B4 and B5 and succeeded in every tested family; B5 did not outperform B4.
- With the reasoning path held fixed, LLM, external and oracle representation proposals produced 0/400, 142/400 and 400/400 successes.
- A 29-operation generic rewrite language contained constructive solutions at bounded depths 2–4, while none of 17,280 depth-one alternatives validated.
- Registered structured composition plus a fixed motif-to-basis realizer produced 400/400 known-family and 100/100 held-out successes. Matched depth-one search produced 0/400 and 0/100; matched random composition produced 52/400 and 13/100.
- The frozen Phi-4 self-composition condition produced 0/400 known and 0/100 held-out successes under the same primitive vocabulary and registered opportunity budget.
- The atomic high-level reference produced 131/400 known-family successes but 0/100 on the held-out structural family.
- C3 exceeded C_rand by 87 percentage points in both populations; both registered Holm-adjusted P values were 0.00029997.
- No false jumps were observed for any condition in 200 known-family and 100 held-out no-jump worlds. This does not imply zero population risk.
- All 10,800 AJ5 and 16,800 CJ5 selected candidates replayed deterministically with zero mismatches.
- Offline reconstruction of the original known-family Phi-4 C_self interface found 1,200/1,200 non-empty responses but 0/1,200 strict whole-response JSON parses and 0/19,200 executable plan opportunities; all responses reached the registered 700-token completion cap. This is an interface-attrition result, not evidence about the quality of valid proposals.
- All five minimal-extension shards were completion-verified, and inference-free replay reproduced 2,772/2,772 candidate rows with zero mismatches and zero model calls.
- On the identical fixed 96-world panel, historical Phi-4 4-bit, Phi-4 4-bit with a 2,048-token cap, Phi-4 8-bit, DeepSeek matched, DeepSeek native and Phi-4 8-bit with one validator repair each produced 0/96 world successes (Wilson 95% interval 0–3.8%); every registered paired JSR difference was 0.000.
- A separately frozen grammar-constrained DeepSeek sensitivity on the same panel produced 3,939/4,608 dynamically executable plan opportunities, 280/288 executable selected candidates and 15/96 successful worlds (15.6%; Wilson 95% interval 9.7–24.2%).
- Grammar-constrained candidate attrition was 236/280 through J1–J2 and 21/280 through J3–J5; its 21 validated candidates occurred in 15 worlds and all triggered the scaffold's `multi_argument_function` realizer.
- Grammar-constrained success was concentrated in meta-law (9/12) and unification (6/12); the other six families each produced 0/12. On the same panel, C_rand succeeded in 16/96, with 66 joint failures, 15 C_rand-only successes, 14 grammar-constrained-only successes and one joint success.
- Six validation-verified shards from the superseded broad extension are disclosed descriptively: matched DeepSeek, Phi-4 strict-schema decoding and Phi-4 one-repair on n=400 known-family and n=100 held-out populations. All yielded zero successful worlds; they are not a completed factorial.
- The separately frozen Phi-4 completion-budget condition retained the historical revision, 4-bit runtime, prompts, worlds, slots, attempts, interventions and J0–J5, changing only the cap from 700 to 2,048 tokens. It produced 0/400 known-family and 0/100 held-out successes. In the known-family population, 4,642/19,200 plan opportunities were schema-valid and 9 were executable, but these yielded one final candidate that failed J1; held-out executability was 0/4,800.
- Phi-4 8-bit, DeepSeek matched and the one-repair Phi-4 condition produced 0/4,608 schema-valid effective plan opportunities on the fixed panel. DeepSeek native returned reasoning text for all 576 calls but no separate parseable answer, with 518/576 calls reaching the 4,096-token cap.
- The balanced DeepSeek supplied-representation control produced 3/40 successful worlds (7.5%; Wilson 95% interval 2.6–19.9%). Four of 120 model-authored expression-and-intervention candidates were parse-valid and executable, and three passed J1–J5; 116/120 calls reached the cap.
- A separately frozen, inference-free realizer audit replayed 3,288 archived candidate slots under 11 policies, yielding 36,168 candidate-policy and 12,056 world-policy rows. Aligned replay reproduced every archived gate and verdict with zero mismatches.
- Disabling motif realization reduced C3 from 400/400 known-family and 100/100 held-out successes to 0/400 and 0/100, C_rand from 52/400 and 13/100 to zero, and grammar-constrained DeepSeek from 15/96 to zero. Cumulative J1–J2 still retained 1,168/1,500 C3, 1,040/1,500 C_rand and 236/288 DeepSeek candidate slots; none passed J3.
- Retaining motif algebra while rebinding variables without node roles or intervention-key inspection preserved 347/400 known-family and 100/100 held-out C3 worlds, 57/400 and 13/100 C_rand worlds, and 8/96 DeepSeek worlds. This is not a semantics-free condition because motif algebra remains supplied.
- Leave-one-signature-out replay removed 100 held-out C3 worlds when `relation_arity_3` was masked, 100 known-family C3 worlds when `unobserved_dependency` was masked, 50 C3 worlds when each other active nonredundant signature was masked, and all 15 DeepSeek worlds when `multi_argument_function` was masked. `shared_rule_binding` had redundant unification coverage and caused no world loss when masked alone.

The n=96 panel is a targeted sensitivity analysis and must never be described as replacing the original n=400 confirmatory study. The fixed n=96 slice is the primary paired Phi-budget comparison; the complete known-family n=400 and held-out n=100 budget populations are supplementary descriptive sensitivities, not new confirmatory populations. The P2 n=40 control is balanced but not paired to every n=96 condition and must be shown separately.

## Interpretation, not directly proven

- Representation proposal and search organization may be a major bottleneck for the tested frozen model, but the original C_self result alone cannot separate that possibility from truncation and serialization failure.
- The unchanged 0/96 rates show that 4-bit precision, the historical 700-token cap alone, one validator-only repair and simple substitution of the tested stronger checkpoint do not by themselves remove the bottleneck under these interfaces.
- Because autonomous candidates almost never reached execution under the legacy interfaces, those runs cannot distinguish weak conceptual proposals from structural serialization failure. Native DeepSeek's legacy 0/96 is especially an interface result because reasoning consumed the frozen output budget without a separate answer.
- The grammar-constrained condition shows that the legacy DeepSeek interfaces hid executable model-generated graph topology. The model did not exceed C_rand in aggregate, and the scaffold supplied realization, fit, ranking and intervention.
- The concentration of success in two families and the reduction from 236 J2-passing candidates to 21 J3-passing candidates show that syntax was not the only limitation; performance remained strongly dependent on the tested structural family and prospective-separation requirement.
- DeepSeek P2 shows that the served checkpoint can sometimes use a supplied representation; 3/40 is a limited positive control, not evidence of reliable supplied-representation reasoning.
- Abductive reasoning may be usefully decomposed into representation proposal, downstream reasoning and prospective validation.
- A phenomenologically discontinuous explanatory jump may sometimes be implemented as a sequence of computationally local representation transformations.
- Structured search priors, rather than raw sampling volume alone, appear responsible for much of C3's advantage over random composition.
- The held-out result suggests limited search-side structural generalization beyond family-aligned atomic operators. Its triadic-product basis was already present in the fixed realizer, so it is not an unseen-mechanism realization test.
- The realizer audit identifies causal dependence of archived verdicts on the supplied motif basis. Because candidates were originally selected under the aligned pipeline, it does not estimate how search would adapt if rerun under a different realizer.

Any sentence expressing these points must use interpretive qualifiers and remain tied to the controlled procedural setting.

## Prohibited claims

- LLMs generally cannot jump or are incapable of abduction.
- Human creativity, intuition or scientific creativity has been reproduced or explained.
- The system autonomously invented representations from nothing.
- The results establish general scientific discovery, AGI or arbitrary theory discovery.
- Programmatic representation mutation is equivalent to human intuition.
- Zero observed false jumps means the true false-jump rate is zero.
- World models or agents are unnecessary.
- The representation meta-language is unconstrained.
- The result applies to all models, domains or LLMs.
- The targeted n=96 sensitivity panel is a new preregistered or replacement confirmatory population.
- The held-out family is wholly conceptually novel.
- The study proves Zahavy's position wrong or proves a computational impossibility claim.

## Maximum publication claim

In controlled procedural worlds, structured search combined generic representation rewrites with a fixed, family-aligned motif realizer to produce prospectively validated explanations outside locally adequate incumbent hypothesis spaces. Counterfactual replay showed that the semantic motif library was necessary for every archived validated escape, while role-aware field binding was necessary only for a subset. A grammar-constrained model supplied successful edit topology in 15/96 panel worlds but did not exceed random composition in aggregate; the scaffold supplied the realized laws and interventions. The result does not establish autonomous representation invention or general scientific discovery.
