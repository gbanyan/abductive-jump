# Measuring representation change in language-model discovery

**[AUTHOR NAMES AND AFFILIATIONS — REQUIRED BEFORE SUBMISSION]**

## Abstract

Hypotheses can be novel in wording or prediction while remaining inside a supplied representational language. We introduce a preregistered benchmark for a narrower event: escape from a frozen incumbent hypothesis language, followed by better prediction than its best admissible hypothesis on a committed intervention. Across eight synthetic families, typed external representation proposals enabled a frozen language model to validate escapes in 142 of 400 worlds, compared with 0–1 of 400 for direct, sampling-matched, fixed-space and attribute-only alternatives. Without family-level operators, four-step compositions of 29 generic graph rewrites succeeded in 400 of 400 known-family worlds and 100 of 100 worlds from a held-out structural family; random compositions succeeded in 52 and 13, respectively, whereas language-model compositions succeeded in none. No false jumps occurred in 300 control worlds. These results isolate representation proposal as a bottleneck in this benchmark, while remaining specific to a human-designed scaffold, one frozen model and synthetic worlds.

Abduction, conceptual change and scientific creativity are often described as changes in the space of possible explanations rather than better search within an unchanged space<sup>1–6</sup>. Computational systems can invent predicates and features<sup>7,8</sup>, restructure domain theories<sup>9</sup>, discover equations<sup>10,11</sup> and produce new algorithms by searching executable programs<sup>12,13</sup>. Language models have broadened this agenda: they can generate and update hypotheses<sup>14,15</sup>, guide program search<sup>13</sup> and participate in agentic scientific workflows<sup>16–20</sup>. Yet a high-scoring or unusual candidate need not change the representational language supplied by a task. Conversely, a structurally different candidate need not make a useful prediction.

This distinction creates a measurement problem. Natural-language novelty ratings, embedding distance and downstream performance do not establish that a candidate lies outside an incumbent hypothesis space. Nor does failure inside a supplied grammar distinguish inadequate reasoning from an inability to propose a more expressive representation. Work on computational creativity and constructive induction makes this conceptual distinction explicit<sup>4–9</sup>, but recent language-model benchmarks primarily measure generation, recovery, ranking or performance within task-defined spaces<sup>14,15,21,22</sup>. Broad scientific agents add tools, critique and experiments<sup>16–20</sup>, but their many interacting components make the source of a successful hypothesis difficult to identify.

Here we operationalize **bounded representation-level escape**. We freeze an incumbent typed grammar and its best admissible predictor, require a candidate to fail canonical grammar membership while fitting the same observations, and commit prospectively to an intervention on which candidate and incumbent disagree. A candidate succeeds only if it predicts the intervention and an independent falsification set better than the incumbent oracle. We first validate this assay across eight procedural families using atomic typed representation mutations. We then remove the family-level operator menu and ask whether local generic graph rewrites can be composed into successful representations, including in a preregistered held-out structural family. Proposal source and reasoning are separated while calls, candidate slots and interventions are held fixed. This design does not test human-like creativity or unrestricted science. It tests whether a frozen model embedded in a specified scaffold can cross a known representational boundary and earn that crossing prospectively.

## Results

### A prospective criterion for representation-level escape

Each procedural world supplied observations for which at least one hypothesis in a frozen incumbent language was exactly adequate. The eight families required, respectively, a latent common cause, unification, a hidden regime, conversion of a property into a relation, state invention, a coordinate transformation, resolution of causal ambiguity or a meta-law. The observations deliberately left the incumbent and target representations indistinguishable. A deterministic designer selected, from a finite public action set, the intervention that maximized separation between the fitted candidate and the incumbent oracle without observing its outcome (Fig. 1a–c).

A validated jump required every registered gate J0–J5 (Fig. 1d). The incumbent oracle first had to fit the observations (J0). The candidate had to be executable and outside the incumbent grammar (J1), fit the observations exactly (J2), and disagree materially with the incumbent on the frozen intervention (J3). Only then was the intervention revealed: the candidate had to improve on the incumbent by the registered margin (J4) and pass an independent falsification set (J5). World-level jump success rate (JSR) was the fraction of worlds with at least one validated candidate among three slots. False-jump rate (FJR) applied the same rule to matched control worlds whose truth lay inside the incumbent language. Candidate text, model confidence and semantic novelty never entered the verdict.

The unit of replication was a generated world, not a candidate. Confirmatory populations comprised 50 seeds in each of eight jump families (n=400) and 25 seeds in each of eight no-jump controls (n=200). Conditions shared worlds and had the same ex ante opportunity: three candidate slots, two model calls and one prospectively committed intervention per slot. Exact simulators, canonical graph hashes and full event records made every verdict replayable.

### Typed representation proposals outperform fixed-space alternatives

Direct model proposals (B0) and sampling-matched model proposals (B1) each succeeded in 1 of 400 worlds (0.25%). Repeated reasoning with the representation fixed (B2) and external changes restricted to incumbent-language attributes (B3) succeeded in 0 of 400. In contrast, externally sampled typed representation mutations (B4) and a structurally diverse variant with a falsification gate (B5) each succeeded in 142 of 400 worlds (35.5%; stratified bootstrap 95% CI, B4 31.0–40.25%; B5 31.0–40.0%; Fig. 2a).

All eight preregistered contrasts of B4 or B5 against B0–B3 were positive (one-sided paired bootstrap P=9.999×10−5; Holm-adjusted P=7.999×10−4 for each comparison). Successful worlds were distributed across all eight families: B4 family counts were 18, 29, 17, 12, 20, 13, 18 and 15 of 50; B5 counts were 16, 31, 13, 23, 13, 17, 16 and 13. Thus, the aggregate was not produced by one family.

No condition produced a false jump in 200 control worlds. For B4 and B5, the two-sided Wilson 95% upper bound was 1.88%, below the preregistered 5% threshold. This does not imply zero underlying risk; it bounds the risk supported by these controls. The external conditions also showed a monotonic opportunity curve: B4 succeeded in 53, 101 and 142 of 400 worlds after one, two and three slots, respectively, and B5 in 58, 96 and 142 (Fig. 2c). Fixed-space conditions remained near zero despite the same call, evaluation and intervention capacity.

### The proposal source is the limiting component

We next held the reasoner and three-slot/two-call path fixed while changing only the representation source. Model-proposed representations (P0) succeeded in 0 of 400 worlds, external typed proposals (P1) in 142 of 400, and an oracle-correct representation whose equation and outcomes remained hidden (P2) in 400 of 400 (Fig. 2b). P1−P0 and P2−P0 were significant after Holm correction (adjusted P=2.000×10−4 each). The reasoner could therefore use a correct or useful changed representation when supplied, whereas its proposal interface did not reliably produce one.

This attribution is to the tested interface, not to the model in isolation. The external proposer encoded a nine-member portfolio of generic but high-level structural changes. The equality of B4 and B5 further showed no measurable archive benefit in the primary portfolio. Removing the falsifier or crossover likewise did not change world-level JSR; crossover was never used by the primary three-candidate portfolio. Value-only mutation remained at zero, model selection from the mutation vocabulary reached 1 of 400, and random untyped edits reached 18 of 400. These outcomes suggested that typed representation proposals mattered, while also exposing a stronger alternative explanation: the high-level menu might contain prepackaged family answers.

### Generic rewrites compose into validated representations

We tested that explanation in a second, separately preregistered study. The nine atomic high-level operations were removed from the focal condition and replaced with 29 local graph/abstract-syntax-tree rewrites. Adding an untyped node, changing its type or observability, adding a function, changing relation arity and binding each argument were separate operations. No primitive accepted a family label, ground truth, target distance, outcome or semantic fitness judgment. Each candidate followed a linear ancestry of at most four operations.

Across the same eight structural families with new seeds (n=400 worlds), fixed-space search (C0) and all 192 generic depth-one alternatives (C2) succeeded in 0 worlds. The frozen atomic portfolio (C1), retained as a reference rather than a cost-matched condition, succeeded in 131 worlds (32.75%). Outcome-blind stratified traversal of four-step generic compositions (C3) succeeded in all 400 worlds (100%), as did the oracle representation (C5). C3 exceeded C0 and C2 by 1.0 (95% CI 1.0–1.0; one-sided paired randomization P=9.999×10−5; Holm-adjusted P=2.000×10−4; Fig. 3b).

The retained jump gain, defined relative to C0 and the atomic reference C1, was 3.053 (stratified bootstrap 95% CI 2.685–3.540; Fig. 3c). Values above one are possible because the generic traversal was not restricted to reproducing the three sampled atomic alternatives and explored a larger structured candidate set under the registered operation budget. This statistic therefore does not mean generic operators were three times intrinsically better than atomic ones; C1 and C3 have different operation semantics.

Two controls isolated composition from opportunity alone. Random four-step paths from the same primitive generator (C_rand) succeeded in 52 of 400 worlds (13.0%); the C3−C_rand difference was 0.87 (95% CI 0.845–0.895; Holm-adjusted P=3.000×10−4). The frozen model received the same primitive manifest and attempted three sets of 16 four-step plans (C_self), but succeeded in 0 worlds. As in AJ5, this identifies a limitation of the tested planning/output interface; malformed plans consumed their slots and the external system did not repair them semantically.

### Composition transfers to a held-out structural family

The second study preregistered a family excluded from AJ5 development, CJ5 pilot inference and known-family confirmation. In 100 `triadic_relation_reification` worlds, observations supported an incumbent cubic rule under correlated inputs, whereas the target reified an arity-three relation whose product mechanism was exposed by intervention. The primitive set contained reification and arity changes but no operation that created this target in one step.

C3 succeeded in 100 of 100 held-out worlds. C0, C1, C2 and C_self each succeeded in 0; C_rand succeeded in 13. The C3−C_rand difference was 0.87 (95% CI 0.80–0.93; Holm-adjusted P=3.000×10−4; Fig. 4b). C3 also produced no false jumps in 100 held-out-interface controls, for a combined C3 control count of 0/300 and Wilson 95% upper bound of 1.26%.

Every successful C3 candidate had registered ancestry depth four, and none of 17,280 evaluated depth-one alternatives validated. This establishes a depth-one lower bound and depth-four constructive upper bound within the registered operator system, not a globally minimal graph-edit or conceptual distance. The held-out claim is similarly bounded: AJ5 already included a binary property-to-relation family and the generic language contained a dormant reification operation. What was held out was the arity-three structure, product mechanism, generator and confirmatory instances—not the broad concept of reification.

All 10,800 selected AJ5 candidates and all 16,800 selected CJ5 candidates reproduced their representation, intervention and J0–J5 verdicts in deterministic replay, with zero mismatches. The CJ5 replay reconstructed 35,533 ancestry records. No confirmatory world was excluded and no shard was rerun in either study. Together, the results support compositional, prospective escape from the registered hypothesis spaces while locating that capability in the complete human-designed search-and-reasoning scaffold.

## Discussion

This study turns a broad claim about explanatory “jumps” into a bounded event with a prospective cost. A candidate must cross a frozen syntactic boundary, preserve the observations and then outperform the best incumbent explanation on an intervention selected before its outcome is known. Under this criterion, fixed-space search, additional model sampling and attribute mutation were insufficient in the tested worlds, whereas typed external proposals enabled reliable escapes. When atomic family-level operators were removed, outcome-blind compositions of generic rewrites not only retained the effect but succeeded on a preregistered held-out structural family.

The result connects computational accounts of transformational creativity and constructive induction<sup>4–9</sup> to recent executable and language-model-guided search<sup>12–15</sup>. FunSearch shows that frozen-model proposals can be selected by a deterministic evaluator to produce valuable programs<sup>13</sup>; hypothesis benchmarks assess generation, recovery and ranking<sup>14,15,21,22</sup>; falsification and multi-agent systems expand the scientific workflow<sup>16–20</sup>. Our complementary contribution is not broader autonomy. It is an assay that separates representation proposal from reasoning and distinguishes search within a language from prospective gain after leaving it.

The proposal factorial matters for this interpretation. The same frozen reasoner solved every world when given the oracle representation and a substantial fraction when given external typed proposals, but not when responsible for proposing the representation through the registered interface. The CJ5 self-composition result sharpened that gap. It should not be read as a universal inability of language models: it is conditional on Phi-4, its quantized runtime, prompt, decoding policy, plan syntax and finite budget. Nor should C3 be described as the model's unaided invention. Generic operators, traversal strata, structural ranking, exact fitters and simulators were designed by humans. The demonstrated capability belongs to their composition with the frozen model.

Several limitations constrain external validity. First, synthetic worlds trade ecological realism for exact oracles, exhaustive membership checks and uncontaminated outcomes. Success may not translate to scientific domains where representations are informal and interventions costly. Second, C3's perfect benchmark score suggests that the registered traversal is well aligned with these generators; it measures condition separation rather than a frontier ceiling. Third, the mutation language embeds meta-level priors about graphs, functions, relations and binding. Although it withholds family and outcome information, these priors are scientifically consequential. Fourth, the held-out relation is structurally new to the study but conceptually adjacent to an earlier binary relation family. Fifth, zero accepted controls provides an upper confidence bound, not proof of zero false discoveries.

A real-science extension should therefore preserve the prospective logic while weakening designer alignment: freeze domain ontologies before target selection, use interventions whose outcomes are genuinely unavailable to the system builders, compare multiple independently developed proposal languages and model families, and enlist domain experts to judge whether a formal structural change corresponds to explanatory value. Until then, the present result supports a narrower conclusion. Representation proposal can be an experimentally separable bottleneck, and a frozen language model can participate in overcoming it when embedded in a transparent, typed and falsifiable search process.

## Methods

### Study design and preregistration

AJ5 and CJ5 were frozen in Git before their respective confirmatory model calls. AJ5 used preregistration commit `895ebb9118ffd0046825b88868621f2a70f69f61`. CJ5 used commit `65f2087` with a documented pre-unlock correction at `7ecb977`; held-out execution was unlocked only at `27ee542`, after known-family and control shards were terminal. Pilot seeds were excluded. No confirmatory result caused a change to model, families, operators, thresholds, budgets or seeds.

### Model and inference

Both studies used frozen `microsoft/phi-4` revision `2db69c1c3e91a05d2c64a3185acfbaf36f744e25`, served with vLLM 0.10.2 from image digest `sha256:607442e407b0fea97f8a132a78b787c121a996dd4de181fa08e8da06e71ec2db` using dynamic bitsandbytes 4-bit quantization on one RTX 4090. The context limit was 4,096 tokens, temperature 0.2, top-p 0.95 and completion cap 700; the AJ5 sampling manipulation used temperature 0.7 for registered proposal calls. Each request had a deterministic seed. No fine-tuning, reinforcement learning or cross-world adaptation occurred.

### Procedural worlds and incumbent oracles

World generators returned public observations, a redacted action set, a frozen incumbent `LanguageSpec`, hidden truth and independent intervention/falsification cases. AJ5 used eight families and 50 jump seeds per family; CJ5 reconstructed them with 50 new seeds per family. No-jump controls used 25 seeds per family in each phase. CJ5 added 100 jump and 100 control seeds through the held-out interface. An exact or bounded exhaustive procedure verified local adequacy and produced the best incumbent prediction.

### Representations and search conditions

Representations were canonical typed graphs with executable fitted programs. AJ5 tested direct model output, model sampling, fixed-space reasoning, value-only mutation, sampled high-level representation mutation and structurally diverse mutation. CJ5 replaced the focal high-level portfolio with `GENERIC_PRIMITIVE_SET_V1`, comprising 29 local operations over nodes, edges, functions, equations, dependencies, constraints, temporal indices, types, observability, arity, bindings, reification, decomposition, copy and crossover. C3 traversed 48 four-operation branches using outcome-blind structural strata and retained three candidates. C_rand sampled 48 paths and selected by seeded structural hash. C_self requested 16 plans in each of three slots; invalid plans were not repaired.

### Prospective evaluation

For each candidate, deterministic fitting used observations only. J0 required incumbent observation MSE≤10−12; J1 required DSL validity and at least one frozen-language membership failure; J2 required candidate observation MSE≤10−12; J3 required absolute candidate–oracle separation≥0.5 on the selected action; J4 required candidate intervention MSE to improve on the oracle by >0.1; and J5 required candidate falsification MSE≤10−12 and >0.1 improvement over the oracle. The action, predictions, candidate hash and split hash were committed before simulator evaluation.

### Statistics

The world was the replicate. AJ5 macro-averaged families equally and used 10,000 deterministic family-stratified paired bootstrap replicates (seed 20260902) for percentile 95% intervals and one-sided paired P values. CJ5 used the same bootstrap for effects and paired random sign-flip tests for registered contrasts. Holm correction was applied within each preregistered comparison family at α=0.05. FJR intervals are two-sided Wilson 95% intervals. Exact n and denominators are stated with each result; candidate rows were never analyzed as independent replicates.

### Integrity and replay

Every request, representation, ancestry edge, fitted program, intervention commitment, gate value and configuration hash was retained. Replay reconstructed selected representations from the incumbent and mutation records and recomputed J0–J5. Infrastructure failures would have required an identical whole-shard rerun; none occurred. There were no outcome-quality exclusions.

### AI assistance in research and writing

The tested language model generated registered candidate and reasoning outputs as described above. OpenAI Codex was used after completion of all experiments to inspect repository artifacts, recompute lightweight audits, search literature, and assist with drafting and consistency checking. It did not choose confirmatory hypotheses, alter data, rerun inference or make authorship decisions. All numbers were traced to frozen artifacts; all citations and interpretations require author verification. Human authors retain responsibility for the work. **[DISCLOSURE REQUIRES EXPLICIT APPROVAL BY ALL AUTHORS BEFORE SUBMISSION.]**

## Data availability

All synthetic-world definitions, confirmatory result tables, comparison tables, manifests and replay artifacts are included in the project repository. Before submission, the authors will archive the exact release in a DOI-minting repository and replace this sentence with the accession and immutable link. No personal or third-party restricted data were used.

## Code availability

Source code for generation, search, evaluation, statistics and deterministic replay is included in the project repository. The submission release will identify the exact Git commit and an archival DOI. The frozen external model weights are not redistributed; model identifier, revision, runtime image and inference configuration are reported above.

## References

1. Peirce, C. S. Deduction, induction, and hypothesis. *Popular Science Monthly* **13**, 470–482 (1878).
2. Harman, G. H. The inference to the best explanation. *Philos. Rev.* **74**, 88–95 (1965).
3. Lipton, P. *Inference to the Best Explanation* (Routledge, 2004).
4. Boden, M. A. *The Creative Mind: Myths and Mechanisms* (Routledge, 2004).
5. Wiggins, G. A. A preliminary framework for description, analysis and comparison of creative systems. *Knowl.-Based Syst.* **19**, 449–458 (2006).
6. Wiggins, G. A. Searching for computational creativity. *New Gener. Comput.* **24**, 209–222 (2006).
7. Muggleton, S. & Buntine, W. Machine invention of first-order predicates by inverting resolution. In *Proc. 5th Int. Conf. Machine Learning* 339–352 (1988).
8. Stahl, I. Predicate invention in inductive logic programming. *Mach. Learn.* **13**, 287–320 (1993).
9. Donoho, S. K. & Rendell, L. A. Rerepresenting and restructuring domain theories: a constructive induction approach. *J. Artif. Intell. Res.* **2**, 411–446 (1995).
10. Schmidt, M. & Lipson, H. Distilling free-form natural laws from experimental data. *Science* **324**, 81–85 (2009).
11. Udrescu, S.-M. & Tegmark, M. AI Feynman: a physics-inspired method for symbolic regression. *Sci. Adv.* **6**, eaay2631 (2020).
12. Fawzi, A. et al. Discovering faster matrix multiplication algorithms with reinforcement learning. *Nature* **610**, 47–53 (2022).
13. Romera-Paredes, B. et al. Mathematical discoveries from program search with large language models. *Nature* **625**, 468–475 (2024).
14. Wang, Z. et al. Hypothesis Search: inductive reasoning with language models. In *International Conference on Learning Representations* (2024).
15. Zhou, Y. et al. Hypothesis generation with large language models. In *NLP4Science* 117–139 (2024).
16. Huang, A. et al. POPPER: automated hypothesis validation with language models. In *Proc. ICML*, PMLR **267** (2025).
17. Lu, C. et al. The AI Scientist: towards fully automated open-ended scientific discovery. Preprint at https://arxiv.org/abs/2408.06292 (2024).
18. Gottweis, J. et al. Towards an AI co-scientist. *Nature* (2026). https://doi.org/10.1038/s41586-026-10644-y
19. Swanson, K. et al. An autonomous multi-agent system for scientific discovery. *Nature* (2026). https://doi.org/10.1038/s41586-026-10652-y
20. Boiko, D. A. et al. Autonomous chemical research with large language models. *Nature* **624**, 570–578 (2023).
21. Chen, T. et al. HypoSpace: a diagnostic benchmark for set-valued hypothesis generation under underdetermination and sublinear coverage bounds. Preprint at https://arxiv.org/abs/2510.15614 (2025).
22. Liu, Y. et al. ResearchBench: benchmarking LLMs in scientific discovery via inspiration-based task decomposition. *Findings ACL* 13187–13207 (2026).
23. Koivisto, M. & Grassini, S. Best humans still outperform artificial intelligence in a creative divergent thinking task. *Sci. Rep.* **13**, 13601 (2023).
24. Hubert, K. F., Awa, K. N. & Zabelina, D. L. A comparison of human and AI creativity across domains. *Sci. Rep.* **14**, 2562 (2024).
25. Haase, J., Hanel, P. H. P. & Pokutta, S. Artificial muses: generative artificial intelligence chatbots have risen to human-level creativity. *J. Creat.* **35**, 100113 (2025).
26. Ding, A. W. & Li, S. Generative AI lacks the human creativity to achieve scientific discovery from scratch. *Sci. Rep.* **15**, 9587 (2025).
27. Pearl, J. *Causality: Models, Reasoning, and Inference* (Cambridge Univ. Press, 2009).
28. Peters, J., Janzing, D. & Schölkopf, B. *Elements of Causal Inference* (MIT Press, 2017).
29. Zahavy, T. Position: LLMs can't jump. ICML Position Paper/OpenPrint 20260728.0010v1 (2026).
30. Bran, A. M. et al. Augmenting large language models with chemistry tools. *Nat. Mach. Intell.* **6**, 525–535 (2024).
31. Zheng, Y. et al. Large language models for scientific discovery in molecular property prediction. *Nat. Mach. Intell.* **7**, 437–447 (2025).
32. Ektefaie, Y. et al. Evaluating generalizability of artificial intelligence models for molecular datasets. *Nat. Mach. Intell.* **6**, 1512–1524 (2024).
33. Kauffmann, J. et al. Explainable AI reveals Clever Hans effects in unsupervised learning models. *Nat. Mach. Intell.* **7**, 412–422 (2025).
34. Kim, Y. et al. Capable language models can outgrow the benefits of collaboration. *Nat. Mach. Intell.* **8**, 1157–1172 (2026).

## Acknowledgements

**[FUNDING AND ACKNOWLEDGEMENTS — REQUIRED BEFORE SUBMISSION]**

## Author contributions

**[CRediT-CONFORMANT AUTHOR CONTRIBUTIONS — REQUIRED BEFORE SUBMISSION]**

## Competing interests

**[COMPETING-INTERESTS STATEMENT — REQUIRED BEFORE SUBMISSION]**

## Correspondence

**[CORRESPONDING AUTHOR AND EMAIL — REQUIRED BEFORE SUBMISSION]**
