# AIJ submission status and readiness audit

Audit date: 10 September 2026. Target: *Artificial Intelligence*, Regular Paper.

## Verdict: SUBMITTED — AWAITING EDITORIAL ASSESSMENT

The AIJ manuscript was submitted through Editorial Manager on 10 September 2026 under manuscript number `ARTINT-S-26-02213`. The rebuilt verification PDF was reviewed after upload. This status records successful system submission and does not imply peer-review assignment or acceptance.

The manuscript now concerns representation-space revision, heuristic search and the attribution of executable explanatory content. It does not claim that representation search is new, that LLMs generally cannot revise theories, or that the grammar-constrained model outperforms random composition. No new model experiment or scientific branch was opened.

## Assessment by dimension

| Dimension | Assessment | Evidence and remaining boundary |
|---|---|---|
| AIJ scope fit | READY | Representation languages, constructive induction, reasoning and heuristic search are central; Regular Paper remains the intended category |
| Novelty | CONDITIONALLY READY | Precise contribution is the implemented prospective scored-artifact contract joined to provenance, replay interventions and supplied-knowledge inventory. Individual ingredients and several combinations have strong predecessors; contribution sufficiency remains an editorial risk |
| Relation to classic AI | READY | Independent related-work section covers abduction, belief/theory revision, predicate invention, constructive induction, restructuring and meta-interpretive learning; no first-ever claim |
| Formal clarity | READY within stated scope | A0, finite P0, selected observation-optimal comparator, T=(R,f), commitment and J0-J5 are separated. S19 lists the implemented V(T) checks, source positions and nonchecks; no semantic-equivalence validator is implied |
| Experimental validity | READY for bounded claims | Frozen results retained; world is the replicate; AJ5 tail quantities are not calibrated P values; structural controls and complete-policy contrasts are identified |
| Component attribution | READY | Versioned schema, trace adapter, validator and real C3 record distinguish runtime evidence, code inspection and reconstruction. The original theory hash and all six gates match; deletion changes the explanation-dependent hash but not gates. Original commitment timestamp/digest remain unavailable |
| Generality | CONDITIONALLY READY | Demonstration is synthetic/noiseless and family-aligned. The record/application procedure is portable by design, but external portability and general discovery performance are untested |
| Reproducibility | READY for internal traceability | 265 numerical/configuration checks pass; archived replay coverage retained; public preservation asset checksum matches and all 675 manifest files verify. This is not independent experimental replication |
| Writing | READY for author review | Question-led results, separate classical/modern positioning, consolidated limitations, paragraph-level qualifier inventory, 214-word abstract, seven main figures and six main tables |
| Citation integrity | READY with documented access limits | All 45 references have primary-source audit entries; all are cited and all citation numbers resolve. Older books and some publisher-blocked sources were checked through primary metadata/author versions. Final journal reference formatting remains unverified |
| Data/code availability | READY | Public repository/release verified; raw ledgers, superseded records, manifests and replay utility retained. AIJ revision is separate from the historical evidence release; no DOI or redistributed model weights claimed |
| AI disclosure | CONDITIONALLY READY | Substantive ChatGPT/Codex roles are disclosed, including literature, code and figures; Claude Fable 5.1 section-level review is also disclosed. Both authors must personally review/approve and attest responsibility before the final declaration is signed |

## Submission-stage notes

1. **Current official guide/portal.** Live ScienceDirect guide retrieval was blocked (HTTP 403/access errors), so this audit does not claim independent verification of every production requirement. The submission-system controls were used for the submitted package; future requests from the journal remain authoritative.
2. **Separately hosted preprint status.** The cover letter states that no separate preprint or public-manuscript posting is claimed. Repository availability is documented separately and is not treated as a journal preprint.
3. **Author attestation.** The human authors remain responsible for the submitted manuscript, contributions, funding, conflicts, exclusive-submission status and substantive AI-use declaration. This report records the submission; it does not replace their scholarly responsibility.

These holds do not require new experiments. No publication-critical numerical contradiction was found that would justify opening a new scientific branch. No journal submission, editorial message or account action was taken.

## Deliverables and verification

- `manuscript/AIJ_MANUSCRIPT.md`: rewritten title, abstract, introduction, related work, formal framework, question-led results, discussion, limitations and declarations.
- `manuscript/AIJ_SUPPLEMENTARY_METHODS.md`: S1-S20, retaining frozen methods and adding implemented-validity checks and a traceable record example.
- `output/pdf/AIJ_manuscript_and_supplement.pdf`: 43-page A4 review PDF, 11 pt narrative body, seven figures, six main tables, 20 supplementary sections and 45 references. Main text/end matter/references occupy pages 1-26; supplement occupies pages 27-43.
- `manuscript/AIJ_COVER_LETTER.md` and separate AI/data/code statements: ready for the author checks above, not an assertion of completed human approval.
- `schemas/aij-evidence-record-v1.schema.json`, `scripts/build_aij_evidence_record.py`, `scripts/validate_aij_evidence_record.py` and `manuscript/AIJ_EVIDENCE_RECORD_EXAMPLE.json`: version 1.0.0 schema/adapter/validator and actual archival-plus-reconstructed record. The earlier template remains explicitly a legacy unfilled checklist.
- `docs/publication/AIJ_*`: scientific freeze, author-guide audit, 12-article structural-style analysis, title/storyboard and claim matrix.
- `reports/AIJ_*`: novelty attack, two adversarial reviewer simulations, associate-editor simulation, citation/numerical/claim audits, source inventory and PDF QA/build manifests. Simulations are drafting aids, not independent reviews.

The style sample includes author/pre-proof versions and one partially accessible current article; exact portal-level Regular Paper labels were not consistently exposed. This supports structural editorial choices, not a claim that all production metadata were verified. Twelve title candidates were considered in the storyboard. No `.tex` source was created because the existing project has no LaTeX manuscript workflow. Highlights were not created because a current AIJ requirement could not be verified.

The PDF workflow used rendered-page inspection as well as text/bounds checks. All 43 pages of the section-review revision were inspected. Final automated QA reports zero page-bounds or unmapped-glyph failures. The worked example remains Figure 2 beside Section 5.1. AJ5 whiskers show bootstrap intervals, and Results reports the grammar-interface Wilson interval. Tables 4-5 add reachable-input and selection/control information; Table 4 now identifies B1's operation contract. The build manifest binds the PDF to its manuscript, supplement, figures and builder hashes. Humanizer-zh-tw guided positive, focused prose while preserving numerical claims and disclosure; PDF skill guided render-and-verify QA. The Table 6/Figure 5 page break is retained to keep both objects readable; body type was not reduced.

The consistency revision passes 208 repository tests, including eight evidence-record tests and five interface/metadata tests, plus the expanded 265 numerical/configuration checks. The record reconstructs the archived candidate's theory hash, public fitted expression and each of J0-J5; `--reproduce` also compares the complete record and all listed source hashes. Schema checks reject missing fields, unrecognized provenance labels, non-boolean gates and fabricated values for unavailable events. The new offline audit checks all 1,800 B1 slots and all 1,400 AJ5/CJ5 worlds' public variable-name boundary. No runtime evaluator, experimental artifact, model call or supplied realization rule was changed. See `AIJ_CONSISTENCY_REVISION.md` for the requirement-by-requirement disposition.

Verification commands (repository environment):

```text
rtk proxy .venv/bin/python scripts/audit_aij_claims.py
rtk proxy .venv/bin/python scripts/audit_aij_numbers.py
rtk proxy .venv/bin/python scripts/build_aij_evidence_record.py
rtk proxy .venv/bin/python scripts/validate_aij_evidence_record.py --reproduce
rtk proxy .venv/bin/python scripts/audit_aij_contracts.py
rtk proxy .venv/bin/pytest
rtk proxy .venv/bin/python scripts/build_aij_figures.py
rtk proxy .venv/bin/python scripts/build_aij_manuscript.py
rtk proxy pdftoppm -scale-to 1500 -png output/pdf/AIJ_manuscript_and_supplement.pdf tmp/pdfs/aij/page
rtk proxy .venv/bin/python scripts/qa_aij_pdf.py
rtk proxy python3 scripts/build_nmi_reviewer_archive.py --verify output/archive/nmi-preservation-archive-9ebf0dc548a5.tar.gz
```

The archive must be downloaded from the public evidence release if absent locally. The numerical audit also checks excluded raw ledgers supplied by that preservation archive. No command above requests model inference.

## Version-control scope

The AIJ conversion, focused revision and consistency revision are recorded on `nmi-minimal-targeted-sensitivity-v1`. Code tag `aij-review-package-v1` identifies the baseline manuscript and utilities; the section-review revision builds on that baseline and is bound by the updated PDF build manifest; data release `nmi-github-submission-v4` remains unchanged. `docs/publication/AIJ_REPRODUCTION.md` gives the exact pairing and clean-environment commands. Existing modified NMI manuscript/PDF/builder files and unrelated raw experiment outputs are excluded. The requested `docs/publication/NMI_REJECTION_LESSON.md` remains local-only because it was designated internal; it is not included in the public push. The evidence release is not rebuilt or replaced. Submission details and post-upload verification are recorded in `docs/publication/AIJ_EDITORIAL_INTEGRATION.md`.

## Two-sentence scientific center

We introduce a prospective executable assay for bounded hypothesis-space expansion that distinguishes structural representational change from retrospective fit. Applying field-level provenance and replay to hybrid LLM-symbolic systems shows that end-to-end discovery scores can misattribute both successful explanatory content and apparent model failure when deterministic scaffolds or interfaces mediate what reaches the evaluator.

## Section-review revision

All 89 IDs from five user-requested Herdr review lanes have explicit dispositions in `reports/AIJ_SECTION_REVIEW_RESOLUTION.md`. Source verification corrected both manuscript errors and reviewer assumptions. The final bounded regression review found no new must-fix or should-fix error. The principal substantive clarifications concern C_rand blind-binding losses/gains, grammar-versus-random selection policies, all-six AJ5 expression/action overwrites, B4/B5 sampling, A4/A6 identity, and second-model/budget scope. The bibliography now contains 45 entries. The additional 21 numerical checks verify exact paired-world and panel identities. No experimental run or frozen scientific result changed.
