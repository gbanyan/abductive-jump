# NMI component audit: frozen AJ5 and CJ5 implementation

Status: Phase 1 static implementation audit. This document describes the frozen
Phi-4 call graph at tag `nmi-phi4-frozen-2026-09`. It does not run model
inference, inspect extension confirmatory results, change historical artifacts,
or create a new scientific result.

## Executive finding

The executable implementation is less LLM-dependent than several historical
condition labels suggest.

- In AJ5, Phi-4 has a semantic proposal role only in B0 and B1 (and therefore
  factorial P0). In B0 it emits a representation; in B1/P0 it emits a typed
  mutation plan. Every fitted expression and every committed intervention are
  nevertheless selected deterministically.
- In AJ5 B2--B5 and factorial P1/P2, the supplied representation is not
  semantically altered by Phi-4. A malformed first response can still discard
  it and force an incumbent fallback, so the model remains a *parse-validity
  gate*, not a scientific reasoner.
- In all AJ5 conditions and P0--P2, the second Phi-4 response does not determine
  the fitted law or intervention. The runner overwrites both with the
  deterministic fitter and exact maximum-separation choice. Any parseable JSON
  object is enough; only the unused explanation survives.
- CJ5 C3 is already the legitimate no-self-proposal/external-search condition.
  Its representation construction, parameter fitting, ranking, and intervention
  choice are deterministic. The two Phi-4 calls per slot contribute no retained
  scientific field; the second call only gates evaluation on JSON parseability.
  A new condition called “C3 minus LLM” would therefore be redundant unless it
  specifically removes this non-semantic parse gate.
- Factorial P2 does **not** by itself establish Phi-4 reasoning ability. The
  oracle representation is supplied, a deterministic fitter produces the law,
  and deterministic code chooses the intervention. Phi-4 supplies only
  parseable wrappers and an explanation that J0--J5 never inspect.

The safe causal wording is therefore “LLM proposal under B0/B1/P0,” “LLM plan
proposal under C_self,” and “deterministic external search/fitting/evaluation”
for C3 and P2. “Same LLM reasoner” describes the prompts but not the retained
decision path.

## Sources and frozen configuration

The audit follows the code rather than manuscript prose:

- `src/abductive_jump/primary_experiment.py`: AJ5 runner and shared `_run_slot`.
- `src/abductive_jump/factorial_experiment.py`: P0--P2 source mapping; delegates
  to the same AJ5 `_run_slot`.
- `src/abductive_jump/compositional_experiment.py`: CJ5 runner, self-plan parser,
  candidate construction, deterministic fitting, and final evaluation.
- `src/abductive_jump/composition_search.py`: C2/C3/C_rand traversal, scoring,
  ranking, and operation accounting.
- `src/abductive_jump/conditions.py`: public prompt payloads and output contracts.
- `src/abductive_jump/proposals.py`: LLM mutation-plan execution and the
  family-blind nine-member external portfolio.
- `src/abductive_jump/external_reasoning_calibration.py`: deterministic
  prediction-separation table.
- `src/abductive_jump/executable.py`: theory overwrite/parse, commitment, and
  J0--J5 evaluation.
- `src/abductive_jump/llm.py`: OpenAI-compatible request and permissive JSON
  extractor; no retry or repair.
- frozen configs `configs/confirmatory-primary-{jump,control}.json`,
  `configs/confirmatory-factorial-{jump,control}.json`, and
  `configs/compositional-confirmatory-*.json`.

The frozen model is `microsoft/phi-4` revision
`2db69c1c3e91a05d2c64a3185acfbaf36f744e25`, bitsandbytes 4-bit, vLLM 0.10.2,
4096-token context. API completion capacity is 700 tokens per call. The AJ5
prompt additionally instructs B0 direct phase one to finish within 600 tokens
and all supplied-representation or B1 calls within 160 tokens. C_self's first
plan-generation prompt has no smaller textual target but retains the 700-token
API cap; it requests 16 four-step plans in one response. Its second call has the
160-token textual target. These prompt-level targets matter for the planned
`PHI-BUDGET-SENSITIVITY` condition even though the registered API capacity was
equal.

## Information and time boundary

`World.public()` exposes observation inputs **and observation outcomes**, the
incumbent representation/language, nuisance-field names, and intervention
queries without their outcomes. It omits truth, validation cases, intervention
outcomes, and falsification cases/outcomes.

Before commitment:

1. an LLM or deterministic proposer sees only the public payload;
2. deterministic fitting uses public observations and their outcomes;
3. a deterministic table evaluates candidate and incumbent-oracle predictions
   on the public intervention queries, without reading their outcomes;
4. deterministic code selects the query with maximum absolute prediction
   separation (ties by case ID);
5. `freeze_theory` binds the representation, expression, split hash, chosen
   intervention, and candidate prediction.

Only `evaluate_executable` reads the hidden intervention and independent
falsification outcomes, after the commitment object has been created and
validated. The CJ5 search ranker also remains pre-outcome: it reads structural
validity/escape, observation fit, and candidate-versus-incumbent prediction
separation on outcome-free queries. C5 is an intentional ceiling exception: it
uses the hidden truth representation and truth-program compiler before
commitment, but still does not expose hidden outcomes to Phi-4.

## AJ5 call graph and roles

Every AJ5 world-condition has three final candidate slots. Nominally each slot
has two Phi-4 calls, one final candidate evaluation, and one committed
intervention: six calls, three candidate opportunities, and three interventions
per world-condition. The ex-ante API completion capacity is 4,200 tokens.

For every slot, `_run_slot` performs this sequence:

1. obtain or propose a representation;
2. parse/validate the phase-one response;
3. deterministically fit an expression to observations;
4. deterministically compute the prediction table and exact intervention;
5. ask Phi-4 a second time with the fitted expression and table;
6. overwrite the returned representation, expression, and intervention with the
   deterministic values;
7. freeze, then evaluate J0--J5.

| Condition | Representation source retained | Phi-4 semantic role | Deterministic role | Invalid phase one | Nominal opportunity |
|---|---|---|---|---|---|
| B0 direct | Phi-4 JSON theory representation | Generates the representation; emitted expression/intervention are discarded | Fit law, rank intervention, freeze, J0--J5 | Fallback to incumbent | 3 model-proposed representations; 6 calls; 3 interventions |
| B1 sample-matched | Phi-4 plan of 1--3 typed high-level mutations | Chooses operators/arguments at temperature 0.7 | Execute plan, fit, rank intervention, freeze, gates | Fallback to incumbent | 3 plans/representations; at most 9 executed plan mutations; 6 calls; 3 interventions |
| B2 fixed space | Incumbent | No retained semantic choice; phase-one and phase-two parse gates only | Fixed representation, fit, rank, freeze, gates | Fallback is the same incumbent | 3 duplicate candidate slots; 6 calls; 3 interventions |
| B3 attribute | Deterministic equation-attribute variant indexed by slot | No retained semantic choice; parse gates only | Construct value-only variant, fit, rank, freeze, gates | Discards variant and falls back to incumbent | 3 variants; 6 calls; 3 interventions |
| B4 representation mutation | Seeded draw with replacement from external portfolio | No retained semantic choice; parse gates only | Construct/select proposal, fit, rank, freeze, gates | Discards external proposal and falls back to incumbent | 3 selected proposals; 6 calls; 3 interventions |
| B5 full system | Seeded structurally distinct external portfolio subset | No retained semantic choice; parse gates only | Construct/select diverse proposals, fit, rank, freeze, gates | Discards external proposal and falls back to incumbent | 3 selected proposals; 6 calls; 3 interventions |

All six conditions call the deterministic fitter once per slot in the ordinary
path (three calls per world-condition). A realization error triggers an
incumbent fallback and one additional fit for that slot. The exact intervention
designer and J0--J5 evaluator each run once for every phase-two-parse-valid slot.

AJ5 does not use `GENERIC_PRIMITIVE_SET_V1`; its “generic operations evaluated”
count is therefore zero in the CJ5 sense. B1 can execute up to three older typed
mutation operations per candidate. B4/B5 expose three candidate opportunities,
but the implementation reconstructs the complete nine-member portfolio inside
each slot invocation before selecting `external[slot]`. That is 25 legacy
mutation calls per portfolio construction and 75 per world-condition in the
ordinary three-slot runner. The same unused portfolio construction also occurs
in B0--B3 because it precedes the condition branch. These are implementation
operations, not extra candidate opportunities or generic-search evaluations,
and should not be conflated with the registered three-candidate budget.

### AJ5 parser and failure semantics

- `extract_json_object` strips an outer Markdown fence when present, scans from
  each `{`, and returns the first decodable JSON object. Trailing text is not
  rejected.
- B0 then requires a parseable theory object (representation, expression, and
  selected-intervention keys), although only its representation is retained.
- B1 requires `mutation_plan`; it must contain 1--3 steps. Each step must have
  exactly `operator` and `arguments`; the operator must be in the old typed
  enum; arguments must be an object and are string-coerced before execution.
- Any caught phase-one JSON, key, schema, type, validation, or realization error
  consumes the slot and substitutes the incumbent. No semantic or syntactic
  repair occurs.
- In phase two, any decodable JSON object is effectively sufficient because the
  runner overwrites representation, expression, and selected intervention.
  Failure to extract an object consumes the slot and prevents J0--J5 evaluation.
- The client contains no transport retry. HTTP/time-out errors arise outside the
  per-slot parse exception blocks and fail the job/shard rather than becoming a
  scientific candidate failure.

## P0--P2 factorial call graph

`factorial_experiment.py` does not implement a separate reasoner. It invokes the
same `_run_slot` with B1 for P0 and B4 for P1/P2. Budgets remain three slots,
two calls per slot, and three interventions per world-source cell.

| Source | Representation path | What Phi-4 controls | What deterministic/oracle code controls | Causal interpretation |
|---|---|---|---|---|
| P0 LLM | B1 mutation-plan path | Operators and arguments for a 1--3-step typed plan; JSON availability on second call | Plan execution, fitted expression, exact intervention, commitment, gates | Genuine LLM representation-proposal condition, followed by deterministic realization/evaluation |
| P1 external | B4 external portfolio | Only whether both responses are parseable; explanation survives but is unscored | External representation, fitted expression, exact intervention, commitment, gates | External proposal plus deterministic reasoning, with an incidental LLM parse gate |
| P2 oracle | Ground-truth representation supplied through B4 path | Only whether both responses are parseable; explanation is unscored | Oracle representation, observation-only deterministic fit, exact intervention, commitment, gates | Conditional representation ceiling; **not evidence that Phi-4 reasoned out the law or experiment** |

P2 does not use the CJ5 truth-program compiler. It supplies only the truth
representation; `fit_representation` derives the expression from observations.
Nonetheless, the central downstream work is deterministic. Removing Phi-4
semantic content while retaining parse-valid wrappers would leave the scientific
fields unchanged. Removing the calls entirely requires a clean runner change,
but the existing code already shows that no model-selected hypothesis or
intervention reaches J0--J5.

## CJ5 call graph and roles

Every CJ5 condition retains three final candidate slots and normally makes two
Phi-4 calls per slot (six calls and three intervention commitments per
world-condition). The first call is plan generation only for C_self. For all
other conditions the representation already exists and the first response is
checked only for a JSON object. The second response is parsed, then its
representation, expression, and intervention are overwritten before freezing.

| Condition | Representation generation / selection | Nominal structural work | Phi-4 dependency | Deterministic fitting and ranking |
|---|---|---:|---|---|
| C0 fixed space | Incumbent repeated into 3 slots | 0 primitive ops; registered 192 matched evaluations | No semantic dependency; first parse flag is non-causal, second parse gates gates | Repeated incumbent evaluation and fit; exact intervention |
| C1 atomic high-level | Three AJ5 external proposals, non-diverse seeded selection | 3 selected legacy alternatives; cost not comparable to generic ops | No semantic dependency; second parse gate only | High-level fitter; exact intervention |
| C2 generic depth 1 | Deterministic depth-one enumeration and objective diverse ranking | 192 one-step operations/evaluations; 3 retained | No semantic dependency; second parse gate only | Fit/rank all candidates; refit retained 3; exact intervention |
| C3 generic composition | Deterministic 48-branch, depth-4 stratified traversal and objective diverse ranking | Exactly 192 primitive applications and 192 prefix evaluations; 3 retained | **No semantic dependency**; second parse gate only | Fit/rank every prefix, refit retained 3, exact intervention, gates |
| C_self LLM composition | Phi-4 emits 16 four-step plans in each of 3 slots; objective score chooses one valid final plan per slot | 48 attempted plans / 192-operation capacity; actual use = 4 × valid plans | Genuine plan proposal; no model candidate ranking; second parse gate | Execute/validate plans, fit/score valid plans, select best per slot, refit, exact intervention |
| C_rand random primitives | Seeded random 48 paths of depth 4; final candidates selected by structural-hash order | 192 primitive applications; 3 retained | No semantic dependency; second parse gate only | Fit intermediate/final paths; hash selection; refit 3; exact intervention |
| C5 oracle representation | Truth representation repeated; truth program compiled | 0 search ops; 3 ceiling slots | No semantic dependency; second parse gate only | Intentional oracle representation/program; exact intervention; gates |

### C3 dependency conclusion

C3 does not require an LLM to construct, fit, rank, or choose an intervention.
`structured_search` constructs all paths from generic strata and public graph
topology, evaluates every prefix using observation fit and outcome-free query
separation, and `_select_diverse` chooses three. `_fit_for_condition` refits each
selected representation. `_prediction_table` and `max(...)` select the exact
intervention. Before gates, the phase-two payload is overwritten with all three
scientific fields.

The remaining model dependence is procedural: if phase two contains no
extractable JSON object, the candidate is never evaluated. The phase-one JSON
status for non-self CJ5 conditions is merely recorded and does **not** replace or
invalidate the deterministic candidate. Thus “C3 requires Phi-4” is false as a
semantic causal statement; “the historical C3 runner included six Phi-4 calls
and a phase-two parse gate” is exact.

### C_self parser and invalid-output behavior

C_self's first response is parsed as follows:

1. extract the first JSON object;
2. require `plans` to be a list;
3. consume exactly the first 16 plan positions (missing entries are failures;
   extras are ignored);
4. require each plan to contain exactly four steps;
5. require each step to have exactly `operator` and `arguments` keys;
6. require a known `GenericPrimitive`, forbid `SUBGRAPH_CROSSOVER`, require an
   argument object, string-coerce its values, and execute through
   `apply_primitive`.

Each invalid or missing plan consumes its fixed opportunity. There is no retry,
schema-constrained decoding, validator feedback, syntactic repair, semantic
repair, or deterministic completion. Valid plans are evaluated only after all
four steps, and deterministic score/ranking chooses one per slot. If a slot has
no valid plan, `max(..., default=...)` supplies the incumbent.

Two accounting caveats follow directly from the code:

- candidate-row `phase_one_valid` is set to `True` for C_self regardless of
  whether any of its 16 plans parsed or executed; plan-level validity exists
  only in `llm_self_plans.parquet`;
- `candidate_evaluations` is recorded as the 192 operation *capacity*, not the
  number of valid plans actually evaluated. Likewise, `primitive_operations_used`
  is four times the number of fully valid plans, even when a plan failed after
  one or more operations; it is not a count of every attempted prefix.

Malformed-output failure must therefore be reported as interface/validation
failure until executable candidates exist; it cannot support a claim of
conceptual inability.

## Actual versus registered deterministic accounting

The frozen metadata consistently preserves final candidate opportunity, but
some internal counters are capacity labels rather than literal function-call
counts. Static nominal counts below assume no exceptions and denote `V` as the
number of fully valid C_self plans across three calls.

| Condition | Registered `candidate_evaluations` | Literal search `evaluate_candidate` calls before final refit | Approximate fitter invocations before/at final slots |
|---|---:|---:|---:|
| C0 | 192 | 193 (192 loop + 1 shared fixed candidate) | 386 composed fits + 3 final composed fits |
| C1 | 3 | 3 | 6 composed fits for ranking + 3 AJ5 high-level final fits |
| C2 | 192 | 192 | 384 composed fits + 3 final composed fits |
| C3 | 192 | 192 | 384 composed fits + 3 final composed fits |
| C_self | 192 capacity | V + 3 eager default-candidate evaluations | 2V + 6 composed fits + 3 final composed fits |
| C_rand | 192 | 240 (192 prefixes + 48 final-path reevaluations) | 480 composed fits + 3 final composed fits |
| C5 | 3 | 1 shared oracle candidate | 2 composed fits for initial scoring; final truth-program compilation, not fitting |

Each `evaluate_candidate` invokes `fit_composed_representation` once for the
incumbent and once for the candidate. The final three slots are then fitted
again, except C5, which compiles the truth program. This table is a static code
count, not a correction to historical artifacts. Future compute tables should
separate primitive applications, search evaluations, fitter calls, final
candidate opportunities, LLM calls/tokens, and committed interventions rather
than treating them as interchangeable.

## Condition-level access summary

- **LLM access:** public observations with outcomes; public incumbent/language;
  public intervention queries without outcomes; when supplied, the candidate
  representation, deterministic fitted expression/loss, and candidate/oracle
  prediction-separation table. Never truth, validation cases, intervention
  outcomes, or falsification data.
- **External AJ5 proposer:** redacted `PublicWorld` only. It is family-blind by
  API, although its fixed high-level portfolio contains strong structural priors.
- **CJ5 search/ranker:** redacted `PublicWorld` only; no family string is passed
  into `structured_search`, `depth_one_search`, or `random_search`.
- **Fitters:** observation inputs and outcomes plus candidate representation.
- **Exact designer:** fitted candidate and incumbent-oracle predictions on the
  public action set; no action outcomes.
- **Oracle components:** incumbent oracle uses observations and the frozen
  incumbent program family; P2 additionally receives truth representation; C5
  additionally compiles the truth program.
- **Evaluator:** full `World`, including hidden intervention and falsification
  outcomes, but only after commitment validation.

## Required implications for the extension protocol

1. Substitute DeepSeek or higher-precision Phi-4 only where the model is on a
   genuine causal path: B0/B1/P0 and C_self are primary. P1/P2 and C3 need not be
   rerun under a new model label unless the scientific question explicitly tests
   parse-interface robustness.
2. Treat P1, P2, and C3 as external/deterministic reasoning paths with an
   incidental historical JSON gate. A deterministic-wrapper replay is the
   clean component test; it is not evidence of a newly invented C3 condition.
3. Record C_self validity at plan level, not through the current candidate-row
   `phase_one_valid` field.
4. Keep final candidate slots (3), plan opportunities (16 per slot), primitive
   depth (4), and interventions (3 per world-condition) distinct from added
   completion/reasoning budget in `PHI-BUDGET-SENSITIVITY`.
5. Do not call any condition compute-matched merely because it has six calls and
   three final slots. Token capacity, plan opportunity, primitive work, fitter
   work, and wall-clock/GPU compute differ.

