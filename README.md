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

The original preregistered study is complete and retains **AJ5 — representation-mutation advantage**. Its final compositional generalization/falsification phase also returns **CJ5** under a separate preregistration: structured search composed generic local rewrites with 100% JSR on 400 existing-family and 100 held-out worlds, versus 0% for depth-one rewrites and 13% for matched random primitives. All conditions had 0/300 combined false jumps. The same-vocabulary LLM self-composition control remained at 0%, so the result supports bounded procedural composition of supplied primitives—not autonomous or vocabulary-free theory invention. See `reports/compositional-representation-jump-final.md`, `reports/compositional-representation-jump-reviewer2.md`, and the append-only `research-ledger.md`.
