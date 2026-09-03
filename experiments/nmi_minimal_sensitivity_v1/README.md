# Minimal targeted NMI sensitivity extension

This namespace contains a targeted sensitivity analysis and does not replace the original Phi-4 4-bit confirmatory study. Historical artifacts are preserved at commit `ae1ede683fdef09f2bf60f6e1052b60394ad6cf8`, tag `nmi-phi4-frozen-2026-09` and branch `nmi-phi4-frozen-archive-2026-09`.

## Frozen populations

- Fixed paired panel: 96 existing confirmatory worlds, comprising the same 12 outcome-blind selected seeds in each of eight known families.
- Positive-control panel: 40 of those worlds, comprising the same five predeclared seeds per family.
- Original confirmatory population: n=400; unchanged and reported separately.

The exact world IDs, selection salt and source hashes are in `panel_manifest.json`. The protocol and operational amendment are in `protocol.json` and `protocol_amendment_001.json`.

## Allowed run matrix

1. Phi-4 8-bit C_self, n=96.
2. DeepSeek matched C_self with `reasoning_effort=none`, n=96.
3. DeepSeek native C_self with `reasoning_effort=max`, n=96.
4. DeepSeek supplied-representation positive control, n=40.
5. Phi-4 8-bit C_self with one structural-validator repair, n=96; enabled because the frozen historical pre-executable failure rate exceeded 25%.

No other model, budget, decoding, family or factorial condition belongs to this extension.

## Completion and analysis

Each run directory must contain `validation.json` with `status=complete_verified`. Partial raw calls must not be interpreted. After all five validations exist, run the zero-model-call postprocessing sequence:

```bash
rtk proxy env PYTHONPATH=src .venv/bin/python scripts/run_nmi_minimal_postprocessing.py --root .
```

This command performs deterministic replay first, rejects any mismatch, then writes world-level summaries, Wilson intervals, paired transitions, per-family descriptions, cumulative attrition, compute accounting, figures and a hash manifest. Candidate-level significance testing is prohibited.
