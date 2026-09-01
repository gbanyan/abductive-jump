# Abductive Jump

A mechanistic study of whether structured external representation mutation helps a frozen language model escape a locally adequate incumbent hypothesis space and reach prospectively validated explanatory models.

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

See `research-ledger.md` for the authoritative chronological record. The confirmatory study must not run until a preregistration commit hash and frozen manifests are recorded.

