# A prospective assay reveals scaffold-driven hypothesis-space expansion

**Jing-Rung Huang**<sup>1,*</sup> and **Wen-Hsiang Lu**<sup>1</sup>

<sup>1</sup> Department of Computer Science and Information Engineering, National Cheng Kung University, Tainan 701, Taiwan

<sup>*</sup> Corresponding author: Jing-Rung Huang (p78084063@mail.ncku.edu.tw)

ORCID: Jing-Rung Huang, 0000-0003-4776-3550; Wen-Hsiang Lu, 0009-0002-5149-6790

## Abstract

Scientific discovery can require changing not only a hypothesis but the language in which hypotheses are expressed. We introduce a prospective, replayable assay for bounded hypothesis-space expansion: candidates must leave a frozen language, fit observations, commit to an intervention before outcome reveal, outperform the observation-optimal incumbent comparator and survive held-out falsification. Externally typed proposals succeeded in 142 of 400 synthetic worlds. Deterministic compositional search paired with a frozen, family-aligned motif-to-basis realizer succeeded in all 400 known-family worlds and 100 worlds from one search-side holdout. Model-free replay reproduced every verdict because deterministic components supplied the evaluated representations, fitted expressions and interventions. A grammar-constrained model proposer produced validated edits in 15 of 96 worlds but did not outperform random composition. The assay therefore measures system-level representational escape while showing that causal attribution requires field-level provenance across model and scaffold components.

<!-- INTRODUCTION -->

Scientific change can alter the representational vocabulary in which hypotheses are stated<sup>1,2,3</sup>. Computational creativity and constructive induction distinguish exploration within a space from transformations of that space<sup>4,5,6,7,8,9</sup>. Symbolic regression, program search and language-model-guided systems discover equations, algorithms and hypotheses<sup>10,11,12,13,14,15,16,17</sup>, while multi-agent systems automate broader workflows<sup>18,19,20</sup>.

Studies of language-model creativity reach mixed conclusions: some systems exceed population-average scores on divergent-thinking tasks, yet stronger human responses remain competitive, and judged creative outputs do not establish scientific representational change<sup>21</sup>. A recent position paper describes the generation of new explanatory premises as an abductive “jump” that current language models may lack<sup>22</sup>. Neither divergent-thinking scores nor that historical argument establishes whether a system left a specified hypothesis language, survived a prospective intervention, or which model–scaffold component supplied the move.

Recent work now explicitly targets expanding principle or model spaces. PiEvo treats discovery as optimization over an evolving principle space across four benchmarks<sup>23</sup>. Model Discovery Agent couples a language-model proposer to Bayesian experiment design in an open model setting spanning physics, chemistry and biology<sup>24</sup>. HypoArena evaluates prospective hypothesis discovery in 988 cases across six domains and 15 frontier models<sup>25</sup>. EvoSCM evolves structural causal models through intervention and prospective prediction<sup>26</sup>. Our contribution is not the first system to expand a principle or model space. It is an assay that requires canonical non-membership relative to a frozen incumbent language, commitment-before-outcome-reveal prediction, exact replay and component-level attribution of the resulting theory.

Related diagnostic benchmarks study underdetermined hypothesis generation and inspiration-based task decomposition<sup>27,28</sup>. A reconstructed molecular-genetics task found mainly incremental assistance from generative AI, but its historical case study does not establish a general incapacity<sup>29</sup>. Our separation of observational fit from intervention and falsification follows the interventionist distinction between association and causal prediction<sup>30,31</sup>.

Here we operationalize **bounded hypothesis-space expansion**. We freeze an incumbent representational language, generate executable candidates and require a six-gate verdict: incumbent adequacy (J0), canonical structural non-membership (J1), candidate adequacy (J2), a discriminating committed prediction (J3), prospective intervention gain (J4) and survival on separate held-out falsification cases (J5; Fig. 1). Here, escape denotes structural non-membership in a frozen representation language together with prospective improvement over a selected observational comparator; it does not establish functional inexpressibility within the entire incumbent language. Candidate prose, model confidence, embedding distance and semantic novelty do not enter the verdict.

Our experiments validate the assay and reveal a component-attribution limit. External typed proposals and generic compositional search cross the frozen language reliably, whereas fixed-space alternatives do not. However, code-path ablation shows that the successful search condition's representations, fitted equations, ranking and interventions were deterministic; removing model output leaves all 500 jump and 300 control verdicts unchanged. The audit demonstrates how a system-level discovery benchmark can misattribute successful explanatory content to a model when deterministic scaffolding supplies the decisive representation, fit and intervention. The contribution is therefore the prospective assay, the typed search result and a method for auditing causal system attribution—not evidence that a language model produced the successful escapes.

## Results

### A prospective criterion for hypothesis-space expansion

Each synthetic world contains observations compatible with an incumbent model, a frozen typed-graph language, hidden intervention outcomes and separate held-out falsification cases. The comparator minimizes observation loss over the frozen finite incumbent program set, with canonical-JSON tie-breaking; it is not optimized on intervention outcomes. Before any intervention outcome is revealed, a candidate representation, executable expression, selected action, prediction and split hash are committed. A validated jump is the conjunction J0∧J1∧J2∧J3∧J4∧J5 (Fig. 1). This design turns “leaving a hypothesis space” into a replayable event rather than a judgement about wording or apparent novelty.

### Typed proposals and fixed-language structural controls

In AJ5, direct (B0) and sampling-matched (B1) model proposals each succeeded in 1/400 worlds; fixed-space reasoning (B2), attribute-only mutation (B3) and value-only mutation succeeded in none. External typed proposals (B4 and B5) each succeeded in 142/400 (35.5%; Fig. 2a). All eight prospectively specified contrasts with B0–B3 had positive paired differences. The archived bootstrap tail quantities are retained in the source data but are not treated as null-calibrated P values (Supplementary S10).

Holding the downstream path fixed, the proposal-source comparison found 0/400 successes from model-proposed representations, 142/400 from external typed proposals and 400/400 from oracle representations (Fig. 2b). The system can execute a supplied changed representation, but this does not establish model necessity after deterministic fitting because the second call received a fitted expression and maximum-separation intervention that were programmatically enforced.

Gate attrition clarifies the result (Fig. 2d). From 1,200 jump-world candidates each, B4 retained 823 at J1, 573 at J2, 270 at J3 and 154 at J4–J5; B5 retained 838, 562, 262 and 145. B0 retained 65, 22, 4 and 1, while B1 retained 546, 375, 118 and 1, showing that these executable model proposals usually failed after rather than before structural evaluation. Controls still produced 112 and 110 B4/B5 candidates through J3, but none passed J4: prospective outcomes, not J0–J3 alone, eliminated these apparent escapes.

Fixed-language conditions serve as structural negative controls: because they cannot satisfy J1 by design, their zero jump rates do not estimate a general limitation of search or reasoning.

### Generic rewrites and fixed motif realization produce validated representations

CJ5 replaced nine high-level mutations with 29 local graph and syntax-tree rewrites. Node addition, type, observability, arity and argument binding were separate steps; no primitive accepted a family label, target distance or outcome. C3 traversed 48 four-step branches. At each edit, a deterministic realizer mapped graph motifs to nine fixed basis libraries and fitted coefficients from public observations. The resulting fits and public-action prediction separations entered the outcome-blind scores; diversity-aware final ranking then retained three terminal candidates before commitment and outcome reveal. Those hand-authored bases aligned with the procedural family mechanisms, including the held-out triadic-product basis; C3 therefore tests search over motif triggers, not invention of an unseen functional form.

Across eight known families (n=400 worlds), fixed-space search (C0) and depth-one alternatives (C2) succeeded in none. The atomic reference (C1) succeeded in 131 (32.75%), random four-step paths (C_rand) in 52 (13.0%) and C3 in all 400 (Fig. 3). C3 exceeded C_rand by 0.87 (95% CI 0.845–0.895; adjusted P=3.00×10−4). Its family-wise saturation demonstrates within-generator reliability and assay separability, not eight independent replications or a frontier benchmark.

The C3–C_rand contrast compares complete search-and-selection policies: C3 ranks using observational compatibility and prospective discrimination, whereas C_rand selects by seed-fixed structural hash. It does not isolate proposal generation from candidate ranking.

### Code-path ablation attributes C3 success to deterministic scaffolding

Inspection of the frozen C3 path showed that representation, expression, ranking and intervention selection occurred deterministically before the model response. Response fields for representation, expression and intervention were overwritten; only an explanation remained, and explanations do not enter J0–J5. We therefore replaced both model calls with a valid empty explanation and recomputed every theory, commitment and verdict without inference.

All 2,400 candidate verdicts matched the archive. The replay retained the pooled 400 known-family and 100 held-out jump-world successes and the structurally guaranteed 0/300 control false jumps. Phi-4 output was therefore not semantically necessary for C3. The perfect result belongs to the typed deterministic search, hand-authored motif-to-basis realizer and evaluation scaffold. More generally, the audit shows why scientific-discovery evaluations need code-path attribution: system success alone does not identify which component supplied the explanatory content.

### Interface controls separate serialization from executable proposal

Historical model-planned composition scored 0/400, but offline reconstruction showed that this could not isolate proposal quality. All 1,200 responses were non-empty and JSON-extractable, yet none contained the required outer plan list; every response reached its completion cap. Contract inspection also showed that the prompt omitted executor argument keys. On a fixed outcome-blind panel of 96 historical worlds, increasing Phi-4 precision or budget, substituting DeepSeek, or allowing one validator repair left every legacy-interface condition at 0/96. Native DeepSeek returned reasoning but no separate answer to the parser. These failures were dominated by pre-executable attrition and do not establish conceptual incapacity.

A separately frozen grammar-constrained DeepSeek condition supplied exact parser syntax but no truth, fitted law, intervention outcome or semantic repair. All 4,608 plan opportunities were schema-valid and 3,939 were dynamically executable. The resulting model-proposed graph edits yielded 15/96 successful worlds, concentrated in meta-law and unification, compared with 16/96 for outcome-blind random composition on the identical panel (Fig. 4). The deterministic scaffold still supplied motif realization, fitting, ranking and intervention. The redesigned two-stage, grammar-constrained interface yielded executable model-generated edit plans, but did not show that the model independently supplied the realized law or outperformed random primitive search. Full precision, budget, repair, token-cap and supplied-representation diagnostics are reported in Supplementary Sections S12–S16 and Extended Data Figures 1–3.

### Counterfactual replay tests predictive content and field binding

We froze an inference-free realizer-dependence audit after the preceding component findings and before counterfactual replay (Fig. 4). It retained every archived candidate representation and slot from C3 and C_rand across 400 known-family and 100 held-out worlds, plus the grammar-constrained DeepSeek candidates on the 96-world panel. The aligned policy reproduced all archived gates and verdicts without mismatch. We then replaced every non-incumbent motif realization with the exact incumbent expression while retaining the outside-space candidate graph and deterministically recommitting its maximum-separation public action. C3 fell from 400/400 and 100/100 to 0/400 and 0/100; C_rand fell from 52/400 and 13/100 to zero; DeepSeek fell from 15/96 to zero. Despite this, 1,168/1,500 C3, 1,040/1,500 C_rand and 236/288 DeepSeek candidate slots still passed cumulative J1–J2; none passed J3. Because this intervention sets the candidate expression equal to the incumbent expression, prediction separation is zero and failure at J3 follows by construction. This structural negative control verifies removal of non-incumbent predictive content; it does not establish that this particular basis library is the only realization mechanism capable of supporting escape.

A second policy retained each detected motif's algebraic term shape but rebound variables canonically by public field type and lexical order, without node roles or inspection of which fields changed across intervention queries. It retained 347/400 known-family and 100/100 held-out C3 successes, 8/96 DeepSeek successes, and 57/400 plus 13/100 C_rand successes. C3 losses were confined to hidden regimes (26/50 retained) and meta-law (21/50); DeepSeek retained 5/12 meta-law and 3/12 unification worlds. This policy is not semantics-free because it preserves the motif's algebra. Within this fixed pipeline, changing field binding affects a subset of archived successes even when motif algebra is retained. The incumbent-substitution control does not compare alternative realizers capable of producing non-incumbent expressions.

Leave-one-signature-out replay sharpened the attribution. Masking `relation_arity_3` removed all 100 held-out C3 successes. Masking `multi_argument_function` removed 50 C3 worlds and all 15 DeepSeek worlds. Masking `unobserved_dependency` removed 100 C3 worlds; the remaining active signatures each accounted for 50, except `shared_rule_binding`, whose removal caused no world loss because alternative `multi_argument_function` candidates covered the same unification worlds. These are post-confirmatory fixed-candidate sensitivities, not reruns of search under a new realizer.

### Transfer to one held-out structural family

The second study reserved `triadic_relation_reification` from development, pilot inference and known-family confirmation. C3 succeeded in 100/100 held-out worlds, C_rand in 13/100, and C0, C1, C2 and C_self in none (difference from C_rand 0.87, 95% CI 0.80–0.93; adjusted P=3.00×10−4).

The holdout is limited: an earlier family used binary property-to-relation change, the generic language already included reification and the shared realizer already contained the triadic-product basis. The arity-three target structure, generator and instances were new, but the realization mechanism was not. This is therefore a search-side structural-family holdout; one adjacent family cannot support broad external generalization.

### A worked prospective escape

In one held-out world, observations with x=z=w gave y=9x³, so the incumbent `y=9x³` and candidate `y=9xzw` both fit exactly. Four generic edits reified the incumbent prediction edge, changed the new relation to arity three, and bound z and w; the pre-specified realizer supplied the `xzw` basis and fitted its coefficient (Fig. 5). Before outcome reveal, the assay committed to setting z from 6 to 7 at x=w=6. The incumbent predicted 1,944; the candidate predicted 2,268; the revealed outcome was 2,268. A separate held-out falsification case at z=5 yielded 1,620, again exact for the candidate. The representation failed the frozen language on relation count, type, arity bindings and result structure, and passed J0–J5.

### Specificity and replay

The zero false-jump count requires qualification. In C3 controls, 800 of 900 candidates passed J1, 567 passed J2 and 283 passed J3, but none passed J4. The null was therefore non-trivial through the prospective commitment gate. An offline check verified that the selected observation-optimal comparator exactly matched the simulator on all 1,625 intervention and falsification cases across the 300 CJ5 control worlds (and all 1,125 cases in the 200 AJ5 controls). Under this verified condition, no candidate can achieve the strictly positive error reduction required by J4 and J5. The observed 0/300 is best interpreted as a structural-specificity check under the exact simulator, not an empirical false-positive estimate for noisy science; the Wilson upper bound is descriptive only.

All 10,800 AJ5 and 16,800 CJ5 selected candidates replayed exactly, including 35,533 CJ5 ancestry records. No confirmatory world was excluded and no shard was rerun.

## Discussion

This work contributes an assay for a specific event: an executable candidate leaves a frozen hypothesis language and pays for that move with a prospective prediction that beats the selected observation-optimal incumbent and survives separate held-out falsification cases. Canonical non-membership, commitment-before-outcome-reveal ordering and exact replay distinguish this event from judged novelty or retrospective fit.

The code-path and counterfactual audits are methodological results. They demonstrate that a system-level discovery benchmark can assign successful explanatory content to a language model even when deterministic scaffolding supplies the decisive representation, basis, fit, ranking and intervention. Substituting incumbent expressions eliminated prospective discrimination by construction; role/action-blind rebinding supplies the non-trivial sensitivity result. Conversely, legacy model-planned zero rates were dominated by pre-executable attrition, whereas executable AJ5 model proposals usually failed at later gates. A grammar-constrained interface restored executability and exposed model-generated graph topology, but the deterministic scaffold still supplied realization and evaluation, all successes used one motif and aggregate performance did not exceed random composition. End-to-end failure can therefore underestimate what reaches the evaluator, just as end-to-end success can overattribute explanatory content to a model. Claims of model-driven representation change require field-level provenance throughout the committed theory.

A system-level escape claim, a model-contribution claim and a representation-invention claim require different evidence. The first concerns whether the committed executable theory passes the assay. The second requires tracing model-authored fields into the evaluated artifact and testing whether those fields affect the outcome. The third additionally requires showing that the decisive explanatory forms were not supplied by a benchmark-aligned realization library. Passing the first test does not establish the other two.

External validity is the principal limitation. The worlds are synthetic and noiseless; C3 is saturated; search strata, generators and motif-to-basis realizer were co-designed; and the operator language embeds graph, function, relation and binding priors. The original confirmation used one model; the extension sampled only one additional checkpoint on a fixed subset, and its native condition was not compute-matched. Only one conceptually adjacent, search-side family was held out. World seeds quantify within-generator reliability. The higher-level generalization units are nine structural families, only one of which was held out, so small world-level P values do not substitute for structural breadth.

A decisive extension should freeze the current assay and add independently authored families, distractor primitives, deeper compositions, stochastic observations, partial observability and at least one recognizable mechanistic simulation. Broader open and proprietary model comparisons could then use the tested separation of reasoning and grammar-valid answer stages, while reporting dynamic executability and J1–J5 rather than treating format compliance as scientific success. These experiments are proposed, not part of the present evidence.

The conclusion is narrow but durable: hypothesis-space expansion can be measured prospectively and replayed exactly; typed deterministic search paired with a hand-authored algebraic realizer aligned with the procedural generators can produce it in controlled worlds; and causal component auditing can reveal when apparent capability or incapacity instead belongs to the scaffold or interface.

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

After auditing the frozen responses, we specified one additional DeepSeek condition on the identical 96-world panel. Each of three slots retained 16 independent four-step plans and therefore 48 representation opportunities per world. The first call reserved 4,096 tokens for native reasoning; a second call received that model-produced deliberation and a complete parser-level operation syntax, used `reasoning_effort=none`, and reserved 4,096 tokens for a compact grammar-constrained plan object. These two calls replaced the original proposal-plus-explanation allocation, preserving six calls per world. The schema guaranteed only JSON structure, plan count, depth, operator names and argument keys/types. The grammar-constrained condition exposed 28 non-crossover primitives because no donor graph was supplied; the original CJ5 vocabulary contained 29 including crossover.

The serializer received no fitted expression, truth, target distance, intervention outcome, gate value or semantic repair. Worlds, primitive vocabulary, candidate slots, opportunities, deterministic downstream fitter and intervention selector, hidden-information boundaries and J0–J5 were unchanged. The model supplied graph-edit topology; the scaffold supplied motif realization, fit, selection among the 16 plans and the committed maximum-separation intervention. The protocol and code were frozen at commit `b6e1561` and tag `nmi-fair-interface-v1-protocol-freeze`. A subsequent operational amendment partitioned families into four disjoint shards without changing calls or scientific settings. A post-freeze 31-call throughput pilot used eight formal-panel worlds and returned 15 non-empty responses, but produced no candidate, world or summary table; it was archived and excluded before formal shards began, and the unchanged worlds were rerun. Concurrent shard launch then exposed a four-sequence server limit: three timeout-only shard directories contained no returned response or result table. We archived and excluded them, froze a second operational amendment at commit `6bab5fb` and tag `nmi-fair-interface-v1-sequential-shards`, and scheduled the unchanged shards sequentially.

### Worlds, representations and search

Generators returned public observations, candidate intervention actions without outcomes, a frozen incumbent `LanguageSpec`, hidden truth and independent intervention and falsification cases. AJ5 used eight families and 50 jump seeds per family; CJ5 used 50 new seeds per family. No-jump controls used 25 seeds per family in each phase. CJ5 added 100 held-out jump and 100 control seeds. Representations were canonical typed graphs with executable fitted programs.

AJ5 tested direct model output, model sampling, fixed-space reasoning, attribute-only mutation and two typed high-level proposal conditions. CJ5 used 29 generic local rewrites. C3 traversed 48 four-operation branches and retained three candidates by a deterministic score. The shared realizer matched candidate graphs against nine hand-authored motifs, assigned fixed basis functions aligned with the procedural mechanisms and solved only their coefficients from public observations. The held-out triadic-product basis was present before unlock. C_rand sampled 48 four-step paths. C_self requested 16 plans in each of three slots; invalid plans were not repaired.

### Prospective evaluation

J0 required incumbent observation MSE≤10−12; J1 required DSL validity and frozen-language non-membership; J2 required candidate observation MSE≤10−12; J3 required candidate–oracle prediction separation≥0.5 on the committed action; J4 required intervention MSE improvement>0.1; J5 required falsification MSE≤10−12 and improvement>0.1. Candidate, prediction, action and split hashes were committed before simulator evaluation.

### Statistics and component audit

The world was the replicate. AJ5 used 10,000 family-stratified paired bootstrap replicates for effect uncertainty; its archived uncentered bootstrap tail proportions are not null-calibrated tests. CJ5 used the same bootstrap for effects and paired sign-flip tests. Holm correction was applied within prospectively specified comparison families at α=0.05. Candidate rows were used only for attrition. Family-level distributions are reported descriptively because eight known families plus one held-out family do not support a stable population-level family inference.

The post-hoc component audit reconstructed all C3 candidates from archived deterministic representations, fitted expressions and selected interventions, replacing the model-derived explanation with an empty string. It then regenerated each world, froze a new commitment and recomputed J0–J5. No model inference was run.

The realizer-dependence protocol was frozen at commit `7753db8` and tag `nmi-realizer-audit-v1-protocol-freeze` before formal counterfactual replay. It fixed 3,288 archived candidate slots: C3 and C_rand on all 500 jump worlds and grammar-constrained DeepSeek on the 96-world panel. Eleven policies comprised aligned replay, complete motif disabling, role/action-blind field rebinding and one mask for each of eight non-incumbent signatures. Complete disabling replaced motif-derived expressions with the exact incumbent expression while preserving the candidate graph. Role/action-blind replay preserved motif algebra but assigned type-compatible public fields in lexical order, refitted coefficients from public observations and did not inspect node roles or intervention-key changes. Signature masks used incumbent fallback only for the named detected motif. Every policy deterministically selected the public action with maximum candidate–incumbent prediction separation before hidden outcomes were evaluated. The audit made zero model calls, treated worlds as the analysis unit and used candidate rows only for gate attrition.

For the targeted sensitivity analysis, exact world counts, JSR and Wilson 95% intervals are primary. Comparisons use paired world transitions and paired JSR differences on the identical 96-world panel; family rates are descriptive. The full n=400 known-family and n=100 held-out Phi-4 budget populations are supplementary descriptive sensitivities, and the n=40 positive control is shown separately. No candidate-level significance tests are performed and P values are not used as primary evidence. Response and plan attrition are reported with their denominators, followed by executable-candidate J1–J5 attrition.

### Integrity and replay

Requests, representations, ancestry edges, fitted programs, commitments, gate values and configuration hashes were retained. Replay reconstructed representations and recomputed J0–J5. Three grammar-constrained-interface shard launches were interrupted after queue starvation produced transport timeouts but before any response or scientific result was returned; their logs were archived outside the formal namespace under a frozen operational amendment, and the unchanged shards were restarted sequentially. No completed shard was rerun and there were no outcome-quality exclusions.

### AI assistance in research and writing

Phi-4 and DeepSeek generated the experimental outputs described above. OpenAI ChatGPT and Codex were used from 2 to 5 September 2026 to discuss methodological alternatives, stress-test interpretations, inspect artifacts, implement and orchestrate separately frozen analyses, verify literature metadata and assist manuscript drafting; the conversational service did not expose a stable deployed-build identifier, so no finer model-version claim is made. These systems did not alter historical confirmatory source data or change frozen evaluation rules. All protocols, code changes, statistical outputs, citations and interpretations were reviewed and approved by the human authors, who retain full responsibility for the work.

## Data availability

Synthetic-world definitions, historical and extension result tables, manifests and replay artifacts, including the inference-free realizer audit, are included in the project repository (https://github.com/gbanyan/abductive-jump). Historical AJ5/CJ5 raw call ledgers and raw superseded-extension shards are not tracked directly in Git; a release utility combines them with the tagged publication commit, writes a file-level SHA-256 manifest and stream-verifies the archive. The exact submission snapshot and its checksum are provided in release `nmi-github-submission-v4` (https://github.com/gbanyan/abductive-jump/releases/tag/nmi-github-submission-v4). The original confirmatory state and separate sensitivity namespaces are identified by commits and tags. No personal or restricted third-party data were used. A DOI-minted archival copy will be deposited before publication.

## Code availability

Source code for generation, search, evaluation, offline attrition, statistics, figure generation, component audit, replay and reviewer-archive verification is included in the public project repository and fixed by release `nmi-github-submission-v4`. Original software is licensed under Apache-2.0 and original synthetic research data and derived artifacts under CC BY 4.0; path-level scope is stated in `LICENSE_SCOPE.md`. A DOI-minted archive will be cited in the accepted version. Model weights are not redistributed; repository identifier, revision and runtime are reported above.

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
21. Bellemare-Pepin, A. et al. Divergent creativity in humans and large language models. *Sci. Rep.* **16**, 1279 (2026). https://doi.org/10.1038/s41598-025-25157-3
22. Zahavy, T. LLMs can't jump. PhilSci-Archive preprint 28024 (2026). https://philsci-archive.pitt.edu/28024/
23. Pu, Y., Lin, T. & Chen, H. Principle-Evolvable Scientific Discovery via Uncertainty Minimization. In *ICML*, PMLR **306** (2026).
24. Murphy, K. Model Discovery Agent: LLM-assisted Bayesian experiment design for data-efficient discovery of mechanistic world models. Preprint at https://arxiv.org/abs/2608.09696 (2026).
25. Zhong, T. et al. Before the Action: Benchmarking LLMs on Prospective Hypothesis Discovery. Preprint at https://arxiv.org/abs/2607.15766 (2026).
26. Zhao, Q. et al. EvoSCM: scientific belief revision through causal model evolution and experimentation. Preprint at https://arxiv.org/abs/2609.01526 (2026).
27. Chen, T. et al. HypoSpace: a diagnostic benchmark for set-valued hypothesis generation under underdetermination and sublinear coverage bounds. Preprint at https://arxiv.org/abs/2510.15614 (2025).
28. Liu, Y. et al. ResearchBench: benchmarking LLMs in scientific discovery via inspiration-based task decomposition. In *Findings of the Association for Computational Linguistics: ACL 2026* 13187–13207 (2026). https://doi.org/10.18653/v1/2026.findings-acl.644
29. Ding, A. W. & Li, S. Generative AI lacks the human creativity to achieve scientific discovery from scratch. *Sci. Rep.* **15**, 9587 (2025). https://doi.org/10.1038/s41598-025-93794-9
30. Pearl, J. *Causality* 2nd edn (Cambridge Univ. Press, 2009).
31. Peters, J., Janzing, D. & Schölkopf, B. *Elements of Causal Inference* (MIT Press, 2017).

## Acknowledgements

No additional acknowledgements.

## Author contributions

J.-R.H. performed conceptualization, methodology, software, validation, formal analysis, investigation, data curation, visualization, project administration and writing of the original draft. W.-H.L. performed supervision and writing - review and editing. Both authors reviewed and approved the manuscript.

## Funding

This research received no specific grant from any funding agency in the public, commercial or not-for-profit sectors.

## Competing interests

The authors declare no competing interests.

## Correspondence

Correspondence and requests for materials should be addressed to Jing-Rung Huang (p78084063@mail.ncku.edu.tw).
