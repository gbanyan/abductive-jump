# NMI component causality matrix

Status: Phase 1 static audit of the frozen AJ5/CJ5 implementation. “Yes” means a
component's semantic output can change the representation, fitted hypothesis,
candidate selection, or intervention reaching J0--J5. A parse-only dependency
is marked separately. Prompted activity is not counted as semantic causality
when the runner overwrites the returned field.

## Matrix legend

- **LLM rep:** LLM semantics generate the retained representation.
- **LLM post-rep reasoning:** a model-generated scientific decision survives
  after representation construction.
- **LLM candidate selection:** LLM semantics decide which candidate reaches a
  final slot.
- **Det fit:** deterministic code supplies the executable law/parameters.
- **Det rank:** deterministic code selects among proposed/search candidates.
- **Det intervention:** deterministic maximum-separation code commits the test.
- **Parse gate:** malformed model output changes whether the intended candidate
  reaches evaluation, without contributing scientific semantics.
- **Hidden pre:** any component intentionally accesses truth or hidden outcomes
  before commitment. Only oracle ceiling inputs qualify.
- **Hidden post:** J4/J5 evaluator reads hidden outcomes after commitment.

## AJ5 and factorial conditions

| Condition | LLM rep | LLM post-rep reasoning | LLM candidate selection | Det fit | Det rank | Det intervention | Parse gate | Hidden pre | Hidden post | Calls / final slots / interventions |
|---|---:|---:|---:|---:|---:|---:|---|---|---:|---|
| B0 | Yes, direct graph | No | Yes, one graph per slot | Yes | No cross-slot rank | Yes | Phase 1 fallback; phase 2 blocks gates | No | Yes | 6 / 3 / 3 |
| B1 | Yes, through 1--3-step plan | No | Yes, one plan per slot | Yes | No cross-slot rank | Yes | Phase 1 fallback; phase 2 blocks gates | No | Yes | 6 / 3 / 3 |
| B2 | No, incumbent | No | No | Yes | No | Yes | Phase 1 fallback is identity; phase 2 blocks gates | No | Yes | 6 / 3 / 3 |
| B3 | No, slot-indexed attribute variant | No | No | Yes | No | Yes | Phase 1 can discard variant; phase 2 blocks gates | No | Yes | 6 / 3 / 3 |
| B4 | No, external seeded draw | No | No | Yes | External seeded selection, not fitted-score rank | Yes | Phase 1 can discard proposal; phase 2 blocks gates | No | Yes | 6 / 3 / 3 |
| B5 | No, external unique subset | No | No | Yes | Deterministic structural-diversity selection | Yes | Phase 1 can discard proposal; phase 2 blocks gates | No | Yes | 6 / 3 / 3 |
| P0 | Yes, B1 plan path | No | Yes | Yes | No cross-slot rank | Yes | Same as B1 | No | Yes | 6 / 3 / 3 |
| P1 | No, external B4 path | No | No | Yes | External seeded selection | Yes | Same as B4 | No | Yes | 6 / 3 / 3 |
| P2 | No, oracle representation | No | No | Yes, observation-only | No | Yes | Can discard oracle rep; phase 2 blocks gates | Truth representation only; no hidden outcomes | Yes | 6 / 3 / 3 |

**P2 verdict:** not a genuine demonstration of LLM reasoning. Phi-4 is asked to
reason, but its representation, expression, and intervention fields are replaced
before evaluation. A parseable response and unscored explanation are its only
surviving effects.

## CJ5 conditions

| Condition | LLM rep | LLM post-rep reasoning | LLM candidate selection | Det fit | Det rank | Det intervention | Parse gate | Hidden pre | Hidden post | Calls / upstream opportunities / final slots / interventions |
|---|---:|---:|---:|---:|---:|---:|---|---|---:|---|
| C0 | No | No | No | Yes | No | Yes | Phase 1 flag only; phase 2 blocks gates | No | Yes | 6 / 192 matched evals / 3 / 3 |
| C1 | No, AJ5 external portfolio | No | No | Yes | Seeded external selection | Yes | Phase 1 flag only; phase 2 blocks gates | No | Yes | 6 / 3 legacy alternatives / 3 / 3 |
| C2 | No, deterministic depth-1 search | No | No | Yes | Yes, objective/diverse | Yes | Phase 1 flag only; phase 2 blocks gates | No | Yes | 6 / 192 one-step candidates / 3 / 3 |
| C3 | **No, deterministic composition** | **No** | **No** | **Yes** | **Yes, objective/diverse** | **Yes** | Phase 1 flag only; phase 2 blocks gates | No | Yes | 6 / 48 four-step branches / 3 / 3 |
| C_self | Yes, four-step plans | No | No: deterministic score selects | Yes | Yes, best valid plan per slot | Yes | Plan parser plus phase-2 gate | No | Yes | 6 / 48 plan opportunities / 3 / 3 |
| C_rand | No, seeded random paths | No | No | Yes | Structural-hash selection | Yes | Phase 1 flag only; phase 2 blocks gates | No | Yes | 6 / 48 random paths / 3 / 3 |
| C5 | No, oracle representation | No | No | Truth-program compiler | No | Yes | Phase 1 flag only; phase 2 blocks gates | Truth representation and program; no hidden outcomes | Yes | 6 / 3 ceiling copies / 3 / 3 |

**C3 verdict:** C3 is already the external deterministic search ablation. The LLM
does not propose, fit, rank, or select an intervention. Its phase-one output is
diagnostic only; phase two is a syntactic availability gate. A scientifically
legitimate necessity analysis should remove/bypass that gate and replay the same
archived deterministic candidates, not invent a nominally new search method.

## Field provenance at the final gate call

| Field consumed by `evaluate_executable` | B0/B1/P0 | B2--B5/P1/P2 | C0--C3/C_rand | C_self | C5 |
|---|---|---|---|---|---|
| Representation | LLM direct/plan semantics | Deterministic external, fixed, attribute, or oracle source | Deterministic search/source | LLM plan executed by deterministic engine, then deterministically selected | Oracle truth representation |
| Expression | Deterministic fitter | Deterministic fitter | Deterministic fitter | Deterministic fitter | Deterministic truth-program compiler |
| Intervention ID | Deterministic max separation | Deterministic max separation | Deterministic max separation | Deterministic max separation | Deterministic max separation |
| Explanation | Phi-4, unscored | Phi-4, unscored | Phi-4, unscored | Phi-4 second call, unscored | Phi-4, unscored |
| Commitment | Deterministic | Deterministic | Deterministic | Deterministic | Deterministic |
| J0--J5 verdict | Deterministic, hidden outcomes only after freeze | Same | Same | Same | Same |

## Failure causality

| Failure location | Operational consequence | Scientific interpretation allowed |
|---|---|---|
| AJ5 B0/B1 phase-one JSON/schema/type failure | Incumbent fallback consumes slot | Proposal/interface failure; separate structure generation from serialization where possible |
| AJ5 B2--B5 or P1/P2 phase-one failure | Intended supplied candidate is discarded | Incidental interface gate; not failure of the external/oracle representation |
| CJ5 non-self phase-one failure | Flag is false, candidate remains | Diagnostic only; no final scientific effect |
| C_self missing/invalid plan | That one of 48 plan opportunities is consumed | Syntax/schema/executability failure, not conceptual failure |
| C_self no valid plan in a slot | Incumbent becomes final candidate | Interface-conditioned proposal failure |
| Any phase-two no-JSON failure | No J0--J5 evaluation for the slot | Wrapper/interface failure because scientific fields would have been overwritten |
| Valid executable candidate fails J1--J5 | Deterministic gate failure | Representation/fit/prospective/falsification failure at the named gate |
| HTTP/time-out/process error | Job/shard exception | Infrastructure failure; not a candidate result |

## Opportunity and compute distinctions

| Quantity | AJ5/P0--P2 | C3 | C_self | Why it must remain separate |
|---|---:|---:|---:|---|
| Final candidate slots | 3 | 3 | 3 | World-level opportunity reaching prospective evaluation |
| LLM calls | 6 | 6 | 6 | Equal call count does not imply equal causal role |
| API completion capacity | 4,200 tokens | 4,200 tokens | 4,200 tokens | C_self packs 16 plans into each first call; textual targets differ |
| Upstream proposals/paths | 3 | 48 branches | 48 plan positions | Search opportunity differs despite equal final slots |
| Generic primitive capacity | 0 | 192 applied | 192 attempted capacity | C_self actual use depends on plan validity |
| Committed interventions | 3 | 3 | 3 | Fixed prospective opportunity; never increase in budget sensitivity |

The planned `PHI-BUDGET-SENSITIVITY` experiment should alter only the
predeclared completion/reasoning budget. It must leave the three final slots,
three C_self calls containing 16 plans each, four operations per plan, and three
interventions unchanged, and it must be labeled not compute-matched to the
historical condition.
