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

The preregistered confirmatory study is complete. The frozen decision tree returns **AJ5 — representation-mutation advantage**: B4 and B5 each reached 35.5% JSR versus 0–0.25% for B0–B3, with 0/200 false jumps in every condition. P0/P1/P2 were 0%, 35.5%, and 100%. The diversity archive and falsifier added no measured benefit, and there was no held-out structural family, so AJ6 is explicitly unavailable. See `reports/abductive-jump-final.md` and the append-only `research-ledger.md`.
