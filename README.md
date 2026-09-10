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

The current AIJ manuscript is [AIJ_MANUSCRIPT.md](manuscript/AIJ_MANUSCRIPT.md), with [supplementary methods](manuscript/AIJ_SUPPLEMENTARY_METHODS.md) and a [review PDF](output/pdf/AIJ_manuscript_and_supplement.pdf). It was submitted to *Artificial Intelligence* on 10 September 2026 as `ARTINT-S-26-02213`; post-upload verification is recorded in [`docs/publication/AIJ_EDITORIAL_INTEGRATION.md`](docs/publication/AIJ_EDITORIAL_INTEGRATION.md). Historical NMI material and experiment identifiers are retained for traceability. See also `reports/compositional-representation-jump-final.md`, `experiments/nmi_fair_interface_v1/` and `experiments/nmi_realizer_audit_v1/`.

### Evidence-record example

[Schema version 1.0.0](schemas/aij-evidence-record-v1.schema.json) and the [real C3 record](manuscript/AIJ_EVIDENCE_RECORD_EXAMPLE.json) distinguish runtime records, code-inspected transformations and offline reconstruction. Original commitment timestamps and digests were not retained; reconstructed values are not presented as historical events. Origin records alone do not certify scientific novelty.

Install the development extra (`pip install -e '.[dev]'`), then run:

```bash
python scripts/build_aij_evidence_record.py
python scripts/validate_aij_evidence_record.py --reproduce
```

Generation and reproduction require the raw held-out call ledger from the frozen evidence release. For exact versions, pair code tag `aij-review-package-v1` with data release `nmi-github-submission-v4` using the [clean-environment reproduction instructions](docs/publication/AIJ_REPRODUCTION.md). Omitting `--reproduce` checks record structure only. Neither command makes model calls. [Revision checks and post-upload status](reports/AIJ_SUBMISSION_READINESS.md) are recorded separately.

## Licensing and citation

Original software is available under Apache-2.0. Original synthetic research data and derived artifacts are available under CC BY 4.0. Manuscript and publication materials remain all rights reserved pending journal publication; third-party material and raw model outputs retain their applicable terms. See `LICENSE_SCOPE.md` for exact path-level scope and `CITATION.cff` for citation metadata.
