# Supplementary Methods

## S1. Formal estimand

Let `R0` denote a world’s incumbent typed representation and `H(R0)` the frozen set of executable hypotheses admitted by its `LanguageSpec`. The incumbent oracle `h0*` minimizes observation loss over `H(R0)`. A candidate representation `R` is an escape only when it is DSL-valid and `R ∉ H(R0)` under canonical membership checks. A world-level validated jump requires at least one of three candidates to pass J0–J5; semantic similarity and model judgment are excluded.

The jump success rate is the proportion of jump worlds with a validated candidate. The false-jump rate applies the identical decision to control worlds whose truth is in `H(R0)`. Abductive precision is the number of validated candidates divided by candidates passing J0–J3. These quantities answer different questions and are never substituted for one another.

## S2. Procedural families

AJ5 generated eight families: latent common cause, unification, hidden regimes, property-to-relation, state invention, coordinate transformation, causal ambiguity and meta-law. Each generator returned public observations, an incumbent representation and language, a hidden executable truth, a finite intervention domain and independent falsification cases. Generator validation checked deterministic output, truth redaction, exact incumbent observational fit, existence of a discriminating intervention and reachability of a valid escaped explanation.

Jump seeds were 10000–10049 per family and controls 20000–20024 per family. CJ5 used reconstruction seeds 30000–30049, controls 50000–50024, held-out jump seeds 40000–40099 and held-out controls 60000–60099. World generation used no LLM output.

## S3. Typed representation and incumbent membership

A representation is a canonical graph of typed nodes and edges plus executable equations, dependencies, constraints, observability, arity, temporal indices and argument bindings. Canonical serialization sorts unordered fields before hashing. `LanguageSpec.contains` checks node kinds, edge/relation forms, equation families and other frozen admissibility constraints. J1 records at least one concrete membership failure and cannot be satisfied by renaming or paraphrase.

The incumbent oracle is exhaustive where the admissible grid is finite and bounded by a registered exact procedure otherwise. Any failure of J0 invalidates a world rather than removing it as difficult. No such confirmatory failure occurred.

## S4. AJ5 conditions

- **B0 direct LLM:** directly emits a typed theory graph.
- **B1 sample matched:** high-temperature independent samples propose at most three typed operations.
- **B2 fixed-space agent:** representation remains `R0`; calls may reason and revise inside it.
- **B3 attribute mutation:** an external mechanism changes only values/equation attributes allowed by `H(R0)`.
- **B4 representation mutation:** three proposals sampled with replacement from a nine-member typed portfolio.
- **B5 full system:** three structurally distinct portfolio proposals, archive accounting and deterministic falsification.

The portfolio contained latent, invariant, sign-contrast regime, additive relation, additive state, square-function, affine-context, causal-edge and transition variants. This high-level alignment motivated CJ5 and is not hidden as a limitation.

The P0/P1/P2 factorial reused the same reasoning code and world populations. Only the proposal source differed: LLM, external portfolio or oracle-correct representation. P2 did not receive fitted parameters, truth-program output or intervention outcomes.

## S5. CJ5 generic primitive language

`GENERIC_PRIMITIVE_SET_V1` contains 29 local operations: add/remove node, edge, function, equation, dependency, constraint and temporal index; reverse/retype/relabel; change observability or arity; bind/unbind; compose/decompose; merge/split; reify edge or node; and bounded copy/crossover. `ADD_NODE` creates an untyped `Primitive`; typing, observability, arity, temporal indexing, dependencies and each argument binding require separate records.

Every record binds the parent hash, child hash, operator, canonical arguments, seed and depth. The implementation rejects family names, truth, outcome fields, target distance and family-level aliases such as `LATENTIZE`, `ADD_STATE`, `PROPERTY_TO_RELATION`, `ADD_REGIME`, `COMMON_CAUSE`, `META_LAW` and `COORDINATE_TRANSFORM`.

## S6. CJ5 search and controls

C3 traversed 48 branches of four local edits. Fixed allocations covered generic topologies for typed nodes, function composition, argument-bound functions, relations and reified edges. Ranking used only DSL validity, incumbent non-membership, observational compatibility, existence of an outcome-blind discriminating query, structural novelty and ancestry diversity.

C0 evaluated 192 within-space candidates. C2 evaluated 192 depth-one alternatives. C_rand drew 48 four-step paths and selected final candidates by seed-fixed structural hash. C_self supplied the identical manifest to Phi-4 and requested 16 plans in each of three slots; invalid plans consumed capacity and were not externally completed. C1 retained the AJ5 atomic portfolio as a reference. C5 supplied the target representation and deterministic truth compiler as a conditional ceiling. Because the operation semantics of C1 and C5 differ, they are shown separately in cost comparisons.

## S7. Held-out family and lock

`triadic_relation_reification` uses three correlated observed inputs. The incumbent language fits a cubic rule on the observational support. The target represents an arity-three relation whose product mechanism separates under intervention. A valid construction requires edge reification, an arity change and separate argument bindings. No primitive produces the complete target.

The generator, structure and confirmatory seeds were excluded from AJ5 and CJ5 pilot inference. Only deterministic unit tests for redaction, oracle adequacy and constructive reachability preceded the lock. Known-family and control runs were terminal before the held-out unlock commit. Because AJ5 contained a binary property-to-relation family and the generic set already included reification, this is structural-family hold-out, not wholly concept-free invention.

## S8. Candidate fitting and intervention selection

The shared fitter deterministically maps a valid representation and public observations to an executable program. It cannot read hidden truth, validation outcomes or family labels. For J3, the designer evaluates candidate and incumbent predictions over a finite public action set and selects their maximum absolute separation. It records action, predictions, candidate hash and split hash before querying the simulator. Model-proposed actions are retained only as diagnostics.

Thresholds were frozen: J0 and J2 observation MSE≤10−12; J3 separation≥0.5; J4 candidate intervention MSE < incumbent MSE−0.1; J5 candidate falsification MSE≤10−12 and < incumbent MSE−0.1. All six gates are conjunctive.

## S9. Opportunity and compute accounting

Every condition–world cell had three final slots, two LLM calls per slot, one final candidate evaluation and one intervention commitment per slot, with 700 completion tokens per call. AJ5 therefore executed 32,400 prospectively specified calls plus 3,600 A6 calls. CJ5 executed 33,600 calls. Unused completion capacity was not reassigned. Actual calls, tokens, attempted/valid operations, candidate evaluations, interventions and latency are reported rather than claiming equality of realized token counts.

## S10. Statistical analysis

The replicate was the world. AJ5 used 10,000 deterministic, family-stratified paired bootstrap replicates with seed 20260902. Seeds were resampled inside each family and conditions remained paired; the aggregate gave each family equal weight. Percentile 95% intervals were reported for rates and paired differences. One-sided empirical P values included the finite-replicate correction and eight primary comparisons were Holm adjusted.

CJ5 used the same stratified bootstrap for effect intervals and paired random sign-flip tests for registered beneficial contrasts. C3–C0 and C3–C2 formed the known-family primary multiplicity family; C3–C1, C3–C_rand and C3–C_self formed a secondary family. Held-out contrasts formed their own prospectively specified family. Two-sided Wilson intervals summarize JSR/FJR. No candidate-level pseudoreplication was used.

### Post-hoc component audit

An inference-free audit replaced both C3 model calls with a valid empty explanation while preserving only the archived deterministic representation, fitted expression and maximum-separation intervention. Every world was regenerated and every commitment and J0–J5 verdict recomputed. All 2,400 candidate verdicts matched, retaining 500/500 jump successes and 0/300 control false jumps. The audit is explicitly post-hoc and changes attribution, not the registered comparison.

In the 400 known-family worlds, all 1,200 historical C_self responses were non-empty and the registered legacy parser extracted a JSON object, but the outer `plans` value was never a list. Thus 0/19,200 registered plan opportunities reached execution or structural evaluation. Every response reached the 700-token cap and strict whole-response JSON validity was 0/1,200. Incumbent fallback candidates inserted after empty self-search are excluded from proposal attrition. The analysis made no model calls.

Retained jump gain was `rho_J=(JSR_C3−JSR_C0)/(JSR_C1−JSR_C0)`. It is undefined for a non-positive denominator. It compares observed rates and does not normalize unequal operator semantics.

## S11. Exclusions, failures and replay

Parse errors, invalid graphs, non-exact fits, absent discriminating interventions and failed falsification were outcomes, not exclusions. A whole shard could be rerun only for a configuration/hash mismatch, unavailable server, missing/duplicate rows or infrastructure interruption, using identical seeds and model configuration. Confirmatory exclusions and shard reruns were both zero.

Replay rebuilt each selected representation from `R0` and its ancestry, recomputed canonical hashes and fitted expressions, reconstructed the frozen intervention, and recomputed J0–J5. AJ5 reproduced 10,800/10,800 selected candidates; CJ5 reproduced 16,800/16,800 with 35,533 ancestry records. There were no mismatches.

### Minimal targeted sensitivity protocol

Historical Phi-4 results were preserved on a dedicated tag and archive branch. The new protocol used a separate namespace and a commit-frozen panel selected by outcome-blind salted SHA-256 ranking. The same 12 existing seeds were applied to each of eight known families, yielding 96 paired worlds; no new generator or seed was introduced. A balanced supplied-representation positive control used five of those seeds per family (n=40).

The only new model conditions were Phi-4 8-bit C_self, DeepSeek matched C_self (`reasoning_effort=none`, 700 output tokens), DeepSeek native C_self (`reasoning_effort=max`, 4,096 output tokens) and DeepSeek supplied-representation positive control (`reasoning_effort=max`, 4,096 output tokens). Offline attrition crossed the prospectively frozen 25% pre-execution trigger, enabling one Phi-4 8-bit repair condition. The repair replaced, rather than augmented, a structurally invalid response and received only validator error classes; it could not receive semantic or simulator feedback.

The separately frozen `PHI-BUDGET-SENSITIVITY` reused the exact historical Phi-4 revision and 4-bit runtime. Prompt semantics, primitive vocabulary, known and held-out worlds, three candidate slots, 16 four-step plans per slot, representation opportunities, interventions, J0–J5 and all hidden-information boundaries were unchanged. Only `generation.max_tokens` increased from 700 to 2,048. The condition therefore tests sensitivity to the original completion cap; it is not compute-matched. Its source protocol was frozen at commit `4606413` and tag `nmi-extension-v1-protocol-freeze`. The completed known-family (n=400) and held-out (n=100) shards were incorporated before outcome analysis through amendment `NMI-MIN-SENS-V1-AMENDMENT-002`; the preselected 96-world panel is the primary paired comparison and the full shards are descriptive.

Each shard had to match its frozen seed panel, model identity, revision, call cardinality and artifact schema before receiving `complete_verified` status. Replay was locked until all five shards were verified. Analysis was then locked until all outputs replayed with zero mismatches. Reported inference consists of counts, Wilson intervals, paired world transitions, paired JSR differences and per-family descriptions. DeepSeek native is explicitly not compute-matched, and the Phi-4 sensitivity changes serving engine together with precision.

## S12. Minimal sensitivity results and attrition

All autonomous fixed-panel conditions produced 0/96 successful worlds (Wilson 95% interval 0–3.8%): the historical Phi-4 4-bit slice, Phi-4 4-bit with the 2,048-token cap, Phi-4 8-bit, DeepSeek matched, DeepSeek native and Phi-4 8-bit with one validator-only repair. The five registered paired contrasts therefore contained 96 joint failures, no successes unique to either member and a paired JSR difference of 0.000. Each of the eight families contributed 12 worlds and had 0/12 in every autonomous condition; these family counts are descriptive.

The fixed-panel 2,048-token Phi-4 run produced 993/4,608 schema-valid plan opportunities but no executable plan. Across the complete descriptive known-family population, 4,642/19,200 opportunities were schema-valid and 9 executable. Those 9 plans occurred within a single selected slot, yielding one candidate, which failed J1. The held-out population produced 1,289/4,800 schema-valid and 0 executable opportunities. JSR was 0/400 known-family and 0/100 held-out, matching the historical world-level counts.

Phi-4 8-bit produced 4,608/4,608 JSON-extractable effective opportunities but 0 schema-valid because the extracted outer `plans` field was not a list. Its one-repair condition repeated the same error in every effective replacement opportunity. DeepSeek matched had 4,480 non-list `plans` errors and 128 missing plans among 4,608 opportunities. DeepSeek native exposed reasoning text in all 576 calls, but no separate answer reached the parser; 518 calls ended at the 4,096-token cap and 58 reported a stop finish reason.

The balanced DeepSeek supplied-representation control succeeded in 3/40 worlds (7.5%; Wilson 95% interval 2.6–19.9%): 1/5 coordinate-transformation and 2/5 hidden-regime worlds, with 0/5 in each other family. Of 120 model-authored expression-and-intervention candidates, 4 were parse-valid, executable and passed J1–J2; 3 also passed J3–J5. The other calls supplied reasoning text without a usable final answer; 116/120 reached the cap. This is a minimum positive control for occasional supplied-representation use, not a reliable ceiling.

The extension used 576 calls in each unrepaired n=96 C_self condition, 864 in the triggered repair and 120 in P2. Total completion tokens were 231,773 for Phi-4 8-bit, 237,792 for DeepSeek matched, 2,249,518 for DeepSeek native, 433,373 for repaired Phi-4, 485,312 for P2 and 528,976 for the fixed-panel Phi-budget condition. The service exposed reasoning text but not a separate reasoning-token count for DeepSeek. All five new shards and both Phi-budget populations replayed without mismatch: 2,772 candidate rows, zero mismatches and zero replay-time model calls.

## S13. Fair-interface sensitivity protocol

An offline audit of the matched and native DeepSeek proposal calls made no model calls. It found that the registered self-composition prompt listed the available operators but not the exact argument names expected by the executor. All 288 matched proposal responses used at least one of the incompatible keys `source`, `target` or `type`; none was strict whole-response JSON. The legacy parser could extract an inner JSON object from an incomplete outer response, so object extraction was not evidence of a valid top-level `plans` object. Native proposal calls contained reasoning but no answer content. These findings motivated a single fair-interface sensitivity rather than a broader model factorial.

The fair condition reused the fixed 96-world panel, three slots, 16 four-step plans per slot, 28 available non-crossover primitives, deterministic fitter and intervention selector, and unchanged J0–J5. Each slot used two calls to the same served DeepSeek checkpoint. A native-reasoning call had a 4,096-token budget. A second `reasoning_effort=none` call received only the first call's deliberation, public world and exact parser-level syntax and had a separate 4,096-token answer budget. Its strict JSON schema fixed the outer object, 16-plan count, four-step depth, operator vocabulary and operator-specific argument keys and string types. It did not guarantee that referenced nodes or edges existed when used, that operations composed successfully, or that a resulting representation fit observations or separated intervention predictions.

No truth, target distance, fitted expression, intervention outcome, J3–J5 value or semantic validator feedback entered either call. The two-stage allocation preserved six calls per world by replacing the original proposal-plus-explanation calls; no additional representation opportunity was added. Protocol, configuration and code hashes were frozen at commit `b6e1561` and annotated tag `nmi-fair-interface-v1-protocol-freeze`. An operational amendment at commit `a65974f` and tag `nmi-fair-interface-v1-shard-freeze` partitioned the eight families into four disjoint two-family shards while retaining concurrency four inside each runner. The server admitted at most four simultaneous sequences. Concurrent launch starved three shards behind that limit: each accumulated four 600-s timeout records but no returned response, candidate table, world table or summary. Those timeout-only directories were archived outside the formal namespace and excluded; a second operational amendment at commit `6bab5fb` and tag `nmi-fair-interface-v1-sequential-shards` froze sequential execution of the unchanged shards. This changed wall time and scheduling only. A separate 31-call pre-amendment throughput pilot likewise produced no result tables and was excluded from all analyses.

## S14. Software and environment

The repository records package versions, configuration hashes, prompt identifiers, model revision, vLLM image digest, GPU class and random seeds in reproducibility manifests. Tests cover world determinism, public-field redaction, DSL membership, primitive legality, budget invariants, reachability, statistics and replay. The publication phase did not call the model or generate new experimental rows.
