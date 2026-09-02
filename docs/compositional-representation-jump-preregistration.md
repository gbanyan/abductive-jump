# Compositional Representation Jump Preregistration

Status: frozen before any new-phase pilot or confirmatory model call. The Git commit
containing this document, `GENERIC_PRIMITIVE_SET_V1`, the held-out generator, and the five
versioned run configurations is the binding preregistration. AJ5 commit `dd6e82c` remains a
frozen antecedent result and is not recomputed or upgraded by default.

## Questions and competing explanations

The primary question is whether a frozen LLM system plus outcome-blind external search can
construct validated representational jumps by composing local generic rewrites when no
dedicated family-level jump operator is available. The secondary prospective question is
whether the same frozen system succeeds on a structural family excluded from AJ5 development
and from new-phase pilot inference.

- **H_menu:** AJ5 mainly selected prepackaged high-level answers. Removing that menu makes
  generic composition approach fixed-space performance.
- **H_comp:** finite compositions of generic primitives retain a material fraction of the AJ5
  advantage and beat matched depth-one search.

Failure is a terminal scientific result. No post-result operator, depth, prompt, family,
fitness, model, or generation-policy rescue is permitted.

## Frozen antecedent and audit

The antecedent AJ5 rates are B0 1/400, B1 1/400, B2 0/400, B3 0/400, B4 142/400, and B5
142/400, with 0/200 false jumps per condition. The new phase does not alter those rows.
`docs/compositional-jump-existing-state-audit.md` establishes that 299/299 successful B4/B5
candidate rows came from a fixed nine-member portfolio whose first `ADD_NODE` supplied a
family-aligned node kind or functional attribute. Recorded depth two or three therefore does
not establish low-level construction.

## Frozen model and runtime

- Host: `gblinux`, one RTX 4090; no DGX, second GPU, fine-tuning, LoRA, RL, or cross-world
  adaptation.
- Model: `microsoft/phi-4`, revision
  `2db69c1c3e91a05d2c64a3185acfbaf36f744e25`.
- Quantization: bitsandbytes 4-bit.
- Engine: vLLM OpenAI server 0.10.2, image
  `vllm/vllm-openai:v0.10.2`, digest
  `sha256:607442e407b0fea97f8a132a78b787c121a996dd4de181fa08e8da06e71ec2db`.
- Context limit 4096; temperature 0.2; top-p 0.95; maximum 700 completion tokens; no
  generation-policy change after freeze.

## Frozen primitive language

`artifacts/generic_primitive_manifest.json` is `GENERIC_PRIMITIVE_SET_V1`. It contains 29
local graph/AST operations: add/remove node, edge, function, equation, dependency, constraint,
and temporal index; reverse/retype/relabel/change observability/change arity; bind/unbind;
compose/decompose; merge/split; edge/node reification; and bounded copy/crossover.

`ADD_NODE` creates only an untyped `Primitive` and rejects type or semantic attributes.
Typing, observability, arity, temporal indexing, dependencies, and each argument binding are
separate records. Every record binds parent hash, child hash, operator, canonical arguments,
seed, and depth. No primitive accepts family, truth, target distance, test outcomes, or a
semantic fitness judgment.

The following and all synonyms are excluded from generic conditions: `LATENTIZE`,
`ADD_STATE`, `PROPERTY_TO_RELATION`, `ADD_REGIME`, `COMMON_CAUSE`, `META_LAW`,
`UNIFY_MECHANISMS`, `CAUSAL_CONFOUNDER`, `COORDINATE_TRANSFORM`, and any one-step
family-conditioned payload. Legacy AJ5 markers such as `transform=square`,
`form=affine_context`, `form=additive_linear`, and `contrast=sign_flip` are forbidden.
The old portfolio is accessible only to reference condition C1.

## Composition, reachability, and distance

Every generic candidate is a linear ancestry
`R0 -> R1 -> ... -> Rd`. The registered maximum is `d_max=4`. A compositional jump requires
depth at least two, J0--J5, prospective validation, incumbent-oracle improvement, and replay.
No depth-one prefix of its ancestry may itself be a validated jump.

Before this freeze, deterministic benchmark-validity code constructed witnesses for ten
development seeds in each existing family and ten unit-test seeds in the held-out generator:
90/90 passed J0--J5 and 0/90 depth-one prefixes passed. Registered bounded construction
depths include two, three, and four. Witness sequences are used only by the reachability
module and artifacts; search code neither imports nor queries them. The certificate is a
constructive upper bound plus a depth-one lower bound, not a proof of globally exact graph
edit distance. The estimator field is therefore named `bounded_minimum_depth` and this
limitation must remain visible.

## Search mechanisms and leakage prohibition

C3 performs a stratified traversal of the primitive product grammar. Strata are generic DSL
topologies (typed node, function composition, argument-bound function, relation, and reified
edge). It enumerates 48 branches of four local edits and ranks final candidates using only:

- DSL validity and incumbent-language escape;
- observational compatibility;
- availability of a discriminating prediction on public outcome-free queries;
- structural novelty and ancestry diversity.

The ranker cannot read family, truth, target edit distance, validation/test/falsification
outcomes, or semantic LLM judgments. Its strata and fixed allocation are disclosed because
they may still encode useful structural priors; Reviewer #2 must assess whether this narrows
the claim.

C_rand draws 48 random four-step paths from the same local action generator and selects three
final candidates by a seed-fixed structural hash order, without the objective ranker.
C_self gives Phi-4 the identical manifest and requests 16 four-step plans in each of three
slots. Valid plans run through the same engine; invalid or missing plans consume their fixed
opportunity and are not repaired. Objective structural/fit ranking chooses one candidate per
slot. The external system never semantically completes an invalid LLM plan.

## Conditions

- **C0_FIXED_SPACE:** incumbent representation; 192 matched within-space candidate
  evaluations, no representation operation.
- **C1_ATOMIC_HIGH_LEVEL:** frozen AJ5 B4 portfolio and frozen AJ5 fitter; reference/upper
  condition with three atomic alternatives. Its unequal operation cost is reported separately.
- **C2_GENERIC_DEPTH_1:** 192 one-step alternatives; no composition.
- **C3_GENERIC_COMPOSITION:** 48 branches x depth 4 = 192 primitive operations/evaluations.
- **C_SELF_LLM_COMPOSITION:** three calls x 16 plans x depth 4 = 192 attempted-operation
  capacity; valid-use and malformed rates are reported.
- **C_RAND_RANDOM_PRIMITIVES:** 48 random branches x depth 4 = 192 operations/evaluations.
- **C5_ORACLE_REPRESENTATION:** ground-truth representation and deterministic truth-program
  compiler; conditional ceiling, not a search comparison.

C4 archive is omitted because AJ5 B5 equaled B4 and archive causality is not required for the
registered question. This omission is frozen before results.

Every condition has three final candidate slots, two LLM calls per slot, one deterministic
prospective intervention per candidate, identical 700-token call capacity, and the same
J0--J5 thresholds. Unused completion capacity is not reassigned. Actual prompt/completion
tokens, valid primitive operations, attempted operations, candidate evaluations, and
interventions are reported. C1 and C5 are reference ceilings and appear on a separate cost
frontier where their operation semantics are not comparable.

## Populations, seeds, and held-out lock

### Existing-family reconstruction

Eight AJ5 families x seeds 30000--30049: 400 worlds. These structures are known and can only
test reconstruction after removing the atomic menu.

### Held-out structural family

Primary family: `triadic_relation_reification`, seeds 40000--40099: 100 worlds. Incumbent
representations directly connect three observed inputs to a locally adequate cubic rule under
correlated observations. Truth reifies a genuinely arity-three relation and prospective
interventions break the correlation. Construction requires reifying an edge, changing arity,
and separately binding additional arguments; no primitive creates the complete mechanism.

AJ5 contained a binary property-to-relation family and a dormant generic reification
operator, so the broad concept of reification is not unseen. What is held out is the
higher-arity structural family, its product mechanism, generator, and confirmatory instances.
This is the preregistered contamination boundary; success cannot be described as wholly
concept-free invention. Temporal state invention was rejected as the held-out choice because
AJ5 already contained that family explicitly.

The held-out generator may be unit-tested for determinism, redaction, oracle adequacy, and
constructive reachability. No LLM or search call may inspect a held-out confirmatory instance
until all existing-family confirmatory and control shards are terminal. Pilot uses only the
eight known families at seed 801. Failure may not cause a family switch.

### No-jump controls

- Existing families: eight x seeds 50000--50024 = 200 worlds.
- Held-out interface: seeds 60000--60099 = 100 worlds.

Truth is inside the incumbent language. Report FJR overall, by depth, family/interface, and
condition. Depth-dependent over-invention is not pooled away.

## Execution and stopping

The immutable order is: preregistration commit; existing-only pilot; confirm the registered
budget invariants without changing them; existing reconstruction; existing no-jump controls;
C_self and C_rand are part of those same shards; unlock held-out jump; held-out controls;
analysis; adversarial review; deterministic replay; final verdict. Shards abort on HTTP,
server, missing-row, duplicate-seed, or budget-accounting failures. Malformed scientific
outputs consume their slot. Infrastructure-only reruns must use identical seeds/config/model
and preserve failed logs. There are no outcome-based exclusions.

## Gates and metrics

J0--J5 retain the AJ5 thresholds: observational and falsification epsilon `1e-12`, minimum
prediction separation `0.5`, counterfactual improvement `0.1`, and falsification improvement
`0.1`. A world succeeds when at least one of three candidates passes all gates.

Primary metrics are JSR, FJR, acceptance precision, counterfactual gain, and cost to jump.
New metrics are compositional JSR, retained jump gain

`rho_J = (JSR_C3 - JSR_C0) / (JSR_C1 - JSR_C0)`,

minimum successful depth, success conditional on depth, structural primitive-sequence
diversity, held-out JSR, and the full operation/call/token/candidate/intervention frontier.
If the denominator for `rho_J` is nonpositive, rho is undefined and cannot support CJ4/5.

## Confirmatory comparisons and statistics

The unit is the world. All tests are one-sided in the registered beneficial direction and
paired by identical family/seed where conditions share worlds.

Primary family-stratified comparisons on the 400 reconstruction worlds are C3 > C0 and C3 >
C2. Use 10,000 family-stratified paired bootstrap replicates for effect CIs and paired random
sign-flip/permutation p-values; Holm-correct the two primary p-values at family-wise alpha
0.05. Report C3 vs C1, C_rand, and C_self with Holm correction as a separate secondary
family. Report Wilson 95% intervals for every JSR/FJR and family-level rates without using
them to change the primary decision.

Held-out C3 vs C0 is an independent paired exact/sign-flip comparison on 100 worlds, reported
with its world-level Wilson interval. It is not pooled with the old eight families. Held-out
C3 vs C2, C_rand, and C_self are secondary and Holm-corrected within the held-out family.

## Frozen success and safety criteria

- Controlled FJR for CJ4: C3 overall no-jump point estimate at most 1% and Wilson 95% upper
  bound at most 2%; no monotonic material depth increase larger than 2 percentage points.
- Meaningful retention: `rho_J >= 0.25` with a positive lower 95% bootstrap bound.
- Multi-family support: C3 success point estimate exceeds C0 in at least four of eight known
  families.
- Held-out materiality: C3 held-out JSR exceeds C0 by at least 10 percentage points, the
  paired p-value is below 0.05, and its 95% lower effect bound is positive.
- Held-out safety: C3 held-out-interface FJR point estimate at most 1% and Wilson upper bound
  at most 5%.

## Exclusions and replay

Confirmatory worlds are never dropped for difficulty, zero effect, malformed model output,
or adverse family result. A whole shard may be excluded only if its frozen config/hash fails,
the server/model manifest differs, rows are missing/duplicated, or an infrastructure failure
prevents prospective completion. Such a failure is repaired only by identical rerun.

Replay must reconstruct every selected representation from incumbent plus primitive records,
recompute structural hashes and fitted expression, reconstruct the exact prospective choice,
and reproduce J0--J5. Any unresolved mismatch makes the corresponding condition invalid; it
is not silently excluded.

## Verdict tree

1. **CJ0 -- invalid compositional benchmark:** any target family lacks a valid registered
   depth-four construction or deterministic oracle/redaction gate. Stop.
2. **CJ1 -- generic language insufficient:** validity witnesses pass but an exhaustive or
   registered oracle composition procedure cannot reliably realize executable targets. Stop;
   do not call this LLM failure.
3. **CJ2 -- atomic menu dependence:** C1 positive while C3 does not significantly beat C0 or
   C2, or retained gain is effectively zero. AJ5 remains; stop AJ6.
4. **CJ3 -- partial compositional retention:** C3 improves on baseline but misses any CJ4
   criterion, or CJ4 passes while held-out materiality/safety fails. AJ5 remains.
5. **CJ4 -- strong bounded compositional search:** both corrected primary tests pass,
   meaningful retention and multi-family criteria pass, FJR is controlled, successful
   ancestry is depth >=2 and replay-valid. This supports composition of generic structural
   rewrites, not general abduction.
6. **CJ5 -- held-out structural generalization:** CJ4 plus all held-out materiality, safety,
   no-dedicated-operator, lock, and replay gates. Only this permits reconsidering bounded AJ6
   candidate language: compositional held-out representation-space escape in these procedural
   worlds.

Reviewer #2 may force a lower verdict for a demonstrated leakage, invalid held-out claim,
unmatched primary opportunity, random-control equivalence that isolates no search benefit,
or replay failure. It may never raise the verdict.

## Claim boundary

Even CJ5 does not establish general scientific discovery, theory invention, universal LLM
ability, or autonomous abduction. The maximum claim is that under the frozen procedural
worlds, generic structural rewrites were compositionally assembled into prospectively
validated explanatory representations, with prospective generalization only if the separately
reported held-out gate passes.
