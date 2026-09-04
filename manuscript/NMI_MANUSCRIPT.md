# A prospective assay for hypothesis-space expansion in AI systems

## Abstract

Scientific discovery can require changing not only a hypothesis but the language in which hypotheses are expressed. We introduce a prospective, replayable assay for hypothesis-space expansion. Candidates must leave a frozen language, fit observations, commit to an intervention before outcome reveal, outperform the incumbent predictor and survive independent falsification. Typed proposals succeeded in 142/400 synthetic worlds. A deterministic search paired with a fixed motif-to-basis realizer succeeded in 400/400 known-family and 100/100 held-out worlds; code-path ablation reproduced every verdict without model output. Legacy self-composition interfaces failed almost entirely before execution. A grammar-constrained DeepSeek interface produced validated outcomes in 15/96 worlds, compared with 16/96 for random four-step composition on the same panel; its 21 validated candidates all triggered one scaffold realizer motif. The assay therefore measures bounded structural escape and exposes component attribution, but does not establish broad autonomous scientific-discovery competence.

## Introduction

Scientific change can alter the representational vocabulary in which hypotheses are stated<sup>1–3</sup>. Computational creativity and constructive induction distinguish exploration within a space from transformations of that space<sup>4–9</sup>. Symbolic regression, program search and language-model-guided systems discover equations, algorithms and hypotheses<sup>10–17</sup>, while multi-agent systems automate broader workflows<sup>18–20</sup>.

Recent work now explicitly targets expanding principle or model spaces. PiEvo treats discovery as optimization over an evolving principle space across four benchmarks<sup>21</sup>. Model Discovery Agent couples a language-model proposer to Bayesian experiment design in an open model setting spanning physics, chemistry and biology<sup>22</sup>. HypoArena evaluates prospective hypothesis discovery in 988 cases across six domains and 15 frontier models<sup>23</sup>. EvoSCM evolves structural causal models through intervention and prospective prediction<sup>24</sup>. These studies broaden the scientific tasks and models under evaluation. A complementary measurement problem remains: how can an evaluation prove that a candidate left a specified incumbent hypothesis language, charge it a prediction before seeing the answer, and separately identify which system component caused the escape?

Related diagnostic benchmarks study underdetermined hypothesis generation and inspiration-based task decomposition<sup>25,26</sup>. Our separation of observational fit from intervention and falsification follows the interventionist distinction between association and causal prediction<sup>27,28</sup>.

Here we operationalize **bounded hypothesis-space expansion**. We freeze an incumbent representational language, generate executable candidates and require a six-gate verdict: incumbent adequacy (J0), canonical structural non-membership (J1), candidate adequacy (J2), a discriminating committed prediction (J3), prospective intervention gain (J4) and independent falsification survival (J5; Fig. 1). Candidate prose, model confidence, embedding distance and semantic novelty do not enter the verdict.

Our experiments validate the assay and reveal a component-attribution limit. Typed proposals and generic compositional search cross the frozen language reliably, whereas fixed-space alternatives do not. However, code-path ablation shows that C3's representations, fitted equations, ranking and interventions were deterministic; removing model output leaves all 500 jump and 300 control verdicts unchanged. The audit demonstrates how a system-level discovery benchmark can misattribute successful scientific content to a model when deterministic scaffolding supplies the decisive representation, fit and intervention. The contribution is therefore the prospective assay, the typed search result and a method for auditing causal system attribution—not evidence that a language model produced the successful escapes.

### Table 1 | Position relative to adjacent discovery evaluations

| Evaluation | Executable hypotheses | Frozen formal language | Canonical out-of-space test | Prospective intervention | Independent falsification | Proposal/reasoning separation | Deterministic replay | Breadth |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| Hypothesis Search<sup>14</sup> | partial | not reported | not reported | not reported | held-out tasks | language hypothesis / program | not reported | ARC-style induction |
| HypoGeniC<sup>15</sup> | text hypotheses | not reported | not reported | not reported | held-out examples | generation / ranking | not reported | hypothesis generation |
| POPPER<sup>16</sup> | partial | not reported | not reported | sequential tests | agentic falsification | hypothesis / validator | not reported | six data domains |
| FunSearch<sup>13</sup> | yes | fixed program skeleton | not reported | evaluator feedback | held-out tests | proposer / evaluator | partial | mathematics |
| PiEvo<sup>21</sup> | yes | evolving principle space | not reported | task dependent | task dependent | proposer / search | not reported | four benchmarks, multiple backbones |
| Model Discovery Agent<sup>22</sup> | yes | open model set | not reported | Bayesian design | posterior checks | proposer / inference | not reported | includes physics, chemistry and biology |
| HypoArena<sup>23</sup> | judged text | not reported | not reported | context regression | rubric / judge | not reported | not reported | 988 cases, six domains, 15 models |
| EvoSCM<sup>24</sup> | yes | evolving causal models | not reported | active intervention | prospective prediction | evolution / selection | not reported | simulated physical worlds |
| This work | yes | yes | canonical certificate | outcome locked | independent exact cases | factorial + component audit | exact | 9 synthetic families; 2-checkpoint sensitivity |

## Results

### A prospective criterion for hypothesis-space expansion

Each synthetic world contains observations compatible with an incumbent model, a frozen typed-graph language, hidden intervention outcomes and independent falsification cases. The best incumbent predictor is computed exactly or by bounded exhaustive search. Before any intervention outcome is revealed, a candidate representation, executable expression, selected action, prediction and split hash are committed. A validated jump is the conjunction J0∧J1∧J2∧J3∧J4∧J5 (Fig. 1). This design turns “leaving a hypothesis space” into a replayable event rather than a judgement about wording or apparent novelty.

### Typed proposals outperform fixed-space alternatives

In AJ5, direct (B0) and sampling-matched (B1) model proposals each succeeded in 1/400 worlds; fixed-space reasoning (B2), attribute-only mutation (B3) and value-only mutation succeeded in none. External typed proposals (B4 and B5) each succeeded in 142/400 (35.5%; Fig. 2a). All eight registered contrasts with B0–B3 were positive after Holm correction (adjusted P=8.00×10−4, the 10,000-replicate resolution floor after correction).

Holding the downstream path fixed, model-proposed representations (P0) succeeded in 0/400 worlds, external typed proposals (P1) in 142/400 and oracle representations (P2) in 400/400 (Fig. 2b). The system can execute a supplied changed representation, but this does not establish model necessity after deterministic fitting because the second call received a fitted expression and maximum-separation intervention that were programmatically enforced.

Gate attrition clarifies the result (Fig. 2d). From 1,200 jump-world candidates each, B4 retained 823 at J1, 573 at J2, 270 at J3 and 154 at J4–J5; B5 retained 838, 562, 262 and 145. B0 retained 65, 22, 4 and 1, while B1 retained 546, 375, 118 and 1, showing that these executable model proposals usually failed after rather than before structural evaluation. Controls still produced 112 and 110 B4/B5 candidates through J3, but none passed J4: prospective outcomes, not J0–J3 alone, eliminated these apparent escapes.

### Generic rewrites and fixed motif realization produce validated representations

CJ5 replaced nine high-level mutations with 29 local graph and syntax-tree rewrites. Node addition, type, observability, arity and argument binding were separate steps; no primitive accepted a family label, target distance or outcome. C3 traversed 48 four-step branches, ranked candidates without outcomes and retained three. A deterministic realizer then mapped nine graph motifs to fixed basis libraries before solving their coefficients from public observations. Those hand-authored bases aligned with the procedural family mechanisms, including the held-out triadic-product basis; C3 therefore tests search over motif triggers, not invention of an unseen functional form.

Across eight known families (n=400 worlds), fixed-space search (C0) and depth-one alternatives (C2) succeeded in none. The atomic reference (C1) succeeded in 131 (32.75%), random four-step paths (C_rand) in 52 (13.0%) and C3 in all 400 (Fig. 3). C3 exceeded C_rand by 0.87 (95% CI 0.845–0.895; adjusted P=3.00×10−4). Its family-wise saturation demonstrates within-generator reliability and assay separability, not eight independent replications or a frontier benchmark.

### Code-path ablation attributes C3 success to deterministic scaffolding

Inspection of the frozen C3 path showed that representation, expression, ranking and intervention selection occurred deterministically before the model response. Response fields for representation, expression and intervention were overwritten; only an explanation remained, and explanations do not enter J0–J5. We therefore replaced both model calls with a valid empty explanation and recomputed every theory, commitment and verdict without inference.

All 2,400 candidate verdicts matched the archive. The replay retained the pooled 400 known-family and 100 held-out jump-world successes and the structurally guaranteed 0/300 control false jumps (Fig. 4). Phi-4 output was therefore not semantically necessary for C3. The perfect result belongs to the typed deterministic search, motif realizer and evaluation scaffold. More generally, the audit shows why scientific-discovery evaluations need code-path attribution: system success alone does not identify which component supplied the scientific content.

### Legacy sensitivities expose proposal-interface attrition

C_self scored 0/400, but offline reconstruction showed that this cannot isolate proposal quality. All 1,200 responses were non-empty and JSON-extractable, yet none contained a valid outer `plans` list; 0/19,200 registered opportunities reached execution or J1. Every response reached the 700-token cap, and none was strict whole-response JSON. The historical failure therefore conflates representation proposal with truncation and serialization.

Direct contract inspection revealed an additional confound. The prompt enumerated operators but omitted their exact argument keys: for example, the executor expects `node`, `other` and `kind`, whereas all 288 matched DeepSeek proposal calls used at least one of `source`, `target` or `type`. None was strict whole-response JSON. The permissive legacy extractor could also recover an inner object from truncated outer JSON, so “JSON extractable” did not imply a valid top-level plan. The registered interface was therefore unsuitable for isolating conceptual proposal quality.

We used a fixed, outcome-blind panel of 96 historical worlds (12 per family) to test precision, budget and model-interface alternatives without replacing the original n=400 confirmation (Fig. 4). Every legacy-interface autonomous condition remained at 0/96 (Wilson 95% interval 0–3.8%). All five paired JSR differences were 0.000: longer-budget and 8-bit Phi-4 versus the historical slice, matched DeepSeek versus that slice, native versus matched DeepSeek, and validator-only repair versus unrepaired 8-bit Phi-4. These are targeted sensitivities, not candidate-level tests or a new confirmatory population.

Attrition remained predominantly pre-executable. On the panel, longer-budget Phi-4 produced 993/4,608 schema-valid opportunities but none executable; Phi-4 8-bit and its one-repair condition produced no schema-valid plans. Matched DeepSeek also produced none: 4,480 opportunities had a non-list `plans` field and 128 lacked `plans`. In the full longer-budget populations, only 9/19,200 known-family opportunities and 0/4,800 held-out opportunities were executable, with no successful world. Precision, budget, repair and checkpoint substitution therefore did not recover an autonomous jump under this interface.

Native DeepSeek also scored 0/96, but for a different interface reason: all 576 calls returned reasoning text, no separate answer reached the parser and 518 hit the 4,096-token cap. This does not isolate conceptual proposal quality from reasoning-to-answer serialization. In the supplied-representation control, 4/120 model-authored candidates were parse-valid and executable and 3 passed J1–J5, yielding 3/40 successful worlds (7.5%; Wilson 95% interval 2.6–19.9%); 116 calls hit the cap. The checkpoint can therefore use a supplied correct representation occasionally, but downstream reliability remains poor. These runs do not establish model-independent conceptual incapacity.

### A grammar-constrained interface with explicit argument syntax yields family-concentrated escapes

We next froze a single grammar-constrained DeepSeek sensitivity on the same 96 worlds (Fig. 4c,d). Separate deliberation and answer budgets plus a strict plan schema guaranteed grammar and parser-level argument syntax but supplied no truth, fit, intervention outcome, gate value or semantic repair. All 4,608 plan opportunities were strict whole-response JSON and schema-valid; 3,939 (85.5%) were dynamically executable. At least one plan was executable in 280/288 candidate slots. Among those selected candidates, 236/280 passed J1–J2, 21/280 passed J3 and the same 21 passed J4–J5. These model-proposed edit plans were subsequently realized, ranked and assigned interventions by the deterministic scaffold. They yielded 21 validated candidates and 15/96 successful worlds (15.6%; Wilson 95% interval 9.7–24.2%). Relative to each legacy zero-rate interface, 15 worlds changed from failure to success and none changed in the opposite direction.

Success was concentrated in two families: meta-law succeeded in 9/12 worlds and unification in 6/12; the other six families each scored 0/12. All 21 validated candidates triggered the same `multi_argument_function` realizer, which is available only when the public graph exposes a `context_zero` role. On the identical panel, outcome-blind random four-step paths succeeded in 16/96 worlds: 66 worlds failed under both conditions, 15 succeeded only under random search, 14 only under the grammar-constrained interface and one under both. The model condition therefore did not exceed random composition in aggregate and instead showed a different, family-specific motif preference. All 288 deliberation calls reached the 4,096-token cap, whereas all 288 serialization calls stopped before their separate cap. The result demonstrates that the legacy interfaces hid executable model-generated topology, not that the model independently supplied the realized law or outperformed random primitive search.

### Transfer to one held-out structural family

The second study reserved `triadic_relation_reification` from development, pilot inference and known-family confirmation. C3 succeeded in 100/100 held-out worlds, C_rand in 13/100, and C0, C1, C2 and C_self in none (difference from C_rand 0.87, 95% CI 0.80–0.93; adjusted P=3.00×10−4).

The holdout is limited: an earlier family used binary property-to-relation change, the generic language already included reification and the shared realizer already contained the triadic-product basis. The arity-three target structure, generator and instances were new, but the realization mechanism was not. This is therefore a search-side structural-family holdout; one adjacent family cannot support broad external generalization.

### A worked prospective escape

In one held-out world, observations with x=z=w gave y=9x³, so the incumbent `y=9x³` and candidate `y=9xzw` both fit exactly. Four generic edits reified the incumbent prediction edge, changed the new relation to arity three, and bound z and w; the pre-specified realizer supplied the `xzw` basis and fitted its coefficient (Fig. 5). Before outcome reveal, the assay committed to setting z from 6 to 7 at x=w=6. The incumbent predicted 1,944; the candidate predicted 2,268; the revealed outcome was 2,268. Independent falsification at z=5 yielded 1,620, again exact for the candidate. The representation failed the frozen language on relation count, type, arity bindings and result structure, and passed J0–J5.

### Specificity and replay

The zero false-jump count requires qualification. In C3 controls, 800 of 900 candidates passed J1, 567 passed J2 and 283 passed J3, but none passed J4. The null was therefore non-trivial through the prospective commitment gate. Nevertheless, because no-jump truth is generated inside the incumbent language and the incumbent oracle is exact, an outside candidate cannot strictly beat it under noiseless evaluation. The observed 0/300 is best interpreted as a structural-specificity check under the exact simulator, not an empirical false-positive estimate for noisy science; the Wilson upper bound is descriptive only.

All 10,800 AJ5 and 16,800 CJ5 selected candidates replayed exactly, including 35,533 CJ5 ancestry records. No confirmatory world was excluded and no shard was rerun.

## Discussion

This work contributes an assay for a specific event: an executable candidate leaves a frozen hypothesis language and pays for that move with a prospective prediction that beats the best incumbent and survives independent falsification. Canonical non-membership, outcome-before-commitment ordering and exact replay distinguish this event from judged novelty or retrospective fit (Table 1).

The code-path audit is itself a methodological result. It demonstrates that a system-level discovery benchmark can assign successful scientific content to a language model even when deterministic scaffolding supplies the decisive representation, basis, fit, ranking and intervention. Conversely, legacy C_self zero rates were dominated by pre-executable attrition, whereas executable AJ5 model proposals usually failed at later gates. A grammar-constrained interface restored executability and exposed model-generated graph topology, but the deterministic scaffold still supplied realization and evaluation, all successes used one motif and aggregate performance did not exceed random composition. End-to-end failure can therefore underestimate what reaches the evaluator, just as end-to-end success can overattribute scientific content to a model. Claims of model-driven representation change require field-level provenance throughout the committed theory.

External validity is the principal limitation. The worlds are synthetic and noiseless; C3 is saturated; search strata, generators and motif-to-basis realizer were co-designed; and the operator language embeds graph, function, relation and binding priors. The original confirmation used one model; the extension sampled only one additional checkpoint on a fixed subset, and its native condition was not compute-matched. Only one conceptually adjacent, search-side family was held out. World seeds quantify within-generator reliability. The higher-level generalization units are nine structural families, only one of which was held out, so small world-level P values do not substitute for structural breadth.

A decisive extension should freeze the current assay and add independently authored families, distractor primitives, deeper compositions, stochastic observations, partial observability and at least one recognizable mechanistic simulation. Broader open and proprietary model comparisons could then use the tested separation of reasoning and grammar-valid answer stages, while reporting dynamic executability and J1–J5 rather than treating format compliance as scientific success. These experiments are proposed, not part of the present evidence.

The conclusion is narrow but durable: hypothesis-space expansion can be measured prospectively and replayed exactly; typed deterministic search can produce it in controlled worlds; and causal component auditing can reveal when apparent capability or incapacity instead belongs to the scaffold or interface.

## Methods

### Study design and protocol freezing

AJ5 and CJ5 protocols were frozen in Git before their reported confirmatory model calls. AJ5 uses commit `895ebb9118ffd0046825b88868621f2a70f69f61`. CJ5 uses `65f20874e16bddf8a7ae36996395ff52b27153b7`, with a documented correction at `7ecb977` and held-out unlock at `27ee542`. The commits are publicly retrievable but unsigned, and no independent registry or transparency-log timestamp was located. We therefore describe the studies as prospectively specified and commit-frozen, not formally preregistered. Pilot seeds were excluded; no confirmatory result changed families, operators, thresholds, budgets or seeds.

### Model and inference

Both studies used frozen `microsoft/phi-4` revision `2db69c1c3e91a05d2c64a3185acfbaf36f744e25`, vLLM 0.10.2, dynamic bitsandbytes 4-bit quantization, a 4,096-token context, temperature 0.2, top-p 0.95 and completion cap 700. AJ5 sampling proposals used temperature 0.7. Each request had a deterministic seed. No fine-tuning or cross-world adaptation occurred.

### Minimal targeted sensitivity extension

The original Phi-4 artifacts were preserved at commit `ae1ede683fdef09f2bf60f6e1052b60394ad6cf8`, tag `nmi-phi4-frozen-2026-09` and archive branch `nmi-phi4-frozen-archive-2026-09`. A separate extension protocol, panel, model configurations and generation code were frozen at commit `320eb29b33ddaed596b0fe7b3f1d5895c706f311` and amended only for operational execution at `f846c89287e379fe313551c47765c24f2abf4959`. New outputs used the `nmi_minimal_sensitivity_v1` namespace and could not overwrite historical files.

An outcome-blind SHA-256 ranking selected 12 of the 50 historical CJ5 seeds before any new model call: 30014, 30012, 30029, 30025, 30011, 30023, 30000, 30032, 30001, 30037, 30002 and 30015. Applying the same seeds to all eight known families produced a fixed 96-world paired panel. The positive control used the first five selected seeds in each family (n=40). This extension is a targeted sensitivity analysis, not a replacement confirmatory population.

The frozen run matrix contained Phi-4 8-bit C_self on 96 worlds; DeepSeek matched C_self with `reasoning_effort=none` on the same worlds; DeepSeek native C_self with `reasoning_effort=max`; and a supplied-correct-representation DeepSeek positive control. The DeepSeek service identified the checkpoint as `deepseek-ai/DeepSeek-V4-Flash-Vision-Exp`, revision `86f746b36186f0e567729a5c06a8c918caba82a9`, served as `deepseek-v4-flash-vision-exp` by a patched vLLM `0.25.2.dev0+g752a3a504.d20260714` runtime with FP8 weights, an NVFP4 key-value cache and a 1,048,576-token context limit. Phi-4 8-bit runs used Transformers 4.56.1 and bitsandbytes 0.47.0. We do not equate this checkpoint with any other DeepSeek release. The matched condition retained the historical 700-token output cap; the native and positive-control conditions froze a 4,096-token output cap. Reasoning text was returned separately in `message.reasoning`; a separate reasoning-token count was recorded only if exposed by the service.

A separately prospectively frozen `PHI-BUDGET-SENSITIVITY` condition retained the historical Phi-4 revision, 4-bit runtime, prompt semantics, primitive vocabulary, worlds, three candidate slots, 16 plans per slot, J0–J5 gates, interventions and hidden-information boundaries. Its only scientific change was increasing the predeclared completion cap from 700 to 2,048 tokens; it did not add representation attempts, candidates or interventions and is not compute-matched to the historical condition. The source protocol was frozen at commit `4606413` and tag `nmi-extension-v1-protocol-freeze`. Complete known-family (n=400) and held-out (n=100) shards were incorporated after shard completion and before analysis tables were generated through amendment `NMI-MIN-SENS-V1-AMENDMENT-002`. The fixed 96-world panel provides the primary paired budget comparison, while the complete populations are reported descriptively.

The superseded broad protocol stopped after eight of 38 planned shards reached `complete_verified`. Besides the two Phi-budget shards, six completed descriptive shards tested matched DeepSeek, Phi-4 strict-schema decoding and Phi-4 one-repair on 400 known-family and 100 held-out worlds each; all six produced zero successful worlds. Strict-schema Phi-4 yielded 28/19,200 executable known-family plans and 1/4,800 held-out plans, while the other completed shards yielded none. Three incomplete runs were retained but excluded: native DeepSeek known-family (404 call records), Phi-budget control (1,043) and an infrastructure-terminated Phi-budget attempt (202/2,400). Reporting these superseded runs prevents selective omission; they are not treated as a completed factorial or replacement confirmation.

Worlds, primitive vocabulary, three candidate slots, 16 four-step plans per slot, representation opportunities, J0–J5, prospective interventions and hidden-information boundaries were unchanged. The matched condition received no additional semantic information. The positive control fixed only the correct representation; the model still authored the executable expression, explanation and intervention selection, so success could not be created by overwriting those fields. Because the offline historical cascade had 100% pre-executable attrition, exceeding the frozen 25% trigger, one additional Phi-4 8-bit condition permitted exactly one replacement repair response per structurally invalid slot. Validator feedback named only syntax, schema, operation, reference, type or arity errors and exposed no truth, target distance, outcome or gate value.

### Grammar-constrained interface sensitivity

After auditing the frozen responses, we specified one additional DeepSeek condition on the identical 96-world panel. Each of three slots retained 16 independent four-step plans and therefore 48 representation opportunities per world. The first call reserved 4,096 tokens for native reasoning; a second call received that model-produced deliberation and a complete parser-level operation syntax, used `reasoning_effort=none`, and reserved 4,096 tokens for a compact grammar-constrained plan object. These two calls replaced the original proposal-plus-explanation allocation, preserving six calls per world. The schema guaranteed only JSON structure, plan count, depth, operator names and argument keys/types. The fair condition exposed 28 non-crossover primitives because no donor graph was supplied; the original CJ5 vocabulary contained 29 including crossover.

The serializer received no fitted expression, truth, target distance, intervention outcome, gate value or semantic repair. Worlds, primitive vocabulary, candidate slots, opportunities, deterministic downstream fitter and intervention selector, hidden-information boundaries and J0–J5 were unchanged. The model supplied graph-edit topology; the scaffold supplied motif realization, fit, selection among the 16 plans and the committed maximum-separation intervention. The protocol and code were frozen at commit `b6e1561` and tag `nmi-fair-interface-v1-protocol-freeze`. A subsequent operational amendment partitioned families into four disjoint shards without changing calls or scientific settings. A post-freeze 31-call throughput pilot used eight formal-panel worlds and returned 15 non-empty responses, but produced no candidate, world or summary table; it was archived and excluded before formal shards began, and the unchanged worlds were rerun. Concurrent shard launch then exposed a four-sequence server limit: three timeout-only shard directories contained no returned response or result table. We archived and excluded them, froze a second operational amendment at commit `6bab5fb` and tag `nmi-fair-interface-v1-sequential-shards`, and scheduled the unchanged shards sequentially.

### Worlds, representations and search

Generators returned public observations, candidate intervention actions without outcomes, a frozen incumbent `LanguageSpec`, hidden truth and independent intervention and falsification cases. AJ5 used eight families and 50 jump seeds per family; CJ5 used 50 new seeds per family. No-jump controls used 25 seeds per family in each phase. CJ5 added 100 held-out jump and 100 control seeds. Representations were canonical typed graphs with executable fitted programs.

AJ5 tested direct model output, model sampling, fixed-space reasoning, attribute-only mutation and two typed high-level proposal conditions. CJ5 used 29 generic local rewrites. C3 traversed 48 four-operation branches and retained three candidates by a deterministic score. The shared realizer matched candidate graphs against nine hand-authored motifs, assigned fixed basis functions aligned with the procedural mechanisms and solved only their coefficients from public observations. The held-out triadic-product basis was present before unlock. C_rand sampled 48 four-step paths. C_self requested 16 plans in each of three slots; invalid plans were not repaired.

### Prospective evaluation

J0 required incumbent observation MSE≤10−12; J1 required DSL validity and frozen-language non-membership; J2 required candidate observation MSE≤10−12; J3 required candidate–oracle prediction separation≥0.5 on the committed action; J4 required intervention MSE improvement>0.1; J5 required falsification MSE≤10−12 and improvement>0.1. Candidate, prediction, action and split hashes were committed before simulator evaluation.

### Statistics and component audit

The world was the replicate. AJ5 used 10,000 family-stratified paired bootstrap replicates; CJ5 used the same bootstrap for effects and paired sign-flip tests. Holm correction was applied within prospectively specified comparison families at α=0.05. Candidate rows were used only for attrition. Family-level distributions are reported descriptively because eight known families plus one held-out family do not support a stable population-level family inference.

The post-hoc component audit reconstructed all C3 candidates from archived deterministic representations, fitted expressions and selected interventions, replacing the model-derived explanation with an empty string. It then regenerated each world, froze a new commitment and recomputed J0–J5. No model inference was run.

For the targeted sensitivity analysis, exact world counts, JSR and Wilson 95% intervals are primary. Comparisons use paired world transitions and paired JSR differences on the identical 96-world panel; family rates are descriptive. The full n=400 known-family and n=100 held-out Phi-4 budget populations are supplementary descriptive sensitivities, and the n=40 positive control is shown separately. No candidate-level significance tests are performed and P values are not used as primary evidence. Response and plan attrition are reported with their denominators, followed by executable-candidate J1–J5 attrition.

### Integrity and replay

Requests, representations, ancestry edges, fitted programs, commitments, gate values and configuration hashes were retained. Replay reconstructed representations and recomputed J0–J5. Three grammar-constrained-interface shard launches were interrupted after queue starvation produced transport timeouts but before any response or scientific result was returned; their logs were archived outside the formal namespace under a frozen operational amendment, and the unchanged shards were restarted sequentially. No completed shard was rerun and there were no outcome-quality exclusions.

### AI assistance in research and writing

Phi-4 generated the original registered outputs described above. OpenAI Codex was used after the original confirmatory experiments to inspect artifacts, implement and orchestrate the separately frozen targeted sensitivity extension, recompute inference-free audits, verify literature metadata and assist drafting. It did not choose hypotheses using observed outcomes, alter historical source data or change the frozen evaluation rules. Human authors verified the cited metadata and remain responsible for originality, accuracy and integrity.

## Data availability

Synthetic-world definitions, historical and extension result tables, manifests and replay artifacts are included in the project repository. Historical AJ5/CJ5 raw call ledgers and raw superseded-extension shards remain local, hash-addressed research artifacts and are not tracked in the current Git repository; they must be included in the anonymized reviewer deposit and DOI archive before submission. The original confirmatory state and separate sensitivity namespace are identified by commits and tags. No personal or restricted third-party data were used.

## Code availability

Source code for generation, search, evaluation, offline attrition, statistics, figure generation, component audit and replay is included in the project repository. The release will identify the exact commit and archival DOI. Model weights are not redistributed; repository identifier, revision and runtime are reported above.

## References

1. Peirce, C. S. Deduction, induction, and hypothesis. *Popular Science Monthly* **13**, 470–482 (1878).
2. Harman, G. H. The inference to the best explanation. *Philos. Rev.* **74**, 88–95 (1965).
3. Lipton, P. *Inference to the Best Explanation* (Routledge, 2004).
4. Boden, M. A. *The Creative Mind: Myths and Mechanisms* (Routledge, 2004).
5. Wiggins, G. A. A preliminary framework for description, analysis and comparison of creative systems. *Knowl.-Based Syst.* **19**, 449–458 (2006).
6. Wiggins, G. A. Searching for computational creativity. *New Gener. Comput.* **24**, 209–222 (2006).
7. Muggleton, S. & Buntine, W. Machine invention of first-order predicates by inverting resolution. In *Proc. 5th Int. Conf. Machine Learning* 339–352 (1988).
8. Stahl, I. The appropriateness of predicate invention as a bias shift operation in inductive logic programming. *Mach. Learn.* **20**, 95–117 (1995).
9. Donoho, S. K. & Rendell, L. A. Rerepresenting and restructuring domain theories. *J. Artif. Intell. Res.* **2**, 411–446 (1995).
10. Schmidt, M. & Lipson, H. Distilling free-form natural laws from experimental data. *Science* **324**, 81–85 (2009).
11. Udrescu, S.-M. & Tegmark, M. AI Feynman. *Sci. Adv.* **6**, eaay2631 (2020).
12. Fawzi, A. et al. Discovering faster matrix multiplication algorithms with reinforcement learning. *Nature* **610**, 47–53 (2022).
13. Romera-Paredes, B. et al. Mathematical discoveries from program search with large language models. *Nature* **625**, 468–475 (2024).
14. Wang, R. et al. Hypothesis Search: inductive reasoning with language models. In *ICLR* (2024).
15. Zhou, Y. et al. Hypothesis generation with large language models. In *Proc. 1st Workshop on NLP for Science* 117–139 (Association for Computational Linguistics, 2024).
16. Huang, K. et al. Automated hypothesis validation with agentic sequential falsifications. In *Proc. 42nd International Conference on Machine Learning*, PMLR **267**, 25372–25437 (2025).
17. Lu, C. et al. The AI Scientist. Preprint at https://arxiv.org/abs/2408.06292 (2024).
18. Gottweis, J. et al. Accelerating scientific discovery with Co-Scientist. *Nature* **655**, 487–496 (2026). https://doi.org/10.1038/s41586-026-10644-y
19. Ghareeb, A. E. et al. A multi-agent system for automating scientific discovery. *Nature* **655**, 497–505 (2026). https://doi.org/10.1038/s41586-026-10652-y
20. Boiko, D. A. et al. Autonomous chemical research with large language models. *Nature* **624**, 570–578 (2023).
21. Pu, Y., Lin, T. & Chen, H. Principle-Evolvable Scientific Discovery via Uncertainty Minimization. In *ICML*, PMLR **306** (2026).
22. Murphy, K. Model Discovery Agent: LLM-assisted Bayesian experiment design for data-efficient discovery of mechanistic world models. Preprint at https://arxiv.org/abs/2608.09696 (2026).
23. Zhong, T. et al. Before the Action: Benchmarking LLMs on Prospective Hypothesis Discovery. Preprint at https://arxiv.org/abs/2607.15766 (2026).
24. Zhao, Q. et al. EvoSCM: scientific belief revision through causal model evolution and experimentation. Preprint at https://arxiv.org/abs/2609.01526 (2026).
25. Chen, T. et al. HypoSpace: a diagnostic benchmark for set-valued hypothesis generation under underdetermination and sublinear coverage bounds. Preprint at https://arxiv.org/abs/2510.15614 (2025).
26. Liu, Y. et al. ResearchBench: benchmarking LLMs in scientific discovery via inspiration-based task decomposition. In *Findings of ACL* (2026).
27. Pearl, J. *Causality* 2nd edn (Cambridge Univ. Press, 2009).
28. Peters, J., Janzing, D. & Schölkopf, B. *Elements of Causal Inference* (MIT Press, 2017).

## Acknowledgements

To be completed by the authors before submission.

## Author contributions

To be completed using the CRediT taxonomy before submission.

## Competing interests

To be completed by the authors before submission.

## Correspondence

To be completed by the corresponding author before submission.
