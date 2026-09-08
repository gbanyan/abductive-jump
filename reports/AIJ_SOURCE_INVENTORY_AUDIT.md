# AIJ source inventory and preservation audit

Audit date: 8 September 2026. Read-only checks; no model inference, new experimental population, or historical artifact rewrite.

## Preserved evidence

The public GitHub release `nmi-github-submission-v4` was checked through the GitHub release API. It is public, non-draft and dated 5 September 2026. Its historical name identifies the evidence package, not this AIJ manuscript revision.

- Preservation asset: `nmi-preservation-archive-9ebf0dc548a5.tar.gz`.
- Size recorded by the public release: 87,702,109 bytes.
- SHA-256 independently recomputed locally: `a1d82e0e186f7da2714e4cf3b62f637a116b6c2ca53e069c908968072efc827a`, matching the release digest.
- `scripts/build_nmi_reviewer_archive.py --verify` checked all **675** manifest-listed files for presence, byte count and SHA-256; result `complete_verified`.
- Embedded release commit: `9ebf0dc548a5ba909dd4c1233835c66625e8a756`.
- Verification does not rerun the archive builder or replace the published asset. No DOI is asserted.

Public source: https://github.com/gbanyan/abductive-jump/releases/tag/nmi-github-submission-v4.

## Numerical and protocol coverage

`audit_aij_numbers.py` checks primary results, gates, world denominators, replay coverage, paired outcomes, completion counts, family cells, realizer masks and binding changes. It also reads six superseded completed shards directly, counts the three disclosed partial call ledgers, checks the excluded 31-call pilot and three four-record timeout-only shards, and resolves every printed supplementary freeze commit in the local Git object database. Resolving an object is not independent timestamp verification. Exact values and input hashes appear in `AIJ_NUMERICAL_AUDIT.md` and `AIJ_NUMERICAL_CHECKS.json`.

Supplement S1-S10 protocol quantities were checked against frozen configurations, generic-primitive manifest, historical summaries and the evaluator/statistical code. S11-S17 operational quantities are tied to `EXTENSION_TERMINATED.json`, superseded Parquet tables, excluded JSONL ledgers, runtime manifests and the preserved initial/corrected fair-interface replay reports. The 576 initial verifier mismatches are metadata defects, not changed scientific outcomes. The final correction checks four shard manifests and preserves the initial report.

The 244 automated assertions are not a claim that every numeral is an independent statistical estimate. Gate indices, section labels, citation numbers, years, model names and commit identifiers have their own semantic checks. Percentages are rounded arithmetic from recorded denominators. The worked example reconstructs one already archived seed; it adds no experimental observation.

## Scientific-source boundaries

The evidence package includes raw historical call ledgers and superseded runs omitted from ordinary Git tracking. The manuscript identifies model weights as external, not redistributed. Source and artifact licenses are scoped by `LICENSE_SCOPE.md`; model weights are not covered by the project's software/data license.

The AIJ manuscript, new figures and editorial audits will be versioned separately from the frozen evidence archive. Existing unrelated working-tree changes and raw run files are not to be staged in the AIJ conversion commit. No claim is made that the old evidence release already contains the AIJ revision.

## Submission items that artifact verification cannot establish

The existence or absence of a separately published Research Square/In Review preprint was not established. Exact-title web search and narrowly scoped Research Square/In Review mailbox searches returned no confirming record; absence of a search result is not proof of absence. Authors must supply the status or identifier before upload. Final author approval, contribution/funding/conflict declarations and current exclusive-submission status require human attestation. Current AIJ author-guide details blocked by publisher access must be checked in the live guide/submission workflow.
