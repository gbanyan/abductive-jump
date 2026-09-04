# Abductive Jump

A prospective, replayable assay for hypothesis-space expansion and causal component attribution in AI systems. Candidates must leave a frozen language, remain observationally adequate, commit to a discriminating intervention before outcome reveal, outperform the incumbent oracle and survive independent falsification.

The project is executed in the fixed order documented in `research-ledger.md`: deterministic world engine and validation first, model calibration second, preregistration and configuration freeze third, and confirmatory inference only afterward.

## Scientific contract

- Primary verdicts are computed by deterministic evaluators, never by an LLM judge.
- Semantic or lexical novelty is never a jump criterion.
- A validated jump must pass preregistered gates J0–J5.
- Every primary condition is compute matched.
- The incumbent-space oracle is a hard requirement for confirmatory benchmark families.
- Primary inference runs only on `gblinux` (single RTX 4090, frozen 8B–14B model, no fine-tuning).

## Layout

- `docs/` — formal specification, literature audit, and preregistration
- `src/` — typed representation DSL, worlds, oracle, mutations, conditions, and analysis
- `tests/` — deterministic unit and integration tests
- `configs/` — versioned pilot and frozen confirmatory settings
- `artifacts/` — manifests, hashes, and tabular experiment outputs
- `reports/` — validation, calibration, pilot, final, and adversarial-review reports

## Status

The frozen AJ5 and CJ5 studies are complete. Subsequent code-path and counterfactual audits show that CJ5 success is attributable to deterministic typed search and a family-aligned motif realizer, not to model output. A separately frozen interface sensitivity produced validated edits in 15/96 worlds but did not outperform matched random composition. The resulting claim is system-level and methodological: the assay detects prospectively validated structural escape while exposing when successful scientific content is supplied by scaffolding rather than by a language model.

See `manuscript/NMI_MANUSCRIPT.md`, `reports/compositional-representation-jump-final.md`, `experiments/nmi_fair_interface_v1/` and `experiments/nmi_realizer_audit_v1/`.

## Licensing and citation

Original software is available under Apache-2.0. Original synthetic research data and derived artifacts are available under CC BY 4.0. Manuscript and publication materials remain all rights reserved pending journal publication; third-party material and raw model outputs retain their applicable terms. See `LICENSE_SCOPE.md` for exact path-level scope and `CITATION.cff` for citation metadata.
