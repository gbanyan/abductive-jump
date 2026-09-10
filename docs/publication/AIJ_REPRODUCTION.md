# AIJ code and historical data pairing

The baseline code package is the Git tag [`aij-review-package-v1`](https://github.com/gbanyan/abductive-jump/tree/aij-review-package-v1). It contains evidence-record schema/adapter/validator version 1.0.0, manuscript utilities and the interface/metadata audit. The separate, unchanged data release is [`nmi-github-submission-v4`](https://github.com/gbanyan/abductive-jump/releases/tag/nmi-github-submission-v4).

Do not unpack the complete historical archive over the newer code checkout: that would replace the code with an older revision. The commands below extract only three raw call ledgers. All other inputs required by these audits are already tracked at the code tag.

The 10 September 2026 section-review revision retains these evidence utilities and historical data. Its editorial changes and additional descriptive audit checks are recorded in `reports/AIJ_SECTION_REVIEW_RESOLUTION.md`; they are not part of the existing baseline tag. The current PDF is bound to its actual local sources by `reports/AIJ_PDF_BUILD_MANIFEST.json`.

## Clean environment

Requires Git, curl, tar, shasum and uv. Use a new directory; no GPU, model server or API credentials are needed. The locked environment uses Python 3.13 and the versions in `uv.lock`.

```bash
git clone --branch aij-review-package-v1 --single-branch https://github.com/gbanyan/abductive-jump.git aij-reproduce
cd aij-reproduce
git rev-parse HEAD
uv sync --frozen --extra dev --python 3.13
curl --fail --location --output nmi-preservation-archive-9ebf0dc548a5.tar.gz https://github.com/gbanyan/abductive-jump/releases/download/nmi-github-submission-v4/nmi-preservation-archive-9ebf0dc548a5.tar.gz
curl --fail --location --output nmi-preservation-archive-9ebf0dc548a5.tar.gz.sha256 https://github.com/gbanyan/abductive-jump/releases/download/nmi-github-submission-v4/nmi-preservation-archive-9ebf0dc548a5.tar.gz.sha256
shasum -a 256 -c nmi-preservation-archive-9ebf0dc548a5.tar.gz.sha256
.venv/bin/python scripts/build_nmi_reviewer_archive.py --verify nmi-preservation-archive-9ebf0dc548a5.tar.gz
tar -xzf nmi-preservation-archive-9ebf0dc548a5.tar.gz --strip-components=1 novelty-seeking-agent-9ebf0dc548a5/artifacts/compositional/confirmatory-heldout/llm_calls.jsonl novelty-seeking-agent-9ebf0dc548a5/artifacts/confirmatory/primary-jump/llm_calls.jsonl novelty-seeking-agent-9ebf0dc548a5/artifacts/confirmatory/primary-control/llm_calls.jsonl
.venv/bin/python scripts/validate_aij_evidence_record.py --reproduce
.venv/bin/python scripts/build_aij_evidence_record.py --output rebuilt-evidence-record.json
.venv/bin/python scripts/validate_aij_evidence_record.py rebuilt-evidence-record.json --reproduce
cmp manuscript/AIJ_EVIDENCE_RECORD_EXAMPLE.json rebuilt-evidence-record.json
.venv/bin/python scripts/audit_aij_contracts.py
.venv/bin/pytest tests/test_aij_evidence_record.py tests/test_aij_contracts.py
```

Expected archive SHA-256: `a1d82e0e186f7da2714e4cf3b62f637a116b6c2ca53e069c908968072efc827a`. Archive verification checks all 675 manifest files. This is the preservation archive, not the anonymized asset, which has a different digest.

## Expected evidence

- The committed C3 example and the newly generated file are byte-identical. `--reproduce` checks source hashes, the reconstructed theory and gates, and the entire record; omitting it checks structure only.
- Original commitment timestamp and digest stay unavailable. Recomputed commitments are post-hoc evidence, not authenticated historical events.
- B1: all 1,800 final representation hashes match execution of archived model mutation plans, including the historical fallback behavior. Its 1,800 phase-one prompts use an operation contract, not B0's direct-graph contract.
- Variable names: across 600 AJ5 and 800 CJ5 archived worlds, every evaluator-allowed name is already present in public observations; no hidden-only name is introduced by falsification.

The commands verify internal traceability and the stated metadata boundary. They do not call models, estimate new success rates, authenticate missing historical timestamps or establish external replication. PDF rendering is a separate publication workflow; its inputs are bound in `reports/AIJ_PDF_BUILD_MANIFEST.json`.
