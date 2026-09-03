# Minimal targeted sensitivity extension

This extension is a targeted sensitivity analysis. The original frozen Phi-4 4-bit n=400 confirmatory study remains unchanged. The matched comparisons below use the same fixed 96 historical worlds; the supplied-representation positive control uses a predeclared balanced n=40 subset. The 2,048-token Phi-4 condition was separately prospectively frozen and changes only the completion cap.

## World-level results

| Condition | Population | Successes | JSR | Wilson 95% interval |
|---|---|---:|---:|---:|
| Phi-4 4-bit historical slice | original confirmatory n=400, fixed paired subset shown | 0/96 | 0.0% | 0.0%–3.8% |
| Phi-4 4-bit 2,048-token budget | previously frozen n=400 budget sensitivity, fixed paired subset shown | 0/96 | 0.0% | 0.0%–3.8% |
| Phi-4 8-bit C_self | new fixed n=96 sensitivity panel | 0/96 | 0.0% | 0.0%–3.8% |
| DeepSeek matched C_self | new fixed n=96 sensitivity panel | 0/96 | 0.0% | 0.0%–3.8% |
| DeepSeek native C_self | new fixed n=96 sensitivity panel | 0/96 | 0.0% | 0.0%–3.8% |
| Phi-4 8-bit one repair | new fixed n=96 sensitivity panel | 0/96 | 0.0% | 0.0%–3.8% |
| DeepSeek supplied representation | new balanced n=40 positive-control subset | 3/40 | 7.5% | 2.6%–19.9% |

## Paired world-level differences

| Reference | Comparison | Both fail | Both succeed | Comparison only | Reference only | Difference |
|---|---|---:|---:|---:|---:|---:|
| Phi-4 4-bit historical slice | Phi-4 4-bit 2,048-token budget | 96 | 0 | 0 | 0 | +0.000 |
| Phi-4 4-bit historical slice | Phi-4 8-bit C_self | 96 | 0 | 0 | 0 | +0.000 |
| Phi-4 4-bit historical slice | DeepSeek matched C_self | 96 | 0 | 0 | 0 | +0.000 |
| DeepSeek matched C_self | DeepSeek native C_self | 96 | 0 | 0 | 0 | +0.000 |
| Phi-4 8-bit C_self | Phi-4 8-bit one repair | 96 | 0 | 0 | 0 | +0.000 |

## Full Phi-4 completion-budget sensitivity

| Condition | Population | Successes | JSR | Wilson 95% interval |
|---|---|---:|---:|---:|
| historical_phi4_4bit_cself_full | original confirmatory n=400 | 0/400 | 0.0% | 0.0%–1.0% |
| phi4_4bit_budget_cself_full | budget sensitivity n=400 | 0/400 | 0.0% | 0.0%–1.0% |
| historical_phi4_4bit_cself_heldout | original held-out n=100 | 0/100 | 0.0% | 0.0%–3.7% |
| phi4_4bit_budget_cself_heldout | budget sensitivity held-out n=100 | 0/100 | 0.0% | 0.0%–3.7% |

| Reference | Comparison | Both fail | Both succeed | Comparison only | Reference only | Difference |
|---|---|---:|---:|---:|---:|---:|
| historical_phi4_4bit_cself_full | phi4_4bit_budget_cself_full | 400 | 0 | 0 | 0 | +0.000 |
| historical_phi4_4bit_cself_heldout | phi4_4bit_budget_cself_heldout | 100 | 0 | 0 | 0 | +0.000 |

## Compute ledger

| Condition | Calls | Prompt tokens | Completion tokens | Reasoning text calls | Latency (s) |
|---|---:|---:|---:|---:|---:|
| Phi-4 4-bit 2,048-token budget | 576 | 704376 | 528976 | 0 | 40446.1 |
| Phi-4 8-bit C_self | 576 | 704376 | 231773 | 0 | 13971.8 |
| DeepSeek matched C_self | 576 | 786804 | 237792 | 0 | 10636.3 |
| DeepSeek native C_self | 576 | 839796 | 2249518 | 576 | 156547.1 |
| Phi-4 8-bit one repair | 864 | 1254663 | 433373 | 0 | 26462.2 |
| DeepSeek supplied representation | 120 | 183891 | 485312 | 120 | 38836.1 |

No candidate-level significance tests were performed. DeepSeek native and the 2,048-token Phi-4 condition are not compute-matched to historical Phi-4. Phi-4 8-bit differs from the historical run jointly in precision and serving engine. Historical `parse_valid` follows the registered legacy object-extraction parser; strict whole-response JSON validity was 0/1,200.
