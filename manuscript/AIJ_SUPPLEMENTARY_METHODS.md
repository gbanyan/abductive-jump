# Supplementary methods: AIJ version

Companion to *Prospective evaluation and component attribution of hypothesis-space expansion in AI systems*. Historical artifact paths and freeze tags are retained verbatim for traceability. Scientific values are unchanged; terminology distinguishes the finite comparator from the full representation language.


## S1. Formal estimand

Let `R0` denote the incumbent representation and `A0` the set of representations admitted by the frozen `LanguageSpec`. Let `P0 = world.incumbent_programs` denote the finite frozen executable comparator set. The comparator procedure selects `h0* = argmin_h (L_obs(h), canonical_json(h))` over `P0`, using lexicographic ordering of the pair. Thus ties in observation loss are broken deterministically by canonical JSON, not by intervention performance. We do not assume that all observational optima are intervention-equivalent, nor claim a universal optimum over every function expressible by the language. J4 and J5 compare against this selected observational optimum.

A candidate theory contains a representation `R` and an executable expression `f`. J1 requires a valid representation with `R` outside `A0`; the later gates evaluate `f`. The canonical membership certificate concerns explicit structural constraints, not a general proof that no functionally equivalent incumbent expression exists. A world-level validated jump requires at least one of three candidates to pass all J0–J5 gates.

The jump success rate is the proportion of jump worlds with a validated candidate. The false-jump rate applies the identical decision to control worlds whose truth is in the frozen incumbent program set. Abductive precision is the number of validated candidates divided by candidates passing J0–J3. These quantities answer different questions and are never substituted for one another.

## S2. Procedural families

AJ5 generated eight families: latent common cause, unification, hidden regimes, property-to-relation, state invention, coordinate transformation, causal ambiguity and meta-law. Each generator returned public observations, an incumbent representation and language, a hidden executable truth, a finite intervention domain and separate held-out falsification cases. Generator validation checked deterministic output, truth redaction, exact incumbent observational fit, existence of a discriminating intervention and reachability of a valid escaped explanation.

Jump seeds were 10000–10049 per family and controls 20000–20024 per family. CJ5 used reconstruction seeds 30000–30049, controls 50000–50024, held-out jump seeds 40000–40099 and held-out controls 60000–60099. World generation used no LLM output.

## S3. Typed representation and incumbent membership

A representation is a canonical graph of typed nodes and edges plus executable equations, dependencies, constraints, observability, arity, temporal indices and argument bindings. Canonical serialization sorts unordered fields before hashing. `LanguageSpec.contains` checks node kinds, edge/relation forms, equation families and other frozen admissibility constraints. J1 records at least one concrete membership failure and cannot be satisfied by renaming or paraphrase. The public world supplied candidate intervention actions and input settings to proposers and fitters, but withheld every intervention outcome.

The implementation exhausts `world.incumbent_programs`, sorts by observation loss and canonical program JSON, and returns the first program. Exactness refers to this finite comparator set. Any failure of J0 invalidates a world rather than removing it as difficult. No such confirmatory failure occurred.

## S4. AJ5 conditions

- **B0 direct LLM:** directly emits a typed theory graph.
- **B1 sample matched:** high-temperature independent samples propose at most three typed operations.
- **B2 fixed-space agent:** representation remains `R0`; calls may reason and revise inside it.
- **B3 attribute mutation:** an external mechanism changes only values/equation attributes allowed by the frozen incumbent language.
- **B4 representation mutation:** three proposals sampled with replacement from a nine-member typed portfolio.
- **B5 full system:** three structurally distinct portfolio proposals, archive accounting and deterministic falsification.

The portfolio contained latent, invariant, sign-contrast regime, additive relation, additive state, square-function, affine-context, causal-edge and transition variants. This high-level alignment motivated CJ5 and is not hidden as a limitation.

The P0/P1/P2 factorial reused the same reasoning code and world populations. Only the proposal source differed: LLM, external portfolio or oracle-correct representation. At the proposal stage, P2 received the target representation but not fitted coefficients, truth-program output or hidden outcomes. Downstream fitting and maximum-separation intervention selection were supplied by the deterministic scaffold, shown in the second call and enforced in the evaluated artifact. The later DeepSeek supplied-representation sensitivity is a distinct control: its expression and selected intervention are model-authored.

B2 and B3 are structural negative controls that cannot pass J1 by design; their zero JSR does not establish a general search or reasoning limitation.

## S5. CJ5 generic primitive language

`GENERIC_PRIMITIVE_SET_V1` contains 29 local operations: add/remove node, edge, function, equation, dependency, constraint and temporal index; reverse/retype/relabel; change observability or arity; bind/unbind; compose/decompose; merge/split; reify edge or node; and bounded copy/crossover. `ADD_NODE` creates an untyped `Primitive`; typing, observability, arity, temporal indexing, dependencies and each argument binding require separate records.

Every record binds the parent hash, child hash, operator, canonical arguments, seed and depth. The implementation rejects family names, truth, outcome fields, target distance and family-level aliases such as `LATENTIZE`, `ADD_STATE`, `PROPERTY_TO_RELATION`, `ADD_REGIME`, `COMMON_CAUSE`, `META_LAW` and `COORDINATE_TRANSFORM`.

## S6. CJ5 search and controls

C3 traversed 48 branches of four local edits. Fixed allocations covered generic topologies for typed nodes, function composition, argument-bound functions, relations and reified edges. Ranking used only DSL validity, incumbent non-membership, observational compatibility, existence of an outcome-blind discriminating query, structural novelty and ancestry diversity.

C0 evaluated 192 within-space candidates. C2 evaluated 192 depth-one alternatives. C_rand drew 48 four-step paths and selected final candidates by seed-fixed structural hash. C_self supplied the identical manifest to Phi-4 and requested 16 plans in each of three slots; invalid plans consumed capacity and were not externally completed. C1 retained the AJ5 atomic portfolio as a reference. C5 supplied the target representation and deterministic truth compiler as a conditional ceiling. Because the operation semantics of C1 and C5 differ, they are shown separately in cost comparisons.

C3 and C_rand differ in both traversal and final selection. Their contrast estimates a difference between complete search-and-selection policies, not a proposal-only effect.

## S7. Held-out family and lock

`triadic_relation_reification` uses three correlated observed inputs. The incumbent language fits a cubic rule on the observational support. The target represents an arity-three relation whose product mechanism separates under intervention. A valid construction requires edge reification, an arity change and separate argument bindings. No primitive produces the complete target.

The generator, structure and confirmatory seeds were excluded from AJ5 and CJ5 pilot inference. Only deterministic unit tests for redaction, incumbent observational adequacy and constructive reachability preceded the lock. Known-family and control runs were terminal before the held-out unlock commit. Because AJ5 contained a binary property-to-relation family and the generic set already included reification, this is structural-family hold-out, not wholly concept-free invention.

## S8. Candidate fitting and intervention selection

In `structured_search`, every intermediate graph is realized and fitted by `evaluate_candidate` before its score is computed. The final `_select_diverse` ranks terminal evaluations using those fitted scores and structural diversity, retaining three. There is no fit-after-retention stage supplying the initial ranking scores. The selected candidates are then committed before outcome reveal.

The shared compositional realizer does not fit an unrestricted model to the candidate graph. It matches the graph against nine pre-specified structural signatures, assigns the fixed basis functions below and solves their coefficients from public observations. It cannot read hidden truth, validation outcomes or family labels, but the basis library was hand-authored to cover the procedural mechanisms. The held-out triadic-product basis existed at the CJ5 freeze before held-out unlock.

| Structural signature | Fixed basis supplied by the realizer | Aligned procedural mechanism |
|---|---|---|
| `relation_arity_3` | `x·z·w` | held-out triadic product |
| `temporally_indexed_recurrence` | `x`, history sums | state invention |
| `unobserved_dependency` | raw stable proxy | latent common cause / causal ambiguity |
| `unobserved_selector` | regime-signed `x` | hidden regimes |
| `bound_relation` | observed scalar variables | property-to-relation |
| `self_composed_function` | `x²` | coordinate transformation |
| `shared_rule_binding` | `x`, context | unification |
| `multi_argument_function` | `x`, `x·context` | meta-law |
| `incumbent_basis` | first two scalar variables | fallback incumbent form |

For J3, the deterministic evaluator compares realized candidate and incumbent predictions over the finite public action set and selects their maximum absolute separation. It records action, predictions, candidate hash and split hash before querying the simulator. Thus C3 and the grammar-constrained interface condition supply graph topology to a scaffold that supplies the basis, fit, ranking and committed intervention. Model-proposed actions are retained only as diagnostics in the C-series conditions; the separate DeepSeek P2 control instead evaluates its model-authored expression and selected intervention.

Thresholds were frozen: J0 and J2 observation MSE≤10−12; J3 separation≥0.5; J4 candidate intervention MSE < incumbent MSE−0.1; J5 candidate falsification MSE≤10−12 and < incumbent MSE−0.1. All six gates are conjunctive.

## S9. Opportunity and compute accounting

Every condition–world cell had three final slots, two LLM calls per slot, one final candidate evaluation and one intervention commitment per slot, with 700 completion tokens per call. AJ5 therefore executed 32,400 prospectively specified calls plus 3,600 A6 calls. CJ5 executed 33,600 calls. Unused completion capacity was not reassigned. Actual calls, tokens, attempted/valid operations, candidate evaluations, interventions and latency are reported rather than claiming equality of realized token counts.

## S10. Statistical analysis

The offline comparator check (`scripts/audit_nmi_control_comparator.py`) regenerated archived control worlds using their recorded family and seed. The selected observation-optimal program matched the simulator exactly on all intervention and falsification cases: 1,125 cases in 200 AJ5 controls, 1,125 in 200 known-family CJ5 controls, and 500 in 100 held-out CJ5 controls. Exact agreement on these scored cases prevents strictly positive error reduction in the controls. This finite-domain check does not assert intervention-equivalence of observational optima in general.

The replicate was the world. AJ5 used 10,000 deterministic, family-stratified paired bootstrap replicates with seed 20260902. Seeds were resampled inside each family and conditions remained paired; the aggregate gave each family equal weight. Percentile 95% intervals were reported for rates and paired differences. For each pair, the statistic was the equal-family mean of within-world binary success differences. Replicates resampled paired seeds with replacement separately within each family. The RNG seed was 20260902 XOR the sum of character codes in the concatenated left/right condition labels. The archived field `p_one_sided` equals (1 + number of bootstrap differences at or below zero) / 10001; `p_holm` applies the step-down Holm arithmetic to eight such quantities. These uncentered bootstrap samples estimate effect uncertainty, not a distribution constructed under the null of zero difference. We therefore describe those unchanged historical fields as bootstrap tail proportions, not calibrated hypothesis-test P values; no replacement test or model run was introduced.

CJ5 used the same stratified bootstrap for effect intervals and paired random sign-flip tests for prospectively specified beneficial contrasts. C3–C0 and C3–C2 formed the known-family primary multiplicity family; C3–C1, C3–C_rand and C3–C_self formed a secondary family. Held-out contrasts formed their own prospectively specified family. Two-sided Wilson intervals summarize JSR/FJR. No candidate-level pseudoreplication was used.

### Post-hoc component audit

An inference-free audit replaced both C3 model calls with a valid empty explanation while preserving only the archived deterministic representation, fitted expression and maximum-separation intervention. Every world was regenerated and every commitment and J0–J5 verdict recomputed. All 2,400 candidate verdicts matched, retaining 500/500 jump successes and 0/300 control false jumps. The audit is explicitly post-hoc and changes attribution, not the commit-frozen comparison.

In the 400 known-family worlds, all 1,200 historical C_self responses were non-empty and the frozen legacy parser extracted a JSON object, but the outer `plans` value was never a list. Thus 0/19,200 prospectively specified plan opportunities reached execution or structural evaluation. Every response reached the 700-token cap and strict whole-response JSON validity was 0/1,200. Incumbent fallback candidates inserted after empty self-search are excluded from proposal attrition. The analysis made no model calls.

Retained jump gain was `rho_J=(JSR_C3−JSR_C0)/(JSR_C1−JSR_C0)`. It is undefined for a non-positive denominator. It compares observed rates and does not normalize unequal operator semantics.

## S11. Exclusions, failures and replay

Parse errors, invalid graphs, non-exact fits, absent discriminating interventions and failed falsification were outcomes, not exclusions. A whole shard could be rerun only for a configuration/hash mismatch, unavailable server, missing/duplicate rows or infrastructure interruption, using identical seeds and model configuration. Confirmatory exclusions and shard reruns were both zero.

Replay rebuilt each selected representation from `R0` and its ancestry, recomputed canonical hashes and fitted expressions, reconstructed the frozen intervention, and recomputed J0–J5. AJ5 reproduced 10,800/10,800 selected candidates; CJ5 reproduced 16,800/16,800 with 35,533 ancestry records. There were no mismatches.

### Freeze identifiers and panel selection

AJ5 and CJ5 protocols were frozen in Git before their reported confirmatory model calls. AJ5 uses commit `895ebb9118ffd0046825b88868621f2a70f69f61`. CJ5 uses `65f20874e16bddf8a7ae36996395ff52b27153b7`, with a documented correction at `7ecb977` and held-out unlock at `27ee542`. The commits are publicly retrievable but unsigned, and no independent registry or transparency-log timestamp was located. We therefore describe the studies as prospectively specified and commit-frozen, not formally preregistered. Pilot seeds were excluded; no confirmatory result changed families, operators, thresholds, budgets or seeds.

The original Phi-4 artifacts were preserved at commit `ae1ede683fdef09f2bf60f6e1052b60394ad6cf8`, tag `nmi-phi4-frozen-2026-09` and archive branch `nmi-phi4-frozen-archive-2026-09`. A separate extension protocol, panel, model configurations and generation code were frozen at commit `320eb29b33ddaed596b0fe7b3f1d5895c706f311` and amended only for operational execution at `f846c89287e379fe313551c47765c24f2abf4959`. New outputs used the `nmi_minimal_sensitivity_v1` namespace and could not overwrite historical files.

An outcome-blind SHA-256 ranking selected 12 of the 50 historical CJ5 seeds before any new model call: 30014, 30012, 30029, 30025, 30011, 30023, 30000, 30032, 30001, 30037, 30002 and 30015. Applying the same seeds to all eight known families produced a fixed 96-world paired panel. The positive control used the first five selected seeds in each family (n=40). This extension is a targeted sensitivity analysis, not a replacement confirmatory population.

### Minimal targeted sensitivity protocol

Historical Phi-4 results were preserved on a dedicated tag and archive branch. The new protocol used a separate namespace and a commit-frozen panel selected by outcome-blind salted SHA-256 ranking. The same 12 existing seeds were applied to each of eight known families, yielding 96 paired worlds; no new generator or seed was introduced. A balanced supplied-representation positive control used five of those seeds per family (n=40).

The only new model conditions were Phi-4 8-bit C_self, DeepSeek matched C_self (`reasoning_effort=none`, 700 output tokens), DeepSeek native C_self (`reasoning_effort=max`, 4,096 output tokens) and DeepSeek supplied-representation positive control (`reasoning_effort=max`, 4,096 output tokens). Offline attrition crossed the prospectively frozen 25% pre-execution trigger, enabling one Phi-4 8-bit repair condition. The repair replaced, rather than augmented, a structurally invalid response and received only validator error classes; it could not receive semantic or simulator feedback.

The separately frozen `PHI-BUDGET-SENSITIVITY` reused the exact historical Phi-4 revision and 4-bit runtime. Prompt semantics, primitive vocabulary, known and held-out worlds, three candidate slots, 16 four-step plans per slot, representation opportunities, interventions, J0–J5 and all hidden-information boundaries were unchanged. Only `generation.max_tokens` increased from 700 to 2,048. The condition therefore tests sensitivity to the original completion cap; it is not compute-matched. Its source protocol was frozen at commit `4606413` and tag `nmi-extension-v1-protocol-freeze`. The completed known-family (n=400) and held-out (n=100) shards were incorporated after shard completion and before analysis tables were generated through amendment `NMI-MIN-SENS-V1-AMENDMENT-002`; the preselected 96-world panel is the primary paired comparison and the full shards are descriptive.

The original 38-shard broad-extension matrix was superseded after eight shards reached `complete_verified`. The two Phi-budget shards above were incorporated descriptively. Six additional completed shards were preserved but not used as a completed factorial:

| Superseded condition | Population | World successes | Executable plan opportunities |
|---|---:|---:|---:|
| matched DeepSeek | known-family n=400 | 0/400 | 0/19,200 |
| matched DeepSeek | held-out n=100 | 0/100 | 0/4,800 |
| Phi-4 strict-schema decoding | known-family n=400 | 0/400 | 28/19,200 |
| Phi-4 strict-schema decoding | held-out n=100 | 0/100 | 1/4,800 |
| Phi-4 one-repair | known-family n=400 | 0/400 | 0/38,400 |
| Phi-4 one-repair | held-out n=100 | 0/100 | 0/9,600 |

Three partial runs were also preserved and excluded from inference: native DeepSeek known-family with 404 completed call records, Phi-budget known-control with 1,043 records and an infrastructure-terminated Phi-budget known-family attempt with 202 of 2,400 calls. These records are disclosed in the public preservation archive; no partial run contributes a denominator or scientific estimate.

Each shard had to match its frozen seed panel, model identity, revision, call cardinality and artifact schema before receiving `complete_verified` status. Replay was locked until all five shards were verified. Analysis was then locked until all outputs replayed with zero mismatches. Reported inference consists of counts, Wilson intervals, paired world transitions, paired JSR differences and per-family descriptions. DeepSeek native is explicitly not compute-matched, and the Phi-4 sensitivity changes serving engine together with precision.

Conditional attrition rates with denominator zero are reported as NA (no executable candidates); positive rates below 0.1% retain three decimal places. Archived raw tables are preserved; publication tables apply this display convention.

## S12. Minimal sensitivity results and attrition

All legacy-interface autonomous fixed-panel conditions produced 0/96 successful worlds (Wilson 95% interval 0–3.8%): the historical Phi-4 4-bit slice, Phi-4 4-bit with the 2,048-token cap, Phi-4 8-bit, DeepSeek matched, DeepSeek native and Phi-4 8-bit with one validator-only repair. The five prospectively specified paired contrasts therefore contained 96 joint failures, no successes unique to either member and a paired JSR difference of 0.000. Each of the eight families contributed 12 worlds and had 0/12 in every legacy-interface autonomous condition; these family counts are descriptive.

The fixed-panel 2,048-token Phi-4 run produced 993/4,608 schema-valid plan opportunities but no executable plan. Across the complete descriptive known-family population, 4,642/19,200 opportunities were schema-valid and 9 executable. Those 9 plans occurred within a single selected slot, yielding one candidate, which failed J1. The held-out population produced 1,289/4,800 schema-valid and 0 executable opportunities. JSR was 0/400 known-family and 0/100 held-out, matching the historical world-level counts.

Phi-4 8-bit produced 4,608/4,608 JSON-extractable effective opportunities but 0 schema-valid because the extracted outer `plans` field was not a list. Its one-repair condition repeated the same error in every effective replacement opportunity. DeepSeek matched had 4,480 non-list `plans` errors and 128 missing plans among 4,608 opportunities. DeepSeek native exposed reasoning text in all 576 calls, but no separate answer reached the parser; 518 calls ended at the 4,096-token cap and 58 reported a stop finish reason.

The balanced DeepSeek supplied-representation control succeeded in 3/40 worlds (7.5%; Wilson 95% interval 2.6–19.9%): 1/5 coordinate-transformation and 2/5 hidden-regime worlds, with 0/5 in each other family. Of 120 model-authored expression-and-intervention candidates, 4 were parse-valid, executable and passed J1–J2; 3 also passed J3–J5. The other calls supplied reasoning text without a usable final answer; 116/120 reached the cap. This is a minimum positive control for occasional supplied-representation use, not a reliable ceiling.

The extension used 576 calls in each unrepaired n=96 C_self condition, 864 in the triggered repair and 120 in P2. Total completion tokens were 231,773 for Phi-4 8-bit, 237,792 for DeepSeek matched, 2,249,518 for DeepSeek native, 433,373 for repaired Phi-4, 485,312 for P2 and 528,976 for the fixed-panel Phi-budget condition. The service exposed reasoning text but not a separate reasoning-token count for DeepSeek. All five new shards and both Phi-budget populations replayed without mismatch: 2,772 candidate rows, zero mismatches and zero replay-time model calls.

## S13. Grammar-constrained interface sensitivity protocol

An offline audit of the matched and native DeepSeek proposal calls made no model calls. It found that the frozen self-composition prompt listed the available operators but not the exact argument names expected by the executor. All 288 matched proposal responses used at least one of the incompatible keys `source`, `target` or `type`; none was strict whole-response JSON. The legacy parser could extract an inner JSON object from an incomplete outer response, so object extraction was not evidence of a valid top-level `plans` object. Native proposal calls contained reasoning but no answer content. These findings motivated a single grammar-constrained sensitivity rather than a broader model factorial.

The grammar-constrained condition reused the fixed 96-world panel, three slots, 16 four-step plans per slot, 28 available non-crossover primitives, deterministic motif realizer and intervention selector, and unchanged J0–J5. The twenty-ninth CJ5 primitive, crossover, was unavailable because no donor graph was supplied. Each slot used two calls to the same served DeepSeek checkpoint. A native-reasoning call had a 4,096-token budget. A second `reasoning_effort=none` call received only the first call's deliberation, public world and exact parser-level syntax and had a separate 4,096-token answer budget. Its strict JSON schema fixed the outer object, 16-plan count, four-step depth, operator vocabulary and operator-specific argument keys and string types. It did not guarantee that referenced nodes or edges existed when used, that operations composed successfully, or that a resulting representation fit observations or separated intervention predictions.

No truth, target distance, fitted expression, intervention outcome, J3–J5 value or semantic validator feedback entered either call. The two-stage allocation preserved six calls per world by replacing the original proposal-plus-explanation calls; no additional representation opportunity was added. Protocol, configuration and code hashes were frozen at commit `b6e1561` and annotated tag `nmi-fair-interface-v1-protocol-freeze`. An operational amendment at commit `a65974f` and tag `nmi-fair-interface-v1-shard-freeze` partitioned the eight families into four disjoint two-family shards while retaining concurrency four inside each runner. The server admitted at most four simultaneous sequences. Concurrent launch starved three shards behind that limit: each accumulated four 600-s timeout records but no returned response, candidate table, world table or summary. Those timeout-only directories were archived outside the formal namespace and excluded; a second operational amendment at commit `6bab5fb` and tag `nmi-fair-interface-v1-sequential-shards` froze sequential execution of the unchanged shards. This changed wall time and scheduling only. A separate post-freeze, pre-amendment 31-call throughput pilot used eight formal-panel worlds and returned 15 non-empty outputs but produced no candidate, world or summary table; it was excluded and the worlds were rerun unchanged.

## S14. Grammar-constrained interface sensitivity results

The grammar-constrained interface produced strict whole-response JSON, schema-valid operation names and parser-level argument types in 4,608/4,608 plan opportunities. Dynamic execution succeeded for 3,939/4,608 plans (85.5%), and 280/288 selected candidate slots contained at least one executable proposal. Cumulative selected-candidate attrition was 236/280 at J1, 236/280 at J2 and 21/280 at each of J3, J4 and J5. The 21 validated candidates yielded 15/96 successful worlds (15.6%; Wilson 95% interval 9.7–24.2%). Compared separately with the historical Phi-4 slice, matched DeepSeek and native DeepSeek, each paired table contained 81 joint failures, 15 successes unique to the grammar-constrained condition, no successes unique to the reference and a paired JSR difference of +0.156.

Success was family-concentrated: meta-law succeeded in 9/12 worlds and unification in 6/12; causal ambiguity, coordinate transformation, hidden regimes, latent common cause, property-to-relation and state invention each succeeded in 0/12. All 21 validated candidates had structural signature `multi_argument_function`; the other selected executable candidates comprised one `bound_relation` and 258 `incumbent_basis` realizations. On the same panel, C_rand succeeded in 16/96 worlds: 66 worlds failed under both conditions, 15 succeeded only under C_rand, 14 only under the grammar-constrained condition and one under both. Thus the model-generated plans did not exceed random composition in aggregate and showed a different family-specific motif distribution. Family counts are descriptive. All 288 deliberation calls returned reasoning text and reached the 4,096-token cap. All 288 serialization calls returned strict schema-valid answers and stopped before their separate cap. Deliberation and serialization used 1,179,648 and 574,538 completion tokens, respectively; the service exposed no separate reasoning-token count. The formal condition used 576 calls and no transport retry.

Deterministic replay verified all 288 candidate rows with zero scientific, prompt or request mismatches and zero replay-time model calls. The initially frozen verifier nevertheless reported 576 metadata mismatches because it expected an `engine` field on each call-ledger row, whereas the frozen runner stores engine metadata in each shard summary's stage manifests. A post-hoc verifier correction preserved the initial report and frozen verifier hash, verified model identity, revision, quantization, engine, engine version and generation settings across all four shard manifests, and omitted only the nonexistent per-call engine comparison. No inference artifact or scientific result changed.

## S15. Software and environment

The repository records package versions, configuration hashes, prompt identifiers, model revision, vLLM image digest, GPU class and random seeds in reproducibility manifests. DeepSeek used FP8 weights with an NVFP4 key-value cache under patched vLLM `0.25.2.dev0+g752a3a504.d20260714`; Phi-4 8-bit used Transformers 4.56.1 and bitsandbytes 0.47.0. Tests cover world determinism, public-field redaction, DSL membership, primitive legality, budget invariants, reachability, statistics and replay. Historical raw call ledgers and raw superseded-extension shards are included in the public release preservation archive with file-level hashes; they are not tracked directly in Git. The publication phase did not call the model or generate new experimental rows.

## S16. Grammar-constrained prompt and analysis templates

The deliberation system instruction was:

```
Reason about executable representation changes using only the supplied public world and primitive syntax. Do not use or invent intervention outcomes, hidden truth, target distance or gate feedback. A separate call will serialize your reasoning, so prioritize sixteen independent four-step plans and exact references.
```

The serialization system instruction was:

```
Return only the compact JSON plan object required by the response schema. Do not explain, repair semantically, use hidden information or add any outcome claim.
```

The serialization request contained the public world, the first call's deliberation and a syntax manifest listing the 28 available operators, their exact parser-level argument keys, four required steps per plan and 16 required plans. The strict response schema allowed one object with a single `plans` array; each plan contained exactly four operation objects, and each operation was one of the frozen operator-specific schemas with no additional properties. Full machine-readable schemas and prompt construction are in `src/abductive_jump/fair_interface.py`; their hashes are in the fair-interface protocol.

World-level Wilson intervals use the two-sided score interval. AJ5 effect intervals resample seeds within each family, keep conditions paired, aggregate families with equal weight and take the 2.5th and 97.5th percentiles of 10,000 deterministic replicates. CJ5 sign-flip tests flip paired world differences under the null, use the finite-replicate correction `(extreme+1)/(replicates+1)` and apply Holm correction within each prospectively specified comparison family. Candidate rows enter attrition tables only and never replace the world as the inferential unit.

## S17. Realizer-dependence counterfactual audit

The post-confirmatory protocol was frozen at commit `7753db8` and annotated tag `nmi-realizer-audit-v1-protocol-freeze` before formal replay. SHA-256 hashes fixed the CJ5 candidate table, grammar-constrained configuration, call ledger and candidate table, as well as the runner and counterfactual-realizer code. The audit made zero model calls and refused execution if any frozen input or code hash changed.

The audit fixed all three selected candidate slots from C3 and C_rand for 400 known-family and 100 held-out jump worlds, plus all three selected grammar-constrained DeepSeek slots for 96 known-family worlds. It therefore evaluated 3,288 archived candidate slots under eleven policies, producing 36,168 candidate-policy rows and 12,056 world-policy rows. Aligned replay reproduced every archived candidate gate and world verdict with zero mismatches.

`motif_disabled` replaced the expression of every detected non-incumbent motif with the exact incumbent expression while retaining the archived candidate representation. The maximum-separation action was then reselected from the unchanged public action set and committed before hidden outcomes were evaluated. Cumulative candidate attrition remained 1,168/1,500 through J2 for C3, 1,040/1,500 for C_rand and 236/288 for grammar-constrained DeepSeek, but all three reached 0 at J3. World success consequently changed from 400/400 known plus 100/100 held out to zero for C3, from 52/400 plus 13/100 to zero for C_rand, and from 15/96 to zero for DeepSeek.

Because incumbent substitution sets candidate and comparator predictions equal, maximum separation is zero, below the J3 threshold of 0.5. J3 failure follows by construction. This is a structural negative control for removal of non-incumbent predictive content, not evidence that this specific basis library is irreplaceable. Signature masking has the same built-in effect on affected candidates; world losses describe coverage among the fixed archived slots.

`role_action_blind_binding` retained the algebraic terms supplied by each detected motif but replaced their variable identities with type-compatible, non-nuisance public fields in lexical order. It did not use representation roles or inspect which fields changed in intervention queries. Coefficients were refitted using public observations. This policy retained 347/400 known-family and 100/100 held-out C3 worlds, 57/400 and 13/100 C_rand worlds, and 8/96 DeepSeek worlds. C3 retained 26/50 hidden-regime and 21/50 meta-law worlds and all worlds in the other seven families; DeepSeek retained 5/12 meta-law and 3/12 unification worlds. Because motif algebra remained intact, this condition isolates field-binding information but is not a semantics-free realizer.

Eight leave-one-signature-out policies replaced only the named motif with incumbent fallback. For C3, masking `relation_arity_3` removed all 100 held-out worlds; masking `unobserved_dependency` removed 100 known-family worlds; and masking each of `bound_relation`, `multi_argument_function`, `self_composed_function`, `temporally_indexed_recurrence` and `unobserved_selector` removed 50. Masking `shared_rule_binding` removed no world because selected `multi_argument_function` candidates provided redundant coverage in unification worlds. For DeepSeek, only `multi_argument_function` supported validated candidates, so its removal changed 15/96 to zero. Exact Wilson intervals, paired transitions, per-family counts, signature distributions and gate attrition are stored in `experiments/nmi_realizer_audit_v1/analysis`.

The audit fixes candidates that were originally selected under the aligned realizer and therefore does not estimate how search would adapt if rerun under a different realizer. It is a causal sensitivity of the archived end-to-end verdict, not a replacement confirmatory study, a model-conceptualization test or evidence of external scientific generalization.

## S18. Relation to adjacent evaluation designs

References correspond to the main manuscript. Representation repair has classical precedents in constructive induction and predicate invention [7–9,32,40,41]. HYDRA and the neurosymbolic novelty architecture already evaluate model repair and system components [34,35]; online dynamic predicate invention further connects representation learning to a predict–verify–refine loop [39].

Model Discovery Agent explicitly separates proposal from Bayesian inference, reports an expansion-component ablation and caches calls [24]. EvoSCM combines model revision, discriminating interventions and committed predictions [26]. Harness-aware evaluation and complete-trace failure attribution address model/scaffold confounding directly [36–38]. The contribution here is therefore the implemented coupling of canonical structural escape, committed executable theory, hidden tests, decisive-field provenance, specified replay interventions and supplied-knowledge inventory. We make no priority claim for any individual ingredient or for the first combination across all AI literature.

A field entering the evaluator is evidence of authorship, not by itself an effect on success. The historical C3 deletion replay, grammar-constrained topology path and separate supplied-representation expression/action control instantiate different provenance paths. Their evidence and limits are reported separately in the main-text claim/evidence table.

## S19. Implemented joint validity V(T)

V(T) is the absence of errors from the three checks below. It is a bounded syntactic and feature-support check, not a semantic correspondence proof. Locations refer to the source files whose hashes accompany the evidence record; no evaluator was changed for this revision.

| Check and source location | Checks performed | Not established |
|---|---|---|
| Graph: `representation.py:78`, `Representation.validate` | Unique node IDs; nonempty, whitespace-free IDs; JSON-normalizable finite attributes; existing edge endpoints; nonempty edge relations; no duplicate edges. `parse_theory` converts kind labels to `NodeKind`. | Complete semantic typing, argument compatibility, causal correctness or connectedness of the whole graph |
| Expression: `expressions.py:17`, `Expression.validate` | Allowed operations const, var, raw_var, add, sub, mul, div, pow, neg, history_sum and if_eq; recursive required operands; at most 64 nodes and depth 12; finite non-boolean numerical constants; allowed variable names | Algebraic correctness, dimensional types, graph dependency equivalence or guaranteed execution. The prompt's tighter 32-node/depth-8 limits are not these evaluator defaults |
| Feature support: `executable.py:109`, `theory_consistency` | history_sum or history requires a connected StateVariable; pow requires a connected Function unless the incumbent equation is polynomial2; regime requires Regime; environment requires Relation; raw_var requires LatentVariable. If the incumbent has Context, context use requires Function, otherwise Invariant | Exact correspondence between expression operands and graph edges, argument ordering, graph-to-expression derivation, full type inference or semantic equivalence. Connected support means a matching node kind with degree greater than zero |

Paths above are relative to `src/abductive_jump/`. `allowed_variables` (`executable.py:69`) collects non-private input names across all splits and intervention keys, not hidden outcome values. It does not infer argument types. The expression traversal for feature support visits arg, left, right, then and else. Structural non-membership is checked separately by `LanguageSpec.membership_failures` (`representation.py:128`) against allowed kinds, counts, relations, edge signatures and equation families.

Execution checks are also separate from V(T): `Expression.evaluate` rejects division by near-zero denominators, invalid powers and non-finite results; `expression_loss` converts specified evaluation exceptions to infinite loss. Thus an expression can pass static validation yet fail execution or predictive gates. `evaluate_executable` (`executable.py:166`) conjoins V(T) with J1-J5. Commitment verification compares world, theory and split hashes, predictions and digest, but does not authenticate the timestamp. `freeze_theory` (`executable.py:143`) requires exactly one public intervention and calculates its prediction before hidden losses are computed.

## S20. A traceable evidence record and reusable adapter

The full record is `manuscript/AIJ_EVIDENCE_RECORD_EXAMPLE.json`, version 1.0.0, validated against `schemas/aij-evidence-record-v1.schema.json` (JSON Schema draft 2020-12). `scripts/build_aij_evidence_record.py` is the CJ5 trace adapter; `scripts/validate_aij_evidence_record.py` checks its schema and, with `--reproduce`, verifies source hashes and exact deterministic reconstruction. Both tools implement version 1.0.0. The earlier unfilled template remains a capture checklist, not experimental evidence or a substitute for the schema.

The example is held-out world `h-52dfdb7df153f50fdcb0`, seed 40000, C3 slot 0, also shown in Section 5.1. The raw candidate result is in `artifacts/compositional/confirmatory-heldout/candidate_results.parquet`; reconstructed graph/expression columns are in `artifacts/compositional_candidates.parquet`. The two model responses are lines 6 and 20 of `artifacts/compositional/confirmatory-heldout/llm_calls.jsonl`, with decoding seeds 614800001 and 614800002. The ledger is supplied in the frozen evidence release. File-level hashes and the complete model output strings are retained in the JSON record.

The phase-one response proposed an unscaled product and was used only for a JSON-validity diagnostic. Phase two returned `USE_SUPPLIED_REPRESENTATION`, `USE_SUPPLIED_FITTED_EXPRESSION` and test-0. The runner had already fitted the retained graph and selected test-0 using public prediction separation. After JSON extraction, it overwrote representation, expression and selected intervention IDs, then translated public variable names to internal names. Only the explanation text survived from the model into the theory. These transformation statements are post-hoc code inspection of `compositional_experiment.py:493-590`, not a runtime event trace.

The evaluator reads the six-node, seven-edge graph in the record, internal expression 9·w·x·z, test-0 and predicted outcome 2268. The public aliases are dax=w, suv=x and wug=z. The supplied triadic-product basis has a refitted coefficient of 9.0. A separate integrity refit reproduces the archived public expression; the deletion replay itself fixes that expression, coefficient, selected slot and action, with no refit, reranking, reselection or adaptive search.

This compact excerpt contains actual record values; it is not the full schema-valid record:

```json
{
  "schema_version": "1.0.0",
  "candidate": {"world_id": "h-52dfdb7df153f50fdcb0",
    "world_seed": 40000, "condition": "C3_GENERIC_COMPOSITION", "slot": 0},
  "raw_call_lines": [6, 20], "action": ["test-0"],
  "prediction": [["test-0", 2268.0]], "coefficient": 9.0,
  "archived_theory_hash":
    "def8cd0bed4456a38c6e3135a51209dad17053edaaa132d74cb738b1f17efabe",
  "original_timestamp": null, "original_digest": null,
  "replay": {"model_calls": 0, "gates_unchanged": true,
    "theory_hash_changed": true, "validated_jump": true}
}
```

The archived theory hash includes explanation text. Replacing that text with an empty string changes the theory hash and commitment digest but preserves all six gates and the candidate verdict. The full record stores both recomputed commitment payloads, including theory/split hashes and intervention predictions. It labels these as post-hoc reconstruction. Original commitment digest and timestamp were not persisted in the result or call ledger and remain null. Commit-before-hidden-loss ordering is supported by runner control flow; it is not an independently timestamped reveal event. No new timestamp is presented as historical evidence.

From the repository root, install the development extra, then run `.venv/bin/python scripts/build_aij_evidence_record.py` and `.venv/bin/python scripts/validate_aij_evidence_record.py --reproduce`. The second command requires the raw release ledger. Without `--reproduce`, validation checks record structure only. Another system can reuse the field/evidence schema and replace the adapter, source identifiers and evaluator. Neither mode establishes scientific novelty or verifies unavailable timing facts.
