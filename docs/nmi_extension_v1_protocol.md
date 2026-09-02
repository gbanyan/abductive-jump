# NMI hardening extension v1: prospective protocol

Status at authorship: **confirmatory results locked; protocol freeze pending**. This document and
the machine-readable protocol must be committed, pushed and tagged before any extension
confirmatory command runs. The extension is a later, commit-frozen prospective sensitivity study;
it is not part of the original AJ5/CJ5 preregistration.

## Immutable boundary

The historical Phi-4 study is preserved at commit
`ae1ede683fdef09f2bf60f6e1052b60394ad6cf8` and annotated tag
`nmi-phi4-frozen-2026-09`. No historical result, prompt, seed, gate, candidate budget, manifest or
verdict will be modified or replaced. New requests and results live only under
`experiments/nmi_extension_v1/`.

The implementation audit established that P0 genuinely uses an LLM to propose a representation,
whereas P1 and P2 overwrite the model's scientific fields with deterministic external/oracle
representations and deterministic fitting. Their model calls therefore measure interface
robustness, not scientific reasoning. C3 is already the legitimate no-self-proposal condition: its
representation traversal, fit, ranking and evaluation are deterministic. C_self is the genuine
model-authored four-edit-plan condition, with deterministic selection among valid returned plans.
No redundant “C3 minus LLM” run will be invented, and P2 will not be described as proof of LLM
reasoning.

## Questions and conditions

The extension tests four separable possibilities:

1. model substitution under the original 700-token, no-repair interface;
2. a strong-model ecological ceiling with DeepSeek `reasoning_effort=max` and 4,096 completion
   tokens, but the same candidate/intervention opportunity;
3. interface sensitivity from one structural-only repair or strict JSON Schema decoding;
4. Phi-4 sensitivity to completion budget and numerical precision.

DeepSeek matched and native runs cover P0/P1/P2 and C_self. P1/P2 are retained because the user
requested them and because they quantify whether a new API can traverse the existing nonsemantic
reasoner gate; they are interpreted under the audit boundary above. Repair and constrained-output
runs apply only to C_self. Deterministic C0-C3/C_rand/C5 are not rerun under a model label.

The exact DeepSeek target is
`deepseek-ai/DeepSeek-V4-Flash-Vision-Exp@86f746b36186f0e567729a5c06a8c918caba82a9`,
served as `deepseek-v4-flash-vision-exp`; it is not identified as the 0731 release. Matched uses
reasoning `none`, 700 tokens, temperature 0.2 and top-p 0.95. Native uses reasoning `max`, 4,096
tokens and the same sampling parameters. The server combines reasoning and answer tokens in
`completion_tokens`; it exposes reasoning text but not a reliable separate reasoning-token count.
Its probabilistic speculative decoder is not bitwise deterministic even with a fixed seed, so raw
generation capture and deterministic downstream replay are distinct requirements.

DeepSeek repair uses exactly one second response if the initial response yields fewer than all 16
structurally valid plans. It receives only the original public prompt, original answer and enumerated
pre-outcome validator errors. Its replacement 16-plan response replaces rather than augments the
initial response. DeepSeek constrained uses the frozen strict schema and no repair. The complete
16-by-4 schema passed a pre-freeze synthetic toy request; it is never silently enabled elsewhere.

`PHI-BUDGET-SENSITIVITY` is deliberately narrower: exact historical model revision, 4-bit engine,
prompt semantics, primitives, worlds, three slots, 16 plans per slot, 48 representation attempts,
interventions, J0-J5 and hidden-information boundaries remain unchanged. Only the predeclared
completion cap changes from 700 to 2,048; repair and constrained decoding remain off. This is not
compute-matched. It tests whether the historical C_self conclusion is sensitive to an unusually
tight limit: all 1,500 archived phase-one calls reached 700 tokens and visibly truncated JSON. The
largest archived prompt plus 2,048 tokens stays 861 tokens below the unchanged 4,096 context limit.

Phi interface sensitivities separately test strict schema at 700 tokens and exactly one
structural-validator repair at 700 tokens. Neither replaces the historical result. The same-revision
precision sensitivity uses runtime BitsAndBytes 8-bit on the frozen Transformers wrapper. Pure-GPU
BF16 does not fit a 24-GB RTX 4090; CPU-offload BF16 served at only about 1.33 token/s and is not
feasible at confirmatory scale. The 8-bit path is feasible, but it also changes serving engine, so
any difference is an engine-plus-precision sensitivity rather than a pure precision effect.

## Worlds, opportunity and information

All runs reuse the exact frozen sets: AJ jump seeds 10000–10049 across eight families; AJ no-jump
seeds 20000–20024; CJ known-family jump seeds 30000–30049; CJ known-family no-jump seeds
50000–50024; held-out triadic-reification jump seeds 40000–40099; and its no-jump seeds
60000–60099. Operational configs are deterministic derivatives of the historical JSON files and are
hashed in `experiments/nmi_extension_v1/configs/config_manifest.json`.

Every C_self treatment retains three final slots, 16 proposed plans of exactly four primitives per
slot, 48 representation attempts per world and one prospective intervention per retained candidate.
No treatment sees hidden intervention or falsification outcomes before commitment. Historical
deterministic fitting, ranking, retention, intervention choice, simulator and J0-J5 thresholds remain
unchanged. A repair response replaces the original opportunity; it does not add candidates.

## Failures, attrition and compute

Each request stores the exact request JSON, raw response JSON, answer, reasoning text, all exposed
usage fields, latency, finish/stop reason, fingerprint and transport-attempt count. Two identical-
payload transport retries are allowed. Malformed, empty or scientifically unsuccessful generations
are never rerun. If transport retries exhaust, the shard aborts and its incomplete tree is retained;
after verified infrastructure recovery only one complete shard restart is allowed. The first complete
attempt is analyzed. A second terminal failure is reported as incomplete.

Descriptive plan/candidate attrition is reported at request return, non-empty answer, JSON parse,
schema, operation-name, argument/type, executable, representation-construction, J0 and J1–J5.
Candidate and plan rows are not independent replicates. Compute tables separately report LLM calls,
transport attempts, prompts, reasoning where exposed, answers, total tokens, attempted/valid plans,
constructed representations, primitive evaluations, fitter and simulator calls, final slots,
interventions, latency and runtime failures. Equal calls, equal opportunities, equal operations,
equal tokens and equal wall-clock are never conflated.

## Outcomes and statistics

The inferential unit is the world. Primary effects are paired world-level JSR differences on jump
worlds and exact false-jump counts on controls. Secondary outcomes are valid-plan rate, family-level
effects, attrition, completion-cap rate and compute. Confidence intervals use a family-stratified
paired bootstrap with 10,000 resamples, seed 730000001 and percentile 95% bounds. If inferential
P-values are shown, two-sided exact McNemar tests receive Holm correction within the AJ-P0 and
CJ-C_self contrast families. Exact counts and effect sizes remain primary.

Predeclared comparisons are DeepSeek matched versus historical Phi-4; DeepSeek native versus
matched; DeepSeek repair and constrained versus native; each Phi budget/constrained/repair
sensitivity versus historical Phi-4; and Phi 8-bit versus historical 4-bit. Known-family and held-out
effects are shown separately before any aggregate. World-level reliability is distinguished from the
much smaller number of structural-family units.

## Replay and reporting

Captured artifacts must deterministically reconstruct parsing, candidate representations, ancestry,
fits, intervention commitments and all gates without another model call. Every config and result is
SHA256 hashed; expected rows, world seeds, split/config hashes and model-condition identifiers are
checked. No success, null, malformed output or contradiction may be silently excluded.

The precommitted interpretation matrix is in `docs/nmi_extension_interpretation_matrix.md`. No
manuscript conclusion or result figure is updated until all shards are frozen and replay-audited.
Optional new-family work is not part of this protocol because designing families after seeing AJ5/CJ5
would not constitute independent external validation; it will be specified as future work unless a
separately frozen, genuinely defensible study is possible.

