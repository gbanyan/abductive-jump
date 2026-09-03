# Historical Phi-4 C_self failure attrition

This is an offline reconstruction from frozen artifacts; it made **zero model calls**.

| Stage | Proposal responses passed | Rate |
|---|---:|---:|
| response_returned | 1200/1200 | 100.0% |
| parse_valid | 1200/1200 | 100.0% |
| schema_valid | 0/1200 | 0.0% |
| operation_valid | 0/1200 | 0.0% |
| argument_type_valid | 0/1200 | 0.0% |
| executable | 0/1200 | 0.0% |
| J1 | 0/1200 | 0.0% |
| J2 | 0/1200 | 0.0% |
| J3 | 0/1200 | 0.0% |
| J4 | 0/1200 | 0.0% |
| J5 | 0/1200 | 0.0% |

All 1,200 responses were non-empty and hit the 700-token completion cap. The registered parser extracted a nested JSON object from every truncated answer, but no response contained a valid outer `plans` schema and none was complete whole-answer JSON. No self-proposed representation reached execution or J1–J5.

The runner's incumbent fallback candidates are excluded from this cascade because they were not representations proposed by C_self.
