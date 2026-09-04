# NMI reviewer-deposit archive

`scripts/build_nmi_reviewer_archive.py` creates upload-ready preservation and anonymous-review archives from a clean publication commit. Each combines:

- every tracked repository file at `HEAD`;
- ten historical AJ5/CJ5 confirmatory `llm_calls.jsonl` ledgers excluded from Git because of size;
- the six completed, superseded broad-extension shards;
- two untracked partial-run directories;
- the tracked infrastructure-terminated partial attempt.

The archive excludes model weights. An internal `ARCHIVE_MANIFEST.json` records the release commit, provenance, byte size and SHA-256 digest of every member. The builder also emits a SHA-256 digest for the compressed archive.

The preservation archive retains the original files and validation hashes for DOI deposition. The anonymous-review mode replaces local account paths, repository email addresses and private LAN endpoints in a fixed, audited set of text files. Its manifest records both source and transformed hashes and the number of replacements. It does not modify source artifacts in the workspace.

From a clean publication commit:

```bash
rtk proxy .venv/bin/python scripts/build_nmi_reviewer_archive.py
rtk proxy .venv/bin/python scripts/build_nmi_reviewer_archive.py --anonymized
rtk proxy .venv/bin/python scripts/build_nmi_reviewer_archive.py --verify output/archive/nmi-preservation-archive-<commit>.tar.gz
rtk proxy .venv/bin/python scripts/build_nmi_reviewer_archive.py --verify output/archive/nmi-anonymous-reviewer-deposit-<commit>.tar.gz
```

The verification command streams every member from the compressed package and checks its size and digest against the internal manifest. Before submission, upload the anonymous copy to a reviewer-accessible deposit and the preservation copy to a DOI-minting repository, record the accession and DOI in the manuscript, and retain both archive-level SHA-256 values in the release notes. Creating the local packages does not itself mint a DOI.
