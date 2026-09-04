# NMI fair-interface sensitivity v1

This namespace contains one additional fixed-panel sensitivity condition. It does not modify or
replace the frozen AJ5/CJ5 or minimal-sensitivity results.

The condition uses the same 96 worlds, 29 available generic primitives, three candidate slots,
16 four-step plans per slot and J0-J5 evaluator. Each slot receives two calls to the same served
DeepSeek checkpoint: a reasoning call and a grammar-constrained serialization call. The second
call receives only the first call's own deliberation, the public world and exact parser-level
syntax. It receives no truth, target distance, fitted result, intervention outcome or gate feedback.

The response schema guarantees only JSON structure, plan count, depth, operation vocabulary and
argument keys/types. Dynamic references and scientific usefulness remain model responsibilities.

The protocol and code hashes must be committed and tagged before the formal 96-world run.

Operational amendments 001 and 002 record the family sharding and the switch from concurrent to
sequential shard scheduling after the server's four-active-sequence limit caused transport queue
timeouts. Timeout-only directories contain no returned model responses and are archived under
`operational_pilots/starved_parallel_shards_excluded`; they are excluded from every analysis.
