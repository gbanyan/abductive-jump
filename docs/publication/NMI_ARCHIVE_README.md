# NMI reviewer-deposit archive

`scripts/build_nmi_reviewer_archive.py` creates an upload-ready archive from a clean publication commit. It combines:

- every tracked repository file at `HEAD`;
- ten historical AJ5/CJ5 confirmatory `llm_calls.jsonl` ledgers excluded from Git because of size;
- the six completed, superseded broad-extension shards;
- two untracked partial-run directories;
- the tracked infrastructure-terminated partial attempt.

The archive excludes model weights. An internal `ARCHIVE_MANIFEST.json` records the release commit, provenance, byte size and SHA-256 digest of every member. The builder also emits a SHA-256 digest for the compressed archive.

From a clean publication commit:

```bash
rtk proxy .venv/bin/python scripts/build_nmi_reviewer_archive.py
rtk proxy .venv/bin/python scripts/build_nmi_reviewer_archive.py --verify output/archive/nmi-reviewer-deposit-<commit>.tar.gz
```

The verification command streams every member from the compressed package and checks its size and digest against the internal manifest. Before submission, upload the verified archive to an anonymized reviewer-accessible deposit and a DOI-minting repository, record the accession and DOI in the manuscript, and retain the archive-level SHA-256 in the release notes. Creating the local package does not itself mint a DOI.
