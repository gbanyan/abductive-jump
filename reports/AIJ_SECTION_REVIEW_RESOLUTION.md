# AIJ section-review resolution

Date: 2026-09-10. Baseline: `0214bc592aa55c92e5aaeffd298fbe22b07f3e3c` (`aij-review-package-v1`). This records the user-authorized verification and necessary corrections following five Claude Fable 5.1 / high Herdr reviews. These are AI-assisted drafting reviews, not independent human peer review.

All 89 review IDs are dispositioned: 32 qualification, 32 readability (including two originally closed checks), five data, eight claim and twelve citation IDs. A disposition describes the integrated change, not automatic acceptance of a reviewer's exact replacement. No must-fix or should-fix item remains open after source verification. Optional retention and modified recommendations are explicit below.

Primary artifacts: [manuscript](../manuscript/AIJ_MANUSCRIPT.md), [supplement](../manuscript/AIJ_SUPPLEMENTARY_METHODS.md), [numerical checks](AIJ_NUMERICAL_CHECKS.json), [citation audit](AIJ_CITATION_AUDIT.md). Original reports and follow-up evidence are preserved in [review directory](aij-section-review-2026-09-10/); original reports contain superseded claims and must be read with this disposition and the verification reports.

## guard

| ID | Verified disposition / evidence location |
|---|---|
| aij-guard-01 | Abstract: shortened qualifiers while retaining one held-out family and pre-supplied basis. |
| aij-guard-02 | Introduction: positive contribution statement and AJ5/CJ5 definitions. |
| aij-guard-03 | 2.2: positive statement of the foundations. |
| aij-guard-04 | 2.3: replaced defensive novelty framing with classical discovery and LLM-SR context. |
| aij-guard-05 | 2.5: stated target artifact and observability directly. |
| aij-guard-06 | 2.2: structural-versus-functional boundary consolidated into 3.2 and Limitations. |
| aij-guard-07 | 3.3/5.1: construction-specific control interpretation consolidated in 5.1. |
| aij-guard-08 | RETAINED: 3.3 error-control distinction remains because operational gate thresholds must not be mistaken for calibrated statistical error control. |
| aij-guard-09 | 3.4/6.4: original commitment disclosure retained at provenance definition; future-runtime recommendation shortened. |
| aij-guard-10 | 3.1: simplified P0 exactness and comparator wording without claiming whole-language exhaustiveness. |
| aij-guard-11 | 4.2: shortened explanation-path wording. |
| aij-guard-12 | 4.2/5.2: separated representation source from second-call necessity; substantive limitation retained in 5.2. |
| aij-guard-13 | 4.3/5.3/Figure 4: removed repeated held-out explanation; scope retained in Abstract, Methods, caption and Limitations. |
| aij-guard-14 | 4.3/5.3/Figure 4: consolidated complete-policy interpretation; no isolated search effect claimed. |
| aij-guard-15 | 4.5: shortened replicate and generality repetition; world remains inferential unit. |
| aij-guard-16 | 4.1/7: independent-registration caveat retained in 4.1 and S11. |
| aij-guard-17 | 4.5: described fixed archived-slot audit directly. |
| aij-guard-18 | 5.2: simplified source-factorial interpretation. |
| aij-guard-19 | 5.5/6.3: conceptual-inability boundary consolidated in Discussion. |
| aij-guard-20 | 5.5/S12: positive description of sparse supplied-representation successes; scope retained in Limitations. |
| aij-guard-21 | 5.6/Figure 7: shortened repeated negative-control explanation; mechanism remains explicit. |
| aij-guard-22 | 5.6/Figure 7: fixed-slot/no-adaptive-search boundary retained in Methods, S17 and Limitations. |
| aij-guard-23 | 5.7: reconstruction counts and provenance stated directly; replication boundary retained in Limitations. |
| aij-guard-24 | 6.4: positive account of combined procedure. |
| aij-guard-25 | 6.4: concise validator scope and future runtime-recording recommendation. |
| aij-guard-26 | Data availability: simplified release status while preserving frozen evidence distinction. |
| aij-guard-27 | AI declaration: simplified substantive-use disclosure and added Claude Fable 5.1 review role. |
| aij-guard-28 | S4: shortened fixed-space control caveat; J1 construction boundary retained. |
| aij-guard-29 | S11: consolidated repeated registration/temporal disclosures. |
| aij-guard-30 | S17: consolidated interpretation of archived-slot interventions. |
| aij-guard-31 | S18: stated field authorship and outcome dependence directly. |
| aij-guard-32 | S20: reduced repeated unavailable-timestamp/validator disclaimers while preserving null fields and code-order basis. |

## read

| ID | Verified disposition / evidence location |
|---|---|
| aij-read-01 | Abstract: replaced unexplained provenance jargon with plain account of scored content. |
| aij-read-02 | Abstract: clarified provenance versus dependence and sentence connection. |
| aij-read-03 | Abstract: shortened awkward formulations; final abstract 214 words. |
| aij-read-04 | Introduction: simplified proposed procedure sentence. |
| aij-read-05 | 2.2: simplified structural-membership explanation. |
| aij-read-06 | Introduction/3.4/4.1: defined AJ5 and CJ5 as historical study identifiers before use. |
| aij-read-07 | 3.3/3.4: moved historical provenance disclosure after prospective gate definition. |
| aij-read-08 | 3.3/Table 1/S20: separated V(T) from individual gate requirements and standardized conjunction notation. |
| aij-read-09 | 3.3: explicitly mapped bounded expansion event, validated escape and historical validated jump; defined jump/control worlds. |
| aij-read-10 | 3.3/5.1: consolidated repeated control interpretation. |
| aij-read-11 | 3.4: rendered procedure as six numbered steps. |
| aij-read-12 | 4.2/S4: removed orphan value-only condition; A4_VALUE_ONLY is B3 alias, not A6. Source: analysis.py. |
| aij-read-13 | 4.4: defined P2 at first local use. |
| aij-read-14 | 4.4: defined historical/legacy interface. |
| aij-read-15 | 4.4: introduced DeepSeek checkpoint and native-reasoning budget. |
| aij-read-16 | 4.4: introduced 25% pre-execution repair trigger before results. |
| aij-read-17 | 4.3: replaced cryptic historical-design reference with direct description. |
| aij-read-18 | CLOSED: original review reconciled eleven audit policies; no correction required. |
| aij-read-19 | Figure 2: explained archive test/falsification labels. |
| aij-read-20 | 5.1: clarified intervention/falsification error notation. |
| aij-read-21 | 5.2: reconciled same reasoning code with explicit generation-temperature difference. |
| aij-read-22 | Figures 4/7: clarified plotted historical labels and model-panel label. |
| aij-read-23 | 4.4/5.4/5.5/S4/S12: standardized supplied-representation control terminology. |
| aij-read-24 | 5.5: corrected punctuation in grammar-interface result. |
| aij-read-25 | 6.1: replaced ambiguous verb in representation-language discussion. |
| aij-read-26 | S9: identified A6 as triggered random-untyped graph-edit ablation; source proposals.py and preserved ledgers. |
| aij-read-27 | Supplement: expanded JSR/FJR, DSL and interval/statistical acronyms at introduction. |
| aij-read-28 | S1: removed unused shorthand definition. |
| aij-read-29 | CLOSED: original review reconciled 1,125 + 500 = 1,625 control cases. |
| aij-read-30 | S11: consolidated repeated protocol information. |
| aij-read-31 | 2.3/4.3/5.3/6.1: distinguished incumbent structural language, supplied meta-language and proposal serialization syntax. |
| aij-read-32 | 4.4: simplified runtime sentence. |

## data

| ID | Verified disposition / evidence location |
|---|---|
| aij-data-01 | MODIFIED: existing Control worlds/cases output was already archived in AIJ_NUMERICAL_CHECKS.json; added S10 pointer rather than creating duplicate report. Reviewer withdrew missing-output claim. |
| aij-data-02 | S16: documented zero-difference, exact-enumeration and random-flip branches; all reported contrasts use random flips. |
| aij-data-03 | S9: decomposed 32,400 into 21,600 primary + 10,800 factorial, plus 3,600 distinct A6 calls. |
| aij-data-04 | S20: identified excerpt as shortened field paths with actual values. |
| aij-data-05 | RETAINED: dynamic bitsandbytes quantization is supported by docs/phi4_runtime_extension_manifest.md launch command and description; reviewer withdrew concern. |

## claim

| ID | Verified disposition / evidence location |
|---|---|
| aij-claim-01 | 5.6/Figure 7/S17: corrected C_rand blind-binding interpretation to 10 lost and 15 newly successful known-family worlds, total 57/400; same 13 held-out worlds. Added exact paired-world regression checks. |
| aij-claim-02 | 5.5/Figure 6/S14: disclosed score-based grammar retention versus hash-based C_rand retention. C_rand evaluates paths; no isolated causal selection effect or unsupported crossover availability claim. |
| aij-claim-03 | S14: added family-level random/model successes and single shared meta-law success; 15/96 versus 16/96 is a complete-policy comparison. |
| aij-claim-04 | Abstract/5.5/Figure 6: named second DeepSeek checkpoint and larger budgets. |
| aij-claim-05 | 4.2/Table 4/S4: all six AJ5 conditions use deterministic fitting/action overwrites; do not describe all six as source-only contrasts. B4/B5 sampling policies corrected from source. |
| aij-claim-06 | Abstract: clarified provenance versus dependence; retained bounded interpretation. |
| aij-claim-07 | 5.2: stated factorial temperature difference explicitly. |
| aij-claim-08 | RETAINED: MDA v4 Appendix H explicitly documents cached calls; primary-source verification supports S18. |

## cite

| ID | Verified disposition / evidence location |
|---|---|
| aij-cite-01 | Introduction: removed HypoArena [25] from expansion-system citation range; benchmark description retained in 2.4. |
| aij-cite-02 | 2.1: Bonanno [42] supports fixed propositional-language revision; vocabulary distinction is explicitly the present authors' distinction. |
| aij-cite-03 | Introduction: split harness-score [36,37] from failure-attribution [38] support. |
| aij-cite-04 | 2.3/reference 43: added Langley et al. Scientific Discovery (1987), with MIT Press source supporting BACON search/new concepts; no first or fixed-representation priority claim. |
| aij-cite-05 | Reference 22: verified official ICML 2026 position-paper record and used official URL. |
| aij-cite-06 | Reference 23: verified ICML record; removed unverified PMLR 306 and did not add speculative to-appear status. |
| aij-cite-07 | 2.3/reference 44: added official ICLR 2025 LLM-SR paper and neutral model-skeleton/parameter-fitting description. |
| aij-cite-08 | 2.4/reference 45: added Shi et al. v2 constrained Kan-extension completion description; did not generalize to natural-language discovery tasks. |
| aij-cite-09 | Reference 7: added Morgan Kaufmann publisher. |
| aij-cite-10 | Reference 16: added official ICML proceedings name. |
| aij-cite-11 | Reference 39: matched author-name spelling in cited source. |
| aij-cite-12 | Reference 40: added institution; omitted conflicting report number rather than choosing between cover/catalog numbering. |

## Final regression and validation

The bounded final claim-regression review found no new must-fix or should-fix error; see [full report](aij-section-review-2026-09-10/final-regression-review.md) for evidence and coverage limits. Optional notes 1 and 2 were incorporated as cross-reference corrections (Figure 4 → Section 4.3/Table 3; historical parser → S13). Note 3 required no change because held-out scope remains locally available in the caption and Methods. Root separately verified MDA caching and the MIT Press book description, which that final reviewer did not re-fetch.

- Numerical/configuration audit: 265 checks pass, including 21 added exact paired-world and panel-identity checks; frozen experimental values unchanged.
- Evidence-record validator with `--reproduce`: passes; archived values/source hashes and deterministic reconstruction match.
- Contract audit: all 1,800 B1 slots and 1,400 AJ5/CJ5 public-name boundaries pass.
- Repository suite: 208 tests pass in `.venv`; ambient-Python invocation lacked dependencies and was replaced by the repository environment.
- Claim lint: six context flags manually inspected (four held-out/unlock, two explicit scope boundaries); the script reports an inventory, not a self-awarded scientific pass.
- PDF: 43 A4 pages, 11 pt narrative body, seven figures, six main tables, 20 supplementary sections, 45 references. All pages visually inspected; zero bounds/glyph failures. Equation-associated heading grouping repaired to prevent an orphan Section 3.3 heading.

No evaluator, generator, fitting rule, frozen experiment artifact, scientific threshold or model run changed. Pre-existing NMI changes and unrelated raw outputs were left untouched. The working-tree editorial revision builds on the baseline code tag; it is not claimed to be contained in that existing tag. Author attestations and journal upload checks remain the separate existing submission requirements. The manuscript was subsequently submitted to *Artificial Intelligence* on 2026-09-10; submission details and post-upload verification are recorded in `docs/publication/AIJ_EDITORIAL_INTEGRATION.md`. No editorial message or decision has been recorded.

The five review agents were verified settled and their reports preserved before closing this round's tabs `w12A:t2`–`w12A:t6`. No workspace or worktree was created or removed. Scoped text/source whitespace checks pass; generated PDF syntax naturally contains whitespace and was verified with PDF-specific QA instead.
