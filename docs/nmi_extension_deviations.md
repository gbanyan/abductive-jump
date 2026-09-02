# NMI extension v1 deviations and infrastructure events

This log is append-only after the prospective protocol freeze. Scientific outputs are not used to
decide whether an event is recorded or whether a shard is retained.

## Protocol amendment 001: effective P0 temperature

After the initial protocol tag but before any factorial request, static call-path inspection showed
that P0 inherits the historical `sample_temperature = 0.7` override, while P1, P2 and C_self use
`generation.temperature = 0.2`. No config or code changed. The correction was committed and pushed
as `4ebc679b6dfdec053dc77fe6dd68caa78a2cb4da` and remotely tagged
`nmi-extension-v1-protocol-amendment-001` before factorial unlock. C_self shards already running at
the time were unaffected.

## Phi 8-bit scheduling OOM

An attempt to load the frozen Phi 8-bit server while the Phi 4-bit vLLM container occupied about
23.3 GiB on the single gblinux RTX 4090 failed for insufficient GPU memory. No benchmark request or
result shard began. This is classified as a pre-run scheduling conflict, not a model or scientific
failure. The 8-bit lane is queued until the 4-bit lane releases the GPU; its worlds and configs are
unchanged.

## Phi-budget known-jump attempt 001: executor termination

The first `phi_budget/known_jump` runner was attached to a delegated interactive executor. When that
agent turn ended, the runner and SSH tunnel ended even though the remote model server stayed healthy.
The attempt produced 202 of 2,400 expected call records, no `summary.json` and no transport-error
file. It is preserved without modification under
`experiments/nmi_extension_v1/results/_incomplete/phi_budget/known_jump_attempt_001_executor_session_terminated/`.

Under the frozen whole-shard policy, none of its calls are reused. The one allowed clean restart began
from a new empty canonical output directory through root-owned persistent runner/tunnel sessions.
The incomplete attempt is excluded because it has no complete world/candidate result tables, not
because of output content.

