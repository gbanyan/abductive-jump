# NMI minimal sensitivity protocol amendment 002

Status: outcome-blind analysis integration lock, 3 September 2026.

## Purpose

This amendment incorporates the already completed `PHI-BUDGET-SENSITIVITY`
condition into the minimal targeted sensitivity report without making another
model call. The condition was prospectively frozen at commit `4606413` and tag
`nmi-extension-v1-protocol-freeze`, before its results existed. It retains the
exact historical Phi-4 revision and 4-bit vLLM runtime and changes only the
predeclared completion cap from 700 to 2,048 tokens.

This integration decision was written before opening or analysing any result
from the currently running minimal-sensitivity conditions. It is not described
as a new preregistration or as part of the original AJ5/CJ5 registration.

## Why no rerun is permitted

The known-family result already contains all 400 historical worlds and the
held-out result contains all 100 historical held-out worlds. Both shards are
marked `complete_verified`, have the frozen config hashes, exact expected row
and call counts, immutable artifact hashes and zero transport-error records.
Repeating the same model generation would spend compute without adding an
independent comparison and would create an avoidable selection problem.

## Locked analysis

The primary budget comparison uses the 96-world panel that was selected and
frozen independently for `NMI-MIN-SENS-V1`. The 96 rows are extracted from the
complete 400-world budget shard by exact `(family, world_seed, world_id)` keys.
The full 400-world known-family result is reported separately, and the complete
100-world held-out result is retained as supplementary descriptive evidence.

Reports will include exact counts, Wilson 95% intervals, paired world-level
differences, per-family descriptions, gate attrition and token/latency
accounting. Candidate rows are descriptive only and are not treated as
independent inferential replicates.

## Scientific invariants

Relative to historical Phi-4 C_self, all of the following remain unchanged:

- model repository and exact revision;
- 4-bit quantization and vLLM serving engine;
- prompt semantics and primitive vocabulary;
- worlds and seeds;
- three candidate slots, two calls per slot and 16 plans per slot;
- 48 representation attempts per world and four edits per plan;
- parser and no-repair policy;
- prospective intervention logic and hidden-information boundaries;
- J0--J5 definitions and thresholds.

Only `generation.max_tokens` changes, from 700 to 2,048. The condition is not
compute-matched to the historical run. No result may be discarded or reframed
because it weakens the manuscript narrative.
