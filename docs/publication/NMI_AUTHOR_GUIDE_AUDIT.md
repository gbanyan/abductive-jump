# Nature Machine Intelligence author-guide audit

Checked: 2 September 2026. Target: **Article**.

## Binding format assumptions

| Item | Requirement used for this package | Source | Status |
|---|---|---|---|
| Article length | Main text no more than 3,500 words, excluding abstract, Methods, references and legends | [NMI content types](https://www.nature.com/natmachintell/content) | Enforced in readiness audit |
| Abstract | No more than 150 words; unreferenced | NMI content types | Enforced |
| Displays | No more than six figures/tables in the main paper | NMI content types | Plan uses four figures and one table |
| References | Guideline of about 50 | NMI content types and [initial-submission guidance](https://www.nature.com/nature/for-authors/initial-submission) | Ledger contains 44 candidates; final list is shorter |
| Structure | Introduction has no heading; Results and Methods use topical subheadings; Discussion has no subheadings | NMI content types | Enforced in manuscript |
| Methods | Must contain enough detail to interpret and replicate results | Initial-submission guidance | Main Methods plus Supplementary Methods |
| Title | Fit two print lines/75 characters; avoid abbreviations, technical terms and active verbs | Initial-submission guidance | Candidate ranking checks length; final title is provisional pending author choice |
| Legends | Under 250 words; begin with a title sentence and be understandable alone | Initial-submission guidance | Figure plan enforces |
| Statistics | State tests and tails, exact n, define replicates/error bars, and report exact P values where relevant | Initial-submission guidance | Methods and legends planned accordingly |
| Extended Data | Up to ten multi-panel items; integral material belongs here rather than Supplementary Information | Initial-submission guidance | Seven-item plan |
| Supplementary Information | Essential but oversized or specialized background; small figures/tables preferably Extended Data | Initial-submission guidance | Supplement reserved for algorithms and exhaustive tables |
| Data availability | Original research requires a statement and access to the minimum dataset | [Nature reporting standards](https://www.nature.com/nature/editorial-policies/reporting-standards) | Drafted; DOI remains a pre-submission action |
| Code availability | Central custom code available to editors/reviewers; separate statement after Data availability and before references | Nature reporting standards | Drafted; archival DOI remains a pre-submission action |
| Preregistration | Details should accompany submission | Nature reporting standards | Commit-pinned records identified |
| Initial file | Flexible format; a single PDF or Word file with figures is encouraged; line numbers for PDF | Initial-submission guidance | Markdown is source; submission PDF is a packaging task |
| LaTeX | Accepted at acceptance stage; PDF requested before then | Initial-submission guidance | No `.tex` generated because it adds no current value |
| Cover letter | Optional; explain importance and fit without repeating abstract/Introduction | Initial-submission guidance | Drafted |
| LLM authorship/use | LLMs cannot be authors; use must be documented in Methods | Initial-submission guidance | Disclosure drafted; human approval required |
| AI governance | Human accountability, verification and transparent disclosure are required | [NMI AI policy](https://www.nature.com/natmachintell/editorial-policies/ai) | Human sign-off explicitly unresolved |

## Journal-specific reproducibility signal

The NMI editorial [“What is in your LLM-based framework?”](https://www.nature.com/articles/s42256-024-00896-6) asks authors to identify models, versions, prompts, pipeline roles and reproducibility consequences. The 2026 editorial [“Multi-agent AI systems need transparency”](https://www.nature.com/articles/s42256-026-01183-2) additionally emphasizes design motivation, workflow documentation, human oversight, component comparisons and whether added compute/complexity is justified. The manuscript therefore reports exact model/interface scope, proposal-versus-reasoning ablations, call accounting, deterministic replay and human/AI roles.

## Submission-stage checklist

- [ ] All authors approve title, order, corresponding author and submission.
- [ ] Replace repository placeholders with a public immutable DOI.
- [ ] Generate a line-numbered PDF or Word file with embedded figures.
- [ ] Supply editable vector figures, colour-safe palette and source data.
- [ ] Confirm whether double-anonymized review is requested and prepare files consistently.
- [ ] Declare competing interests, funding, contributions and related manuscripts.
- [ ] Have every author review and approve the AI-use disclosure.
- [ ] Refresh author guidance and literature immediately before submission.

## Interpretation note

The NMI content page and general Nature guidance have historically differed on word limits. This package uses the more specific, current NMI Article limit of 3,500 words. If the live submission system gives a different requirement, the journal-specific live form controls.

