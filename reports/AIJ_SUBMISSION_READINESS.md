# AIJ submission readiness

Audit date: 8 September 2026. Target: *Artificial Intelligence*, Regular Paper.

## Verdict: CONDITIONALLY READY

The AIJ scientific/editorial conversion is complete as a reviewable manuscript package. It is **not cleared for journal upload**. Current journal-specific submission specifications and human author attestations remain open. This verdict is not a prediction of acceptance.

The manuscript now concerns representation-space revision, heuristic search and the attribution of executable explanatory content. It does not claim that representation search is new, that LLMs generally cannot revise theories, or that the grammar-constrained model outperforms random composition. No new model experiment or scientific branch was opened.

## Assessment by dimension

| Dimension | Assessment | Evidence and remaining boundary |
|---|---|---|
| AIJ scope fit | READY | Representation languages, constructive induction, reasoning and heuristic search are central; Regular Paper remains the intended category |
| Novelty | CONDITIONALLY READY | Precise contribution is the implemented prospective scored-artifact contract joined to provenance, replay interventions and supplied-knowledge inventory. Individual ingredients and several combinations have strong predecessors; contribution sufficiency remains an editorial risk |
| Relation to classic AI | READY | Independent related-work section covers abduction, belief/theory revision, predicate invention, constructive induction, restructuring and meta-interpretive learning; no first-ever claim |
| Formal clarity | READY within stated scope | A0, finite P0, selected observation-optimal comparator, T=(R,f), validity prerequisite, commitment and J0-J5 are separated. Structural non-membership is not functional inexpressibility |
| Experimental validity | READY for bounded claims | Frozen results retained; world is the replicate; AJ5 tail quantities are not calibrated P values; structural controls and complete-policy contrasts are identified |
| Component attribution | READY | Final-field provenance, overwrite, inference-free replay and fixed-slot realizer interventions distinguish authorship from score dependence. Model-authored expression use is separated from graph authorship |
| Generality | CONDITIONALLY READY | Demonstration is synthetic/noiseless and family-aligned. The record/application procedure is portable by design, but external portability and general discovery performance are untested |
| Reproducibility | READY for internal traceability | 244 numerical/configuration checks pass; archived replay coverage retained; public preservation asset checksum matches and all 675 manifest files verify. This is not independent experimental replication |
| Writing | READY for author review | Question-led results, separate classical/modern positioning, consolidated limitations, paragraph-level qualifier inventory, 220-word abstract, seven main figures and six main tables |
| Citation integrity | READY with documented access limits | All 42 references have primary-source audit entries; all are cited and all citation numbers resolve. Older books and some publisher-blocked sources were checked through primary metadata/author versions. Final journal reference formatting remains unverified |
| Data/code availability | READY | Public repository/release verified; raw ledgers, superseded records, manifests and replay utility retained. AIJ revision is separate from the historical evidence release; no DOI or redistributed model weights claimed |
| AI disclosure | CONDITIONALLY READY | Substantive ChatGPT/Codex roles are disclosed, including literature, code and figures. Both authors must personally review/approve and attest responsibility before the final declaration is signed |

## Upload holds

1. **Current official guide/portal.** Live ScienceDirect guide retrieval was blocked (HTTP 403/access errors). Length, source-file format, reference style/order, keyword count, Highlights, graphical abstract, supplementary-file constraints and the live submission endpoint need current official confirmation. The audit does not substitute a 2023 guide or another journal's rules. Provide the current guide or verify these items in the portal before upload.
2. **Separately hosted preprint status.** Public repository availability is established; a Research Square/In Review posting is not established or excluded. The corresponding author must confirm whether a separate preprint exists and provide its URL/identifier if it does. The cover letter contains a clearly marked author-side completion check.
3. **Author attestation.** Both authors must approve the AIJ revision and reconfirm contributions, funding, conflicts, exclusive-submission status and the substantive AI-use declaration. Agent-assisted source checking is not a substitute for human acceptance of scholarly responsibility.

These holds do not require new experiments. No publication-critical numerical contradiction was found that would justify opening a new scientific branch. No journal submission, editorial message or account action was taken.

## Deliverables and verification

- `manuscript/AIJ_MANUSCRIPT.md`: rewritten title, abstract, introduction, related work, formal framework, question-led results, discussion, limitations and declarations.
- `manuscript/AIJ_SUPPLEMENTARY_METHODS.md`: S1-S18, retaining frozen methods, attrition, operational exclusions and artifact identifiers.
- `output/pdf/AIJ_manuscript_and_supplement.pdf`: 32-page A4 review PDF, with all seven figures, six main tables, 18 supplementary sections and 42 references.
- `manuscript/AIJ_COVER_LETTER.md` and separate AI/data/code statements: ready for the author checks above, not an assertion of completed human approval.
- `manuscript/AIJ_PROVENANCE_RECORD_TEMPLATE.json`: parse-valid record template, not a validated JSON Schema or new empirical result.
- `docs/publication/AIJ_*`: scientific freeze, author-guide audit, 12-article structural-style analysis, title/storyboard and claim matrix.
- `reports/AIJ_*`: novelty attack, two adversarial reviewer simulations, associate-editor simulation, citation/numerical/claim audits, source inventory and PDF QA/build manifests. Simulations are drafting aids, not independent reviews.

The style sample includes author/pre-proof versions and one partially accessible current article; exact portal-level Regular Paper labels were not consistently exposed. This supports structural editorial choices, not a claim that all production metadata were verified. Twelve title candidates were considered in the storyboard. No `.tex` source was created because the existing project has no LaTeX manuscript workflow. Highlights were not created because a current AIJ requirement could not be verified.

The PDF workflow used rendered-page inspection as well as text/bounds checks. All 32 pages were inspected; corrections included a diagram's overflowing label, table column widths, orphaned headings, and equation/lead-in placement. Final automated QA reports zero page-bounds or unmapped-glyph failures. The build manifest binds the PDF to its manuscript, supplement, figures and builder hashes. Humanizer-zh-tw guided removal of repetitive defensive prose while retaining protected numbers, references and disclosure; PDF skill guided render-and-verify QA.

Verification commands (repository environment):

```text
rtk proxy .venv/bin/python scripts/audit_aij_claims.py
rtk proxy .venv/bin/python scripts/audit_aij_numbers.py
rtk proxy .venv/bin/python scripts/build_aij_figures.py
rtk proxy .venv/bin/python scripts/build_aij_manuscript.py
rtk proxy pdftoppm -scale-to 1500 -png output/pdf/AIJ_manuscript_and_supplement.pdf tmp/pdfs/aij/page
rtk proxy .venv/bin/python scripts/qa_aij_pdf.py
rtk proxy python3 scripts/build_nmi_reviewer_archive.py --verify output/archive/nmi-preservation-archive-9ebf0dc548a5.tar.gz
```

The archive must be downloaded from the public evidence release if absent locally. The numerical audit also checks excluded raw ledgers supplied by that preservation archive. No command above requests model inference.

## Version-control scope

The AIJ conversion is a separate commit on `nmi-minimal-targeted-sensitivity-v1`. Existing modified NMI manuscript/PDF/builder files and unrelated raw experiment outputs are excluded. The requested `docs/publication/NMI_REJECTION_LESSON.md` remains local-only because it was designated internal; it is not included in the public push. The evidence release is not rebuilt or replaced. This readiness report's containing commit identifies the manuscript revision; remote push verification is reported in the handoff.

## Two-sentence scientific center

We introduce a prospective executable assay for bounded hypothesis-space expansion that distinguishes structural representational change from retrospective fit. Applying field-level provenance and replay to hybrid LLM-symbolic systems shows that end-to-end discovery scores can misattribute both successful explanatory content and apparent model failure when deterministic scaffolds or interfaces mediate what reaches the evaluator.
