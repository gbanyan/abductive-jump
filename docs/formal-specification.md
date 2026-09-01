# Formal specification

Version: draft-engine-v1. Confirmatory thresholds remain unfrozen until engine and calibration pilots finish.

## Objects

A representation is a typed, directed multigraph serialized as canonical JSON. Node kinds are:

`Primitive`, `Observable`, `LatentVariable`, `StateVariable`, `Entity`, `Property`, `Relation`, `Process`, `Context`, `Regime`, `Parameter`, `Function`, `Equation`, `Invariant`, `CausalEdge`, `Transition`, and `Constraint`.

Each node has an immutable identifier, kind, sorted attributes, and typed references. Canonicalization sorts nodes, references, and attribute keys, normalizes finite numbers, excludes provenance, and hashes the resulting UTF-8 JSON with SHA-256. Scientific provenance is stored separately so equal structures have equal hashes.

The incumbent language `H(R0)` is a frozen `LanguageSpec` containing allowed node kinds, identifiers, edge signatures, equation families, maximum kind counts, and allowed parameter domains. Membership is deterministic. A candidate escapes precisely when it is valid under the general DSL and fails incumbent-language membership for at least one structural reason. Merely changing an allowed value, coefficient, threshold, sign, boundary, edge strength, or rule selection remains within-space.

## Two genomes

- `G_H` contains parameters and rule/equation selections under an unchanged `LanguageSpec`.
- `G_R` contains the typed graph and may alter primitives, relations, topology, state, regimes, invariants, or type-level organization.

Mutation records contain parent hash, operator, canonical arguments, seed, child hash, and timestamp/run identifier. Operators never receive ground truth.

## World protocol

Every generated world records family, control status, generation seed, randomized lexical seed, ground-truth hash, incumbent hash, and disjoint observation/validation/intervention splits. A world is confirmatory-eligible only if its family has an exact or certified bounded incumbent oracle and passes engine validation.

Observation data are generated only from the declared observation policy. Candidate selection may inspect observations and the public intervention action set but not validation/test outcomes. A `ProspectiveCommitment` binds candidate hash, intervention, prediction, world split hash, and freeze timestamp before the simulator reveals the result.

## Jump gates

- **J0 Local adequacy:** exact incumbent oracle observational loss is at most `epsilon_obs`.
- **J1 Representation escape:** candidate is DSL-valid and outside the frozen incumbent language for a structural reason.
- **J2 Compatibility:** candidate observational loss is at most `epsilon_candidate_obs`.
- **J3 Discrimination:** before outcome reveal, candidate and incumbent oracle predictions differ by at least the registered separation threshold for an allowed intervention.
- **J4 Prospective validation:** after commitment, candidate counterfactual loss is lower than oracle loss by more than registered `delta_cf`.
- **J5 Falsification survival:** candidate remains valid/consistent and meets the registered loss and margin criteria across an independently generated falsification set.

All six booleans are materialized. “Validated abductive jump” is their conjunction; no aggregate score may override a failed gate.

## Loss and oracle contract

Each family declares its outcome type and loss. Primary engine families use deterministic scalar outcomes and mean squared error after a preregistered normalization. The incumbent oracle enumerates a finite frozen parameter/rule grid or uses a family-specific analytic minimizer with a verifiable certificate. An approximate unconstrained optimizer without a bound is exploratory only.

The oracle is fit only on observations. Validation can reject malformed/calibration candidates. Test interventions are unavailable until a prospective commitment exists.

## Required families and controls

The engine targets eight generators: latent common cause, unification, hidden regimes/split, property-to-relation, state invention, coordinate transform, causal ambiguity, and meta-law. Each generator must produce randomized parameters, topology where applicable, samples, intervention availability, nuisance structure, and lexicalization. No-jump controls instantiate the same interfaces with truth in the incumbent language and must be of comparable scale.

Negative controls include structurally unchanged semantic paraphrases, invalid structural changes, unnecessary latents, and overcomplicated representations without counterfactual gain.

## Blindness and leakage

Generation modules know truth. Proposal/mutation modules receive a redacted `PublicWorld` containing only observations, incumbent representation/language, action schema, and budgets. Evaluators receive candidate and sealed world through a narrow API. Tests must demonstrate that public serialization omits truth, hidden parameters, intervention outcomes, and family-specific solution hints.

## Confirmatory claim boundary

The strongest permissible primary conclusion is comparative success at validated representation escape in the tested procedural worlds. No result licenses claims about consciousness, human-level creativity, universal scientific discovery, architectural impossibility, or all LLMs.

