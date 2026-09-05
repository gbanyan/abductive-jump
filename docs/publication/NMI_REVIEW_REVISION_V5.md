# Focused reviewer corrections after v4

No model calls were made. No frozen experiment, raw ledger, gate, or historical statistical field was changed.

## Scientific checks

- `scripts/audit_nmi_control_comparator.py` regenerates the archived control populations and exhaustively checks the selected observational comparator against every intervention/falsification outcome. AJ5: 200 worlds, 1,125 cases; CJ5 known: 200 worlds, 1,125 cases; CJ5 held-out: 100 worlds, 500 cases. Exact mismatches: zero in each population. Population counts are not summed as independent worlds.
- `composition_search.evaluate_candidate` realizes and fits each graph before computing its score. `structured_search` selects three terminal evaluations with `_select_diverse`; manuscript and S8 now state this order.
- AJ5 `analysis._paired_bootstrap` resamples uncentered paired differences. Its archived `p_one_sided` is `(1 + count(delta_bootstrap <= 0)) / 10001`, followed by Holm arithmetic. No null distribution is constructed. Historical values remain unchanged but are described as bootstrap tail proportions, not null-calibrated P values. No replacement significance test was introduced.

## Editorial changes

The main definition now distinguishes structural escape from functional inexpressibility. Abstract prioritizes deterministic field provenance. Figure 4b compares aligned and role/action-blind binding (400/400 vs 347/400; 100/100 vs 100/100; 15/96 vs 8/96). Substitution controls remain in panel d and supplementary tables. Paired policy overlap is not interpreted as equivalence. Figure 3 retained-gain annotation was removed; supplementary values remain. Residual affirmative `registered` terminology was replaced with frozen/prospectively specified terminology.

## Public deposit verification

Downloaded the v4 preservation archive without GitHub authentication into a new temporary directory, verified all 675 file-level checksums, and replayed its supplied-representation control using the previously created isolated Python environment. This is a same-host check, not independent third-party reproduction.

- Archive commit: `9ebf0dc548a5ba909dd4c1233835c66625e8a756`
- Archive SHA-256: `a1d82e0e186f7da2714e4cf3b62f637a116b6c2ca53e069c908968072efc827a`
- Replay: 120 candidate rows, 120 verified, zero mismatches.
- Replayed candidate SHA-256: `ea9fb95f97ec1ff8e9779a2b6357e360d2d3738f1954a62dd4be4ed589f33323`

The manuscript continues to cite v4 as the verified scientific-data snapshot; the editorial revision does not replace those frozen data. The PDF was rebuilt and modified main figures/title inspected. Full existing test suite passed.
