# NMI archive privacy audit

Audit date: 5 September 2026.

The full preservation archive was scanned before external deposition for four classes of accidental disclosure: absolute local-account paths, private LAN addresses, email addresses and credential-like assignments. No credential assignment was detected. Thirteen absolute-path occurrences appeared in ten files, eleven private-LAN occurrences appeared in eight files, and a repository email address appeared in two text files. Apparent email matches in the generated PDF were binary-stream false positives and were not treated as visible identifiers.

The archive builder therefore supports two outputs:

- `nmi-preservation-archive-<commit>.tar.gz` retains exact source bytes and is intended for the DOI record;
- `nmi-anonymous-reviewer-deposit-<commit>.tar.gz` replaces local account names, repository email addresses and private LAN endpoints only in the fixed `ANONYMIZE_PATHS` set.

The anonymous archive manifest records each transformed member's original SHA-256, deposited SHA-256, byte size and replacement count. The original workspace and preservation archive remain unchanged. Model weights and access credentials are excluded from both packages. This audit reduces accidental identity and network disclosure but does not replace a human review of the final files before double-anonymous submission.
