# A prospective assay for hypothesis-space expansion in AI systems

## Abstract

Scientific discovery can require changing not only a hypothesis but the language in which hypotheses are expressed. Existing evaluations rarely make that boundary, or the cost of crossing it, testable. We introduce a prospective assay for bounded hypothesis-space expansion. A candidate must be structurally outside a frozen incumbent language, fit existing observations, commit to a discriminating intervention before its outcome is revealed, outperform the best incumbent predictor and survive independent falsification. Across synthetic mechanistic worlds, typed high-level proposals succeeded in 142 of 400 cases, whereas direct, sampled, fixed-space and attribute-only alternatives succeeded in 0–1. Compositions of generic local rewrites succeeded in 400 of 400 known-family and 100 of 100 held-out-family worlds. A post-hoc component audit reproduced all C3 verdicts without language-model outputs, locating this result in the deterministic search scaffold rather than the model. The assay enables auditable attribution of hypothesis-space expansion while exposing saturation and limited external validity.

## Introduction

Abduction selects an explanatory hypothesis, but scientific change sometimes alters the representational vocabulary in which hypotheses can be stated<sup>1–3</sup>. Computational creativity and constructive-induction research formalized related distinctions between exploration within a space and transformations of that space<sup>4–9</sup>. Symbolic regression, program search and language-model-guided systems can discover useful equations, algorithms and hypotheses<sup>10–17</sup>, while multi-agent systems increasingly automate broader scientific workflows<sup>18–20</sup>.

Recent work now explicitly targets expanding principle or model spaces. PiEvo treats discovery as optimization over an evolving principle space across four benchmarks<sup>21</sup>. Model Discovery Agent couples a language-model proposer to Bayesian experiment design in an open model setting spanning physics, chemistry and biology<sup>22</sup>. HypoArena evaluates prospective hypothesis discovery in 988 cases across six domains and 15 frontier models<sup>23</sup>. EvoSCM evolves structural causal models through intervention and prospective prediction<sup>24</sup>. These studies broaden the scientific tasks and models under evaluation. A complementary measurement problem remains: how can an evaluation prove that a candidate left a specified incumbent hypothesis language, charge it a prediction before seeing the answer, and separately identify which system component caused the escape?

Here we operationalize **bounded hypothesis-space expansion**. We freeze an incumbent representational language, generate executable candidates and require a six-gate verdict: incumbent adequacy (J0), canonical structural non-membership (J1), candidate adequacy (J2), a discriminating committed prediction (J3), prospective intervention gain (J4) and independent falsification survival (J5; Fig. 1). Candidate prose, model confidence, embedding distance and semantic novelty do not enter the verdict.

Our experiments validate the assay and reveal a component-attribution limit. Typed proposals and generic compositional search cross the frozen language reliably, whereas fixed-space alternatives do not. However, a code-path audit and inference-free replay show that C3's representations, fitted equations, structural ranking and interventions were deterministic; removing the model output leaves all 500 jump and 300 control verdicts unchanged. The central contribution is therefore the prospective assay and a transparent typed search scaffold—not evidence that a language model was necessary for the successful escapes.

### Table 1 | Position relative to adjacent discovery evaluations

| Evaluation | Executable hypotheses | Frozen formal language | Proves non-membership | Prospective intervention | Independent falsification | Proposal/reasoning separation | Deterministic replay | Breadth |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| Hypothesis Search / HypoGen | partial | no | no | no | no | no | no | language tasks |
| POPPER | partial | no | no | yes | yes | no | partial | literature claims |
| FunSearch | yes | fixed program skeleton | no | evaluator feedback | held-out tests | proposer/evaluator | partial | mathematics |
| PiEvo | yes | evolving principle space | no formal certificate | benchmark dependent | benchmark dependent | proposer/search | no exact replay claim | 4 benchmarks, multiple backbones |
| Model Discovery Agent | yes | open model set | no formal certificate | Bayesian experiment design | posterior predictive checks | proposer/inference | implementation dependent | physics, chemistry, biology |
| HypoArena | judged text | no | no | context regression | rubric/judge | no | no | 988 cases, 6 domains, 15 models |
| EvoSCM | yes | evolving causal models | no frozen-language certificate | active intervention | prospective prediction | model evolution / selection | implementation dependent | synthetic causal systems |
| This work | yes | yes | canonical certificate | outcome locked | independent exact cases | factorial + component audit | exact | 9 synthetic families, 1 model |

## Results

### A prospective criterion for hypothesis-space expansion

Each synthetic world contains observations compatible with an incumbent model, a frozen typed-graph language, hidden intervention outcomes and independent falsification cases. The best incumbent predictor is computed exactly or by bounded exhaustive search. Before any intervention outcome is revealed, a candidate representation, executable expression, selected action, prediction and split hash are committed. A validated jump is the conjunction J0∧J1∧J2∧J3∧J4∧J5 (Fig. 1). This design turns “leaving a hypothesis space” into a replayable event rather than a judgement about wording or apparent novelty.

### Typed proposals outperform fixed-space alternatives

In AJ5, direct model proposals (B0) and sampling-matched proposals (B1) each succeeded in 1 of 400 worlds. Fixed-space reasoning (B2), attribute-only mutation (B3) and value-only mutation succeeded in none. External typed representation proposals succeeded in 142 of 400 worlds in both B4 and B5 (35.5%; Fig. 2a). All eight registered comparisons of B4 or B5 against B0–B3 were positive after Holm correction (adjusted P≤4.00×10−4).

The proposal-source factorial held the downstream path fixed. Model-proposed representations (P0) succeeded in 0 of 400 worlds, external typed proposals (P1) in 142, and oracle representations (P2) in 400 (Fig. 2b). This shows that the tested system can execute a supplied changed representation. It does not establish that the model is needed after deterministic fitting, because the fitted expression and maximum-separation intervention were supplied to the second call and programmatically enforced.

Candidate-level gate attrition clarifies the result (Fig. 2c). In jump worlds, B4 had 1,200 candidates at J0, 823 through J1, 573 through J2, 270 through J3 and 154 through J4–J5. B5 had 1,200, 838, 562, 262 and 145, respectively. In controls, B4 and B5 still produced 112 and 110 candidates through J3, but none passed J4. The zero-control result is therefore not created by J0–J3 alone; prospective outcomes eliminate apparently admissible escapes.

### Generic rewrites compose into validated representations

CJ5 replaced nine high-level mutations with 29 local graph and abstract-syntax-tree rewrites. Adding a node, changing its type or observability, changing arity and binding each argument were separate steps. No primitive accepted a family label, target distance or outcome. C3 deterministically traversed 48 four-step branches, ranked candidates using observational fit, structural escape and prospective prediction separation without outcomes, and retained three.

Across eight known structural families with new seeds (n=400 worlds), fixed-space search (C0) and 192 generic depth-one alternatives (C2) succeeded in no worlds. The frozen atomic reference (C1) succeeded in 131 (32.75%), random four-step paths (C_rand) in 52 (13.0%), and C3 in all 400 (Fig. 3). C3 exceeded C_rand by 0.87 (95% CI 0.845–0.895; Holm-adjusted P=3.00×10−4). C3 was 100% in every family; this demonstrates within-generator reliability and assay separability, not eight statistically independent replications or an unsaturated frontier benchmark.

C_self also scored 0/400, but its failure is narrower than initially anticipated. Offline reconstruction made no new model calls. The 400 known-family worlds yielded 1,200 non-empty proposal responses, each carrying 16 registered plan opportunities. The legacy parser extracted a JSON object from every response, but none had a valid outer `plans` list; consequently 0/19,200 plan opportunities reached execution or J1. All 1,200 responses reached the 700-token completion cap, and none was strict whole-response JSON. The historical 0/400 therefore cannot distinguish weak representation proposals from truncation and serialization failure.

### A deterministic component audit removes the language model

Inspection of the frozen C3 execution path showed that the representation, expression, candidate ranking and selected intervention were generated deterministically before the model response. The response's representation, expression and intervention fields were overwritten; only its explanation remained, and explanation does not enter J0–J5. We therefore performed a post-hoc, inference-free ablation that replaced both model calls with a valid empty explanation and recomputed every C3 theory and commitment from the archived representation, expression and intervention.

All 2,400 candidate verdicts matched the archive. The model-free replay retained 500/500 jump-world successes and 0/300 control-world false jumps (Fig. 4). Thus Phi-4 was not causally necessary for C3 under the implemented path. AJ5 still measures differences among model-facing proposal interfaces, but the perfect C3 result belongs to the typed deterministic search-and-evaluation scaffold. This audit changes the system attribution, not the validity of the prospective assay.

### Transfer to one held-out structural family

The second study reserved `triadic_relation_reification` from AJ5 development, CJ5 pilot inference and known-family confirmation. Observations supported an incumbent cubic rule under correlated inputs; the target reified an arity-three relation exposed by intervention. C3 succeeded in 100 of 100 held-out worlds, C_rand in 13, and C0, C1, C2 and C_self in none. C3 exceeded C_rand by 0.87 (95% CI 0.80–0.93; adjusted P=3.00×10−4).

The holdout is limited. The earlier study contained a binary property-to-relation family, and the generic language already contained reification. What was new was the arity-three structure, product mechanism, generator and instances. Success across a single conceptually adjacent family cannot support broad external generalization.

### A worked prospective escape

In one held-out world, observations with x=z=w gave y=9x³, so the incumbent `y=9x³` and candidate `y=9xzw` both fit exactly. Four generic edits reified the incumbent prediction edge, changed the new relation to arity three, and bound z and w (Fig. 5). Before outcome reveal, the assay committed to setting z from 6 to 7 at x=w=6. The incumbent predicted 1,944; the candidate predicted 2,268; the revealed outcome was 2,268. Independent falsification at z=5 yielded 1,620, again exact for the candidate. The representation failed the frozen language on relation count, type, arity bindings and result structure, and passed J0–J5.

### Specificity and replay

The zero false-jump count requires qualification. In C3 controls, 800 of 900 candidates passed J1, 567 passed J2 and 283 passed J3, but none passed J4. The null was therefore non-trivial through the prospective commitment gate. Nevertheless, because no-jump truth is generated inside the incumbent language and the incumbent oracle is exact, an outside candidate cannot strictly beat it under noiseless evaluation. The observed 0/300 is best interpreted as a structural-specificity check under the exact simulator, not an empirical false-positive estimate for noisy science; the Wilson upper bound is descriptive only.

All 10,800 AJ5 and 16,800 CJ5 selected candidates replayed exactly, including 35,533 CJ5 ancestry records. No confirmatory world was excluded and no shard was rerun.

## Discussion

This work contributes an assay for a specific event: an executable candidate leaves a frozen hypothesis language and pays for that move with a prospective prediction that beats the best incumbent and survives independent falsification. Canonical non-membership, outcome-before-commitment ordering, proposal-source factorials, false-jump controls and deterministic replay distinguish the assay from broader discovery benchmarks (Table 1).

The experiments also show why component attribution must be audited at code-path level. AJ5 indicates that typed external proposals reach useful representations more often than the registered model interfaces. But C_self never crossed its parser, and C3 did not require the model output. The defensible mechanistic result is therefore that typed representation search can cross a frozen space and that interface failures can be separated from downstream executability. Claims of language-model-driven representation change would require a redesigned path in which model-generated scientific content survives into the committed theory, plus a true minus-model ablation.

External validity is the principal limitation. The worlds are synthetic and noiseless; C3 is saturated; search strata and generators were co-designed; the operator language embeds graph, function, relation and binding priors; only one model and one adjacent held-out family were tested. World seeds quantify within-generator reliability. The higher-level generalization units are nine structural families, only one of which was held out, so small world-level P values do not substitute for structural breadth.

A decisive extension should freeze the current assay and add independently authored families, distractor primitives, deeper compositions, stochastic observations, partial observability and at least one recognizable mechanistic simulation. It should compare a stronger open model and a frontier model, with raw, grammar-constrained and validator-repair interfaces, and report parse validity and cumulative J0–J5 attrition. These experiments are proposed, not part of the present evidence.

The current conclusion is narrower but useful: hypothesis-space expansion can be measured prospectively and replayed exactly; typed deterministic search can produce it in controlled worlds; and the assay exposes when an apparent language-model capability is actually supplied by the surrounding scaffold.

## Methods

### Study design and protocol freezing

AJ5 and CJ5 protocols were frozen in Git before their reported confirmatory model calls. AJ5 uses commit `895ebb9118ffd0046825b88868621f2a70f69f61`. CJ5 uses `65f20874e16bddf8a7ae36996395ff52b27153b7`, with a documented correction at `7ecb977` and held-out unlock at `27ee542`. The commits are publicly retrievable but unsigned, and no independent registry or transparency-log timestamp was located. We therefore describe the studies as prospectively specified and commit-frozen, not formally preregistered. Pilot seeds were excluded; no confirmatory result changed families, operators, thresholds, budgets or seeds.

### Model and inference

Both studies used frozen `microsoft/phi-4` revision `2db69c1c3e91a05d2c64a3185acfbaf36f744e25`, vLLM 0.10.2, dynamic bitsandbytes 4-bit quantization, a 4,096-token context, temperature 0.2, top-p 0.95 and completion cap 700. AJ5 sampling proposals used temperature 0.7. Each request had a deterministic seed. No fine-tuning or cross-world adaptation occurred.

### Minimal targeted sensitivity extension

The original Phi-4 artifacts were preserved at commit `ae1ede683fdef09f2bf60f6e1052b60394ad6cf8`, tag `nmi-phi4-frozen-2026-09` and archive branch `nmi-phi4-frozen-archive-2026-09`. A separate extension protocol, panel, model configurations and generation code were frozen at commit `320eb29b33ddaed596b0fe7b3f1d5895c706f311` and amended only for operational execution at `f846c89287e379fe313551c47765c24f2abf4959`. New outputs used the `nmi_minimal_sensitivity_v1` namespace and could not overwrite historical files.

An outcome-blind SHA-256 ranking selected 12 of the 50 historical CJ5 seeds before any new model call: 30014, 30012, 30029, 30025, 30011, 30023, 30000, 30032, 30001, 30037, 30002 and 30015. Applying the same seeds to all eight known families produced a fixed 96-world paired panel. The positive control used the first five selected seeds in each family (n=40). This extension is a targeted sensitivity analysis, not a replacement confirmatory population.

The frozen run matrix contained Phi-4 8-bit C_self on 96 worlds; DeepSeek matched C_self with `reasoning_effort=none` on the same worlds; DeepSeek native C_self with `reasoning_effort=max`; and a supplied-correct-representation DeepSeek positive control. The DeepSeek service identified the checkpoint as `deepseek-ai/DeepSeek-V4-Flash-Vision-Exp`, revision `86f746b36186f0e567729a5c06a8c918caba82a9`, served as `deepseek-v4-flash-vision-exp` by vLLM `0.25.2.dev0+g752a3a504.d20260714`. We do not equate this checkpoint with any other DeepSeek release. The matched condition retained the historical 700-token output cap; the native and positive-control conditions froze a 4,096-token output cap. Reasoning text was returned separately in `message.reasoning`; a separate reasoning-token count was recorded only if exposed by the service.

Worlds, primitive vocabulary, three candidate slots, 16 four-step plans per slot, representation opportunities, J0–J5, prospective interventions and hidden-information boundaries were unchanged. The matched condition received no additional semantic information. The positive control fixed only the correct representation; the model still authored the executable expression, explanation and intervention selection, so success could not be created by overwriting those fields. Because the offline historical cascade had 100% pre-executable attrition, exceeding the frozen 25% trigger, one additional Phi-4 8-bit condition permitted exactly one replacement repair response per structurally invalid slot. Validator feedback named only syntax, schema, operation, reference, type or arity errors and exposed no truth, target distance, outcome or gate value.

### Worlds, representations and search

Generators returned public observations, redacted actions, a frozen incumbent `LanguageSpec`, hidden truth and independent intervention and falsification cases. AJ5 used eight families and 50 jump seeds per family; CJ5 used 50 new seeds per family. No-jump controls used 25 seeds per family in each phase. CJ5 added 100 held-out jump and 100 control seeds. Representations were canonical typed graphs with executable fitted programs.

AJ5 tested direct model output, model sampling, fixed-space reasoning, attribute-only mutation and two typed high-level proposal conditions. CJ5 used 29 generic local rewrites. C3 traversed 48 four-operation branches and retained three candidates by a deterministic score. C_rand sampled 48 four-step paths. C_self requested 16 plans in each of three slots; invalid plans were not repaired.

### Prospective evaluation

J0 required incumbent observation MSE≤10−12; J1 required DSL validity and frozen-language non-membership; J2 required candidate observation MSE≤10−12; J3 required candidate–oracle prediction separation≥0.5 on the committed action; J4 required intervention MSE improvement>0.1; J5 required falsification MSE≤10−12 and improvement>0.1. Candidate, prediction, action and split hashes were committed before simulator evaluation.

### Statistics and component audit

The world was the replicate. AJ5 used 10,000 family-stratified paired bootstrap replicates; CJ5 used the same bootstrap for effects and paired sign-flip tests. Holm correction was applied within prospectively specified comparison families at α=0.05. Candidate rows were used only for attrition. Family-level distributions are reported descriptively because eight known families plus one held-out family do not support a stable population-level family inference.

The post-hoc component audit reconstructed all C3 candidates from archived deterministic representations, fitted expressions and selected interventions, replacing the model-derived explanation with an empty string. It then regenerated each world, froze a new commitment and recomputed J0–J5. No model inference was run.

For the targeted sensitivity analysis, exact world counts, JSR and Wilson 95% intervals are primary. Comparisons use paired world transitions and paired JSR differences on the identical 96-world panel; family rates are descriptive. The n=40 positive control is shown separately. No candidate-level significance tests are performed and P values are not used as primary evidence. Response and plan attrition are reported with their denominators, followed by executable-candidate J1–J5 attrition.

### Integrity and replay

Requests, representations, ancestry edges, fitted programs, commitments, gate values and configuration hashes were retained. Replay reconstructed representations and recomputed J0–J5. Infrastructure failures would have required whole-shard reruns; none occurred. There were no outcome-quality exclusions.

### AI assistance in research and writing

Phi-4 generated the original registered outputs described above. OpenAI Codex was used after the original confirmatory experiments to inspect artifacts, implement and orchestrate the separately frozen targeted sensitivity extension, recompute inference-free audits, verify literature metadata and assist drafting. It did not choose hypotheses using observed outcomes, alter historical source data or change the frozen evaluation rules. Human authors verified the cited metadata and remain responsible for originality, accuracy and integrity.

## Data availability

Synthetic-world definitions, result tables, manifests and replay artifacts are included in the project repository. The submission release will archive an exact commit in a DOI-minting repository. No personal or restricted third-party data were used.

## Code availability

Source code for generation, search, evaluation, statistics, component audit and replay is included in the project repository. The release will identify the exact commit and archival DOI. Model weights are not redistributed; identifier, revision and runtime are reported above.

## References

1. Peirce, C. S. Deduction, induction, and hypothesis. *Popular Science Monthly* **13**, 470–482 (1878).
2. Harman, G. H. The inference to the best explanation. *Philos. Rev.* **74**, 88–95 (1965).
3. Lipton, P. *Inference to the Best Explanation* (Routledge, 2004).
4. Boden, M. A. *The Creative Mind: Myths and Mechanisms* (Routledge, 2004).
5. Wiggins, G. A. A preliminary framework for description, analysis and comparison of creative systems. *Knowl.-Based Syst.* **19**, 449–458 (2006).
6. Wiggins, G. A. Searching for computational creativity. *New Gener. Comput.* **24**, 209–222 (2006).
7. Muggleton, S. & Buntine, W. Machine invention of first-order predicates by inverting resolution. In *Proc. 5th Int. Conf. Machine Learning* 339–352 (1988).
8. Stahl, I. Predicate invention in inductive logic programming. *Mach. Learn.* **13**, 287–320 (1993).
9. Donoho, S. K. & Rendell, L. A. Rerepresenting and restructuring domain theories. *J. Artif. Intell. Res.* **2**, 411–446 (1995).
10. Schmidt, M. & Lipson, H. Distilling free-form natural laws from experimental data. *Science* **324**, 81–85 (2009).
11. Udrescu, S.-M. & Tegmark, M. AI Feynman. *Sci. Adv.* **6**, eaay2631 (2020).
12. Fawzi, A. et al. Discovering faster matrix multiplication algorithms with reinforcement learning. *Nature* **610**, 47–53 (2022).
13. Romera-Paredes, B. et al. Mathematical discoveries from program search with large language models. *Nature* **625**, 468–475 (2024).
14. Wang, Z. et al. Hypothesis Search: inductive reasoning with language models. In *ICLR* (2024).
15. Zhou, Y. et al. Hypothesis generation with large language models. In *NLP4Science* 117–139 (2024).
16. Huang, A. et al. POPPER: automated hypothesis validation with language models. In *ICML*, PMLR **267** (2025).
17. Lu, C. et al. The AI Scientist. Preprint at https://arxiv.org/abs/2408.06292 (2024).
18. Gottweis, J. et al. Accelerating scientific discovery with Co-Scientist. *Nature* (2026). https://doi.org/10.1038/s41586-026-10644-y
19. Ghareeb, A. E. et al. A multi-agent system for automating scientific discovery. *Nature* **655**, 497–505 (2026). https://doi.org/10.1038/s41586-026-10652-y
20. Boiko, D. A. et al. Autonomous chemical research with large language models. *Nature* **624**, 570–578 (2023).
21. Pu, Y., Lin, T. & Chen, H. Principle-Evolvable Scientific Discovery via Uncertainty Minimization. In *ICML*, PMLR **306** (2026).
22. Murphy, K. Model Discovery Agent: LLM-assisted Bayesian experiment design for data-efficient discovery of mechanistic world models. Preprint at https://arxiv.org/abs/2608.09696 (2026).
23. Zhong, T. et al. Before the Action: Benchmarking LLMs on Prospective Hypothesis Discovery. Preprint at https://arxiv.org/abs/2607.15766 (2026).
24. Zhao, Q. et al. Scientific Belief Revision Through Causal Model Evolution and Experimentation. Preprint at https://arxiv.org/abs/2609.01526 (2026).
25. Chen, T. et al. HypoSpace. Preprint at https://arxiv.org/abs/2510.15614 (2025).
26. Liu, Y. et al. ResearchBench. *Findings ACL* 13187–13207 (2026).
27. Pearl, J. *Causality* (Cambridge Univ. Press, 2009).
28. Peters, J., Janzing, D. & Schölkopf, B. *Elements of Causal Inference* (MIT Press, 2017).

## Acknowledgements

To be completed by the authors before submission.

## Author contributions

To be completed using the CRediT taxonomy before submission.

## Competing interests

To be completed by the authors before submission.

## Correspondence

To be completed by the corresponding author before submission.
