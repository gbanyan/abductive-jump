# NMI extension v1 protocol amendment 001

This outcome-blind amendment corrects a temperature omission in the prose summary of the frozen
protocol. It does not change any operational config or code.

The machine-readable configs contain both `generation.temperature = 0.2` and the historical
`sample_temperature = 0.7`. The frozen call path maps P0 to `B1_SAMPLE_MATCHED`, for which
`primary_experiment._run_slot` replaces the effective generation temperature with
`sample_temperature`. The effective temperatures are therefore:

| Condition | Effective temperature |
|---|---:|
| P0_LLM | 0.7 |
| P1_EXTERNAL | 0.2 |
| P2_ORACLE | 0.2 |
| C_SELF_LLM_COMPOSITION | 0.2 |

The original protocol's statement that matched and native use temperature 0.2 is correct for
C_self and P1/P2 but incomplete for P0. P0 remains matched to its historical interface at 0.7.

At amendment authorship, extension C_self shards had started, but no DeepSeek or Phi8 factorial
shard—and therefore no affected P0/P1/P2 request—had started. No result was consulted to make this
correction. Factorial execution remains locked until this amendment receives its own pushed commit
and remote annotated tag. The original freeze tag remains immutable.

