# Compositional Jump Existing-State Audit

Status: completed before the compositional-phase preregistration and before any new-phase
pilot or confirmatory model call. The frozen AJ5 result and its raw outputs are not modified.

## Scope and evidence inspected

This audit inspected the AJ5 preregistration, final report, Reviewer #2 report, completion
audit, world-engine validation, append-only research ledger, all B0--B5 condition code,
the mutation/proposal/realization/replay implementations, and the frozen candidate and
mutation-trace Parquet artifacts. The current repository head at audit start was
`dd6e82ce35e0016a5ae6d3d2cc23420c7a2694c2`, clean and equal to `origin/master`.

## 1. High-level semantic shortcuts

The public `MutationOperator` enum contains direct semantic operations including
`LATENTIZE`, `PROPERTY_TO_RELATION`, `ADD_STATE`, and `ADD_REGIME`. `VARIABLE_TO_FUNCTION`,
`ADD_INVARIANT`, `MERGE_RULES`, `COMPOSE`, and `REIFY_RELATION` can also be high-level in
this benchmark because one invocation changes a scientific type or creates a rule object.

More importantly, AJ5 B4/B5 did not primarily call those named operators. Its fixed external
portfolio used `ADD_NODE` followed by one or two `ADD_RELATION` calls, but the first call was
allowed to insert one of nine already typed alternatives: `LatentVariable`, `Invariant`,
`Regime`, `Relation(form=additive_linear)`, `StateVariable(form=additive_state)`,
`Function(transform=square)`, `Function(form=affine_context)`, `CausalEdge`, or `Transition`.
Those node kinds and attributes are an atomic high-level answer menu despite the low-level
operator name.

The strongest leakage path is the deterministic fitter. `fit_representation` selects its
executable basis directly from the presence of an added high-level node kind or the
`transform`, `form`, or `contrast` attribute. It generally does not require the subsequently
added edges. Thus the first `ADD_NODE` call can license the family-aligned executable
hypothesis before the recorded graph construction is complete.

## 2. Family-to-shortcut map

| Existing family | Ground-truth structural concept | AJ5 portfolio shortcut that licenses the successful basis |
| --- | --- | --- |
| latent common cause | shared unobserved source | `ADD_NODE(kind=LatentVariable)` |
| unification | common rule/invariant | `ADD_NODE(kind=Invariant)` |
| hidden regimes | regime selector and alternate rule | `ADD_NODE(kind=Regime, contrast=sign_flip)` |
| property to relation | contextual relational property | `ADD_NODE(kind=Relation, form=additive_linear)` |
| state invention | memory-bearing state and update | `ADD_NODE(kind=StateVariable, form=additive_state)` |
| coordinate transform | transformed input coordinate | `ADD_NODE(kind=Function, transform=square)` |
| causal ambiguity | unobserved common response | `ADD_NODE(kind=LatentVariable)` |
| meta-law | function governing context-specific rules | `ADD_NODE(kind=Function, form=affine_context)` |

The extra edges make graphs look more complete, but the realization code's decisive dispatch
is the added node kind/attribute. Consequently all eight required structural answers were
present in the portfolio before confirmatory inference.

## 3. Decomposition into generic rewrites

All existing ground-truth graphs can be expressed as sequences of local graph/AST edits:
create an untyped node, change its type or observability, attach local edges, bind arguments,
add or compose a function/equation, and optionally reify or split a relation. The old semantic
operators are therefore removable. A valid new primitive language must separate node
creation, typing, observability, temporal indexing, dependency creation, function creation,
and argument binding; it must not allow `ADD_NODE` to carry answer-bearing type or functional
attributes in the same operation.

## 4. How much B4 success was direct family-aligned mutation?

The frozen replay artifact contains 299 successful B4/B5 candidate rows. Their recorded
depths are 231 at depth 3 and 68 at depth 2. Every success has one of only two operator-name
sequences: `ADD_NODE -> ADD_RELATION -> ADD_RELATION` or
`ADD_NODE -> ADD_RELATION`. In every case the candidate came from the nine-member fixed
portfolio described above; therefore 299/299 successful candidate rows (100%) were exposed
to a single first-step family-aligned node kind/attribute. This is a mechanism audit, not a
claim that every first step alone would pass graph-level J0--J5.

At the world level, B4 and B5 each succeeded in 142/400 worlds. The current artifacts do not
support attributing any successful world to discovery outside that fixed portfolio.

## 5. Existing multi-step compositions

AJ5 has provenance chains of length two or three, and successful candidates cover both
lengths. These are syntactic construction chains around an atomic semantic choice, not a test
of compositional representation search. The experiment did not compare depth one with
matched deeper search, compute a minimum generic edit distance, or require that no individual
step license the target executable basis.

## 6. Ancestry/composition support

The mutation API takes a parent representation and returns a child plus a record containing
parent hash, operator, canonical arguments, seed, child hash, and timestamp. Mutation plans
apply successive records to the preceding child, and replay exports record-level ancestry.
Thus the engine genuinely supports linear ancestry and deterministic composition.

Missing capabilities for the new phase are: a frozen primitive-only allowlist; donor-aware
branch ancestry; explicit depth and operation-budget accounting; graph reachability and
minimum-distance certification; a search frontier that ranks only outcome-blind objective
features; and a compositional-success gate that rejects atomic semantic licensing.

## 7. Hidden state and mutable metadata leakage

`PublicWorld` redacts the family label, ground truth, hidden parameters, and prospective
outcomes. Candidate mutation functions receive only the incumbent/public world and explicit
arguments. No mutable global family state was found in proposal or mutation code.

There is nevertheless an indirect semantic leak: the portfolio itself enumerates the target
node kinds and answer-bearing attributes, while `fit_representation` maps those markers to
family-relevant basis functions. The public observations and intervention schemas can reveal
surface roles such as sequence-valued history or context, and the fitter uses these fields.
This is permitted observational information, but it makes a supplied `StateVariable` or
`affine_context` marker especially close to a complete answer. The new phase must make
executable semantics emerge only after multiple independently local edits and must prevent
selection code from reading family, truth, target edit distance, or prospective outcomes.

## 8. Prior exposure of the eight structures

All eight world families were used in engine development, model calibration, proposal
reachability work, pilots, and confirmatory AJ5. Their generators, truth graphs, executable
programs, and high-level portfolio analogues are present in the repository. They can only be
used as a compositional reconstruction set. They cannot establish unseen-family
generalization.

The existing `state_invention` family also means that temporal state invention is
conceptually contaminated for a new held-out gate. A genuinely held-out primary family must
not be isomorphic to that generator or be dispatched by the existing state/history fitter.
The family choice and generator will be frozen before any new-phase pilot results and its
confirmatory instances will remain sealed until after all reconstruction and control runs.

## Audit conclusion

AJ5 remains supported exactly as frozen. The present evidence cannot distinguish
representation-menu selection from generic representation construction. The new phase is
therefore justified only if it removes both named high-level operators and answer-bearing
`ADD_NODE` attributes, proves targets reachable through local primitives at registered depths,
and tests a prospectively sealed non-isomorphic family without rescue.
