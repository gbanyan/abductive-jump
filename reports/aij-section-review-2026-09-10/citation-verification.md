# Independent verification of aij-cite recommendations

Verifier: aij-cite (bounded subtask: verification only).
Date: 2026-09-10. HEAD: `0214bc592aa55c92e5aaeffd298fbe22b07f3e3c`.
Scope: the 12 findings in `tmp/aij-section-review-2026-09-10/aij-cite.md` plus claim-08 (MDA caching, Supplement S18).
Rule applied: every verdict below rests on a primary record fetched today (arXiv metadata/HTML, Crossref, PMLR, ACL Anthology, ICLR proceedings, ICML site, OpenLibrary, Internet Archive, author PDFs). Earlier reports, including my own review, were treated as claims to be checked, not as evidence. No manuscript, code, report or git state was modified.

Verdict key: **accept** = proposed change is supported as written; **modify** = the finding stands but the proposed wording/entry must change (safe text given); **reject** = the finding does not hold; **unresolved** = cannot be settled from accessible primary sources today.

Summary: accept 6 (01, 03, 05, 09, 10, 11), modify 5 (02, 04, 07, 08, 12), unresolved-but-actionable 1 (06), claim-08 confirmed. No finding rejected.

---

## aij-cite-01 — HypoArena [25] in the "expand ... spaces" range · **accept** (must-fix)

Manuscript: `AIJ_MANUSCRIPT.md:21` "Some explicitly expand principle spaces, mechanistic model classes or causal structures [23–26]."

Sources (arXiv abstract pages, fetched today):
- [25] https://arxiv.org/abs/2607.15766 — "we introduce HypoArena, comprising HypoData, a benchmark of 988 cases across six scientific and analytical domains, and HypoEval, an evaluation framework for open-ended hypothesis sets." No system or expansion mechanism is proposed.
- [23] https://arxiv.org/abs/2602.06448 — "treats scientific discovery as Bayesian optimization over an expanding principle space".
- [24] https://arxiv.org/abs/2608.09696 — LLM "used as a way to propose new models when the current hypothesis space is detected to be insufficient (c.f., M-open Bayesian inference)".
- [26] https://arxiv.org/abs/2609.01526 — "correction rules that revise the causal structures and mechanisms of each hypothesis".

Safe replacement: "Some explicitly expand principle spaces, mechanistic model classes or causal structures [23,24,26]."

## aij-cite-02 — Bonanno [42] and vocabulary change · **modify** (should-fix)

Manuscript: `AIJ_MANUSCRIPT.md:37` "Belief update and revision can change accepted sentences within a fixed logical vocabulary; their semantic characterization is different from changing the vocabulary itself [42]."

Source: arXiv HTML full text https://arxiv.org/html/2310.11506 (author version of AIJ 339 (2025) 104259; Crossref 10.1016/j.artint.2024.104259 confirms journal/volume/year).
- Abstract: "We provide a new characterization of both belief update and belief revision in terms of a Kripke-Lewis semantics ... we identify the initial belief set K with the set of formulas that are believed at that state".
- Section 2: "We consider a propositional logic based on a countable set At of atomic formulas. We denote by Φ₀ the set of Boolean formulas constructed from At".
- Section 7: "as in the original AGM theory – we restricted the analysis to a propositional language containing only Boolean formulas."
- The word "vocabulary" does not occur (0 hits); "language" occurs only in the sense above. The paper makes no statement about changing the language.

Finding confirmed: the first clause is supported (belief sets are sets of formulas of a fixed propositional language Φ₀); the second clause ("different from changing the vocabulary itself") is not in the source. My original proposed wording used "vocabulary", which the source does not use; replace with the source's own term.

Safe replacement: "Belief update and revision, as characterized semantically by Bonanno [42], change the set of accepted formulas within a fixed propositional language. Changing the language itself is a different operation, which that characterization does not address."

## aij-cite-03 — [36–38] and bidirectional score changes · **accept** (optional)

Manuscript: `AIJ_MANUSCRIPT.md:21` "...can change scores in both directions [36–38]."

Sources:
- [36] https://arxiv.org/abs/2605.27898 (v3) — "Comparisons with source implementations show large bidirectional score changes and model-ranking reversals".
- [37] https://arxiv.org/abs/2605.23950 — "harness-induced variance can substantially exceed model-induced variance, including cases of model ranking reversal".
- [38] https://aclanthology.org/2026.acl-long.912/ — abstract concerns "identifying the responsible agent and decisive step of a failure"; reports attribution accuracy ("full traces improve attribution accuracy by up to 76.5%"), not score changes.

Safe replacement: "agent-evaluation research shows that parsers, tool interfaces and execution scaffolds can change scores in both directions [36,37], and that complete traces are needed to attribute failures [38]."

## aij-cite-04 — missing Langley et al. 1987 · **modify** (should-fix; content wording downgraded)

Bibliographic metadata verified:
- Crossref monograph record: DOI 10.7551/mitpress/6090.001.0001, title "Scientific Discovery", authors Patrick W. Langley, Herbert A. Simon, Gary Bradshaw, Jan M. Zytkow, The MIT Press, 1987 (https://api.crossref.org/works/10.7551/mitpress/6090.001.0001).
- Internet Archive catalogue record scientificdiscov00insc: "Scientific discovery : computational explorations of the creative processes", Cambridge, Mass.: MIT Press, 1987, ISBN 0262121166 / 0262620529 (https://archive.org/metadata/scientificdiscov00insc/metadata).
- OpenLibrary edition: same title/subtitle, MIT Press, 1987 (https://openlibrary.org/isbn/9780262121163.json).
- Contemporary reviews listing all four authors: Quarterly Review of Biology 1988 (10.1086/415726), Isis 1989 (10.1086/354955), Leonardo 1988 (10.2307/1578567).

Content check: the MIT Press page (mitpress.mit.edu and direct.mit.edu) returned 403 / a bot challenge, and the open-access copy of the companion AIJ article (Langley & Zytkow, "Data-driven approaches to empirical discovery", Artificial Intelligence 40 (1989) 283–312, Crossref 10.1016/0004-3702(89)90051-9) could not be retrieved as text. I therefore could NOT verify today, from an accessible primary text, the specific framing "heuristic search over a fixed representation of laws and data". My original proposed sentence also contained "first cast", a priority claim that must not be introduced.

Safe replacement (asserts only what verified titles support): "Computational approaches to empirical discovery predate the systems reviewed here [Langley et al. 1987]. Symbolic regression and physics-informed equation discovery search expressive program spaces with quantitative evaluators [10,11]."

Optional richer sentence, ONLY if the authors confirm it against their own copy of the book (unverified by me today): "Classical computational discovery programs treated discovery as heuristic search within a fixed representation of data and laws [Langley et al. 1987]."

Safe bibliographic entry: "P. Langley, H. A. Simon, G. L. Bradshaw, J. M. Żytkow, Scientific Discovery: Computational Explorations of the Creative Processes, MIT Press, Cambridge, MA, 1987. https://doi.org/10.7551/mitpress/6090.001.0001"
(Author-name forms: Crossref gives "Patrick W. Langley" and "Gary Bradshaw"; the reviews give "Pat Langley" and "Gary L. Bradshaw". Either initial form is defensible; "Żytkow" with diacritic follows the author's usual spelling, Crossref has "Zytkow".)

## aij-cite-05 — Zahavy [22] venue · **accept** (should-fix)

Sources:
- ICML 2026 site https://icml.cc/virtual/2026/poster/67091 — title "Position: LLMs can't jump", author Tom Zahavy, track label "Position Paper Posters".
- Author PDF https://www.tomzahavy.com/files/llms-cant-jump.pdf (text extracted): dated "Jan 27th, 2026", "Tom Zahavy, Google DeepMind", "This position paper argues ...".
- PMLR: no ICML 2026 volume exists on https://proceedings.mlr.press/ as of today (index last compiled 17 Aug 2026; 2026 volumes listed are v307, v309, v312, v313, v315, v319, v320, v323, v326, v328, v331–v334, v336, v337, v339; none is ICML). So no PMLR volume/pages can be given.
- PhilSci-Archive https://philsci-archive.pitt.edu/28024/ still returns "The requested URL was rejected"; its existence is supported only by search-index title. Keep the URL as the manuscript already has it; deposit metadata unverified.

Safe bibliographic entry: "T. Zahavy, Position: LLMs can't jump, in: Proceedings of the 43rd International Conference on Machine Learning (ICML), 2026, position paper track; preprint PhilSci-Archive 28024. https://philsci-archive.pitt.edu/28024/"

## aij-cite-06 — PiEvo [23] "PMLR 306" · **unresolved, actionable** (should-fix)

Sources:
- arXiv comments field https://arxiv.org/abs/2602.06448: "Proceedings of the 43rd International Conference on Machine Learning, Seoul, South Korea. PMLR 306, 2026. Copyright 2026 by the author(s)". This is the authors' own statement (copied from the ICML template footer).
- https://proceedings.mlr.press/v306/ → HTTP 404 today. The PMLR index lists no ICML 2026 volume (see aij-cite-05).
- ICML acceptance verified: https://icml.cc/virtual/2026/poster/65369 (Poster, Mon Jul 6 2026, Hall A #902; authors Yingming Pu, Tao Lin, Hongyu Chen).

The volume number is neither confirmed nor contradicted; it is unverifiable until PMLR publishes. Recommend citing the verified facts only.

Safe bibliographic entry: "Y. Pu, T. Lin, H. Chen, Principle-Evolvable Scientific Discovery via Uncertainty Minimization, in: Proceedings of the 43rd International Conference on Machine Learning (ICML), 2026, to appear in PMLR; author version arXiv:2602.06448v2. https://arxiv.org/abs/2602.06448v2"

## aij-cite-07 — missing LLM-SR · **modify** (should-fix; wording softened)

Metadata verified:
- ICLR 2025 proceedings page https://proceedings.iclr.cc/paper_files/paper/2025/hash/28df8e730c054c5331855fd4d5403ba9-Abstract-Conference.html — title "LLM-SR: Scientific Equation Discovery via Programming with Large Language Models"; authors Parshin Shojaee, Kazem Meidani, Shashank Gupta, Amir Barati Farimani, Chandan Reddy.
- arXiv https://arxiv.org/abs/2404.18400 — same title; authors listed as "Shojaee, Parshin; Meidani, Kazem; Gupta, Shashank; Farimani, Amir Barati; Reddy, Chandan K"; comments "ICLR 2025 Oral".
- Supporting passage (both pages): "The LLM iteratively proposes new equation skeleton hypotheses, drawing from its domain knowledge, which are then optimized against data to estimate parameters."

The source supports "the model proposes equation skeletons and a numerical optimizer fits their parameters". My review text called LLM-SR "the standard instance"; that is an unsupported characterization and must not enter the manuscript. The proposed second sentence ("Such splits are precisely where field-level provenance is needed") is the manuscript authors' own argument, not a claim about LLM-SR; it is acceptable only as their claim. A neutral single sentence is given.

Safe replacement (insert after the FunSearch sentence in 2.3): "LLM-SR makes a similar division explicit for equation discovery: the model proposes equation skeletons and their parameters are then optimized against data [LLM-SR]."

Safe bibliographic entry (format matches ref 14): "P. Shojaee, K. Meidani, S. Gupta, A. Barati Farimani, C. K. Reddy, LLM-SR: Scientific Equation Discovery via Programming with Large Language Models, ICLR, 2025. https://proceedings.iclr.cc/paper_files/paper/2025/hash/28df8e730c054c5331855fd4d5403ba9-Abstract-Conference.html"

## aij-cite-08 — Shi et al. 2608.26187 · **modify** (should-fix; description corrected)

Legitimacy and metadata (arXiv, fetched today):
- https://arxiv.org/abs/2608.26187 — citation_title "When the Canonical Completion Is Wrong: Formalizing and Measuring the Jump in Large Language Models"; authors Shi, Dai; Li, Xiaoyu; Hernández-Lobato, José Miguel; v1 2026-08-22, v2 2026-09-04; subjects cs.CL, cs.AI, cs.LG, cs.LO; license CC BY 4.0.
- HTML full text https://arxiv.org/html/2608.26187 — affiliations "University of Cambridge" and "University of New South Wales". It is a preprint, not peer-reviewed.

Content and relevance (HTML full text):
- Cites Zahavy by name: "Zahavy (2026) raised this question and answered it negatively, arguing that LLMs have mastered induction and are increasingly mastering deduction, yet remain structurally incapable of the jump."
- Method: "We define a jump instance as a finite extension problem constrained by excluding the canonical completion given by the Kan extensions and leave exactly one unique correct completion." Instances are finite category-theoretic extension problems rendered as prompts, not natural-language text tasks.
- Result: "We tested four frontier models on nine instances, where the Kan-default rate is zero in all 248 constrained trials, suggesting that the models can jump at least in this step."
- Scope caveat in the paper itself: "the model's performance on the case where constraints and answer forms are on itself (Zahavy, 2026) is still unclear."

Verdict: the reference exists, engages [22] directly, and is a competing operationalization of the "jump"; it is therefore relevant to the sentence at `AIJ_MANUSCRIPT.md:59`. My original wording "in text tasks" was inaccurate and is withdrawn. Because it is a two-week-old preprint, the authors may reasonably treat inclusion as optional rather than required; the priority is a judgment call, not a correctness issue.

Safe replacement: "Zahavy's position motivates the question of generating explanatory premises [22]. Shi et al. formalize a related 'jump' as departure from a canonical (Kan-extension) completion of finite structured data and report that frontier models leave that default on constrained instances [Shi 2026]. Our assay instead evaluates a bounded, executable instance of representational change with hidden-outcome validation."

Safe bibliographic entry: "D. Shi, X. Li, J. M. Hernández-Lobato, When the Canonical Completion Is Wrong: Formalizing and Measuring the Jump in Large Language Models, arXiv preprint, 2026. https://arxiv.org/abs/2608.26187"

(The second reply mentioned in my review, Balani & Panda, arXiv 2608.14397, was not re-verified in this pass and remains optional/unverified.)

## aij-cite-09 — ref 7 publisher · **accept** (optional)

Sources:
- Crossref chapter record https://api.crossref.org/works/10.1016/B978-0-934613-64-4.50040-2 — title "Machine Invention of First-order Predicates by Inverting Resolution", authors Stephen Muggleton, Wray Buntine, container "Machine Learning Proceedings 1988", pages 339–352, 1988, ISBN 9780934613644 (current rights holder listed as Elsevier).
- OpenLibrary ISBN 0934613648 https://openlibrary.org/isbn/0934613648.json — "Machine Learning Proceedings 1988", publisher Morgan Kaufmann.
- Editor field absent in Crossref; do not add an editor.

Safe bibliographic entry: "S. Muggleton, W. Buntine, Machine invention of first-order predicates by inverting resolution, in: Machine Learning Proceedings 1988: Proceedings of the Fifth International Conference on Machine Learning, Morgan Kaufmann, 1988, pp. 339–352."

## aij-cite-10 — ref 16 proceedings name · **accept** (optional)

Source: https://proceedings.mlr.press/v267/huang25n.html — citation_conference_title "International Conference on Machine Learning", pages 25372–25437, authors Kexin Huang, Ying Jin, Ryan Li, Michael Y. Li, Emmanuel Candes, Jure Leskovec; page heading gives "Proceedings of the 42nd International Conference on Machine Learning" (PMLR 267, 2025).

Safe bibliographic entry: "K. Huang, Y. Jin, R. Li, M. Y. Li, E. Candès, J. Leskovec, Automated Hypothesis Validation with Agentic Sequential Falsifications, in: Proceedings of the 42nd International Conference on Machine Learning, PMLR 267 (2025) 25372–25437. https://proceedings.mlr.press/v267/huang25n.html"

## aij-cite-11 — ref 39 author spelling · **accept** (optional)

Source: https://arxiv.org/abs/2602.17217 citation_author: "Crespo-Fernandez, Enrique", "Ray, Oliver", "Filho, Telmo de Menezes e Silva", "Flach, Peter". No accent in the arXiv record. The manuscript's "Crespo-Fernández" is not supported by the source; the choice is between matching the source (no accent) and the author's personal usage (not checked).

Safe bibliographic entry: "E. Crespo-Fernandez, O. Ray, T. de Menezes e Silva Filho, P. Flach, Continual learning and refinement of causal models through dynamic predicate invention, arXiv preprint, 2026. https://arxiv.org/abs/2602.17217"

## aij-cite-12 — ref 40 institution / report number · **modify** (optional)

Sources (author-hosted PDFs, text extracted):
- https://www.mli.gmu.edu/papers/91-95/92-3.pdf — cover carries "92-3", the title "Hypothesis-driven Constructive Induction in AQ17: A Method and Experiments", authors Janusz Wnek and Ryszard S. Michalski, "GMU Center for Artificial Intelligence", and a stamped "P92-2 / MLI92-2". Acknowledgements: "This research was done in the GMU Center for Artificial Intelligence." The paper's own reference list cites sibling reports as "Reports of Machine Learning and Inference Laboratory, Center for Artificial Intelligence, George Mason University, 1992".
- https://www.mli.gmu.edu/papers/91-95/92-2.pdf is a different paper (J. Wnek, "Transformation of Version Space with Constructive Induction: The VS* Algorithm"). So the "MLI92-2" stamp on the cover conflicts with the laboratory's own numbering, under which this report is 92-3.

My earlier proposed "MLI 92-2" was wrong. Use 92-3 per the laboratory's file numbering, or omit the number.

Safe bibliographic entry: "J. Wnek, R. S. Michalski, Hypothesis-driven Constructive Induction in AQ17: A Method and Experiments, Report 92-3, Reports of the Machine Learning and Inference Laboratory, Center for Artificial Intelligence, George Mason University, Fairfax, VA, 1992. https://www.mli.gmu.edu/papers/91-95/92-3.pdf"

## claim-08 — Supplement S18 "caches calls [24]" · **confirmed**

Manuscript: `AIJ_SUPPLEMENTARY_METHODS.md:214` "Model Discovery Agent explicitly separates proposal from Bayesian inference, reports an expansion-component ablation and caches calls [24]."

Source: arXiv HTML v4 https://arxiv.org/html/2608.09696v4 (fetched today; the manuscript cites v4):
- Caching (Appendix H, experimental setup): "Throughout, the LLM runs at temperature 0.2–0.4 with JSON-mode responses and every call is cached for reproducibility".
- Separation: "every numeric quantity — the parameter posterior, the marginal evidence, the model posterior p(m|D), the VoI design score, and the forecast — is computed by Bayesian inference, never by the LLM."
- Ablation (Figure 1 and Figure 7 captions): "an ablation of MDA without M-open exploration (grey, 'no M-open')"; "MDA vs. the same model without M-open expansion ('no M-open')".

All three clauses are supported. No change needed.

---

## Consolidated safe edits (for the integrator)

| ID | Verdict | Edit |
|---|---|---|
| 01 | accept | line 21: "[23–26]" → "[23,24,26]" |
| 02 | modify | line 37: replace sentence with the aij-cite-02 safe replacement (uses "fixed propositional language", not "vocabulary") |
| 03 | accept | line 21: split citation as given |
| 04 | modify | 2.3 opening: use the safe (title-supported) sentence; richer framing only after the authors verify it in the book; add Langley et al. 1987 entry with DOI |
| 05 | accept | ref 22: ICML 2026 position paper entry; keep PhilSci URL |
| 06 | unresolved | ref 23: drop "PMLR 306", write "to appear in PMLR" until the volume is online |
| 07 | modify | 2.3: one neutral sentence; add LLM-SR entry with ICLR proceedings URL |
| 08 | modify | 2.4 line 59: corrected description (Kan-extension completion of finite structured data); add Shi et al. entry; priority is the authors' call |
| 09 | accept | ref 7: add "Morgan Kaufmann"; no editor |
| 10 | accept | ref 16: add proceedings name |
| 11 | accept | ref 39: "Crespo-Fernandez" per arXiv, unless the author's own usage is known |
| 12 | modify | ref 40: report number 92-3 (not 92-2); institution as given |
| claim-08 | confirmed | no change |

## Unresolved items and access limits (today)
- PMLR volume for ICML 2026 (refs 22, 23): not yet published; cannot be verified or refuted.
- PhilSci-Archive item 28024: site rejects access; deposit metadata unverified; URL retained as already in the manuscript.
- Langley et al. 1987 content framing ("heuristic search over a fixed representation"): metadata fully verified; content not verified from an accessible primary text today (MIT Press pages blocked; eScholarship copy of Langley & Zytkow 1989 not retrievable as text). Safe sentence provided.
- Editor of Machine Learning Proceedings 1988: not in Crossref; omitted.
- Balani & Panda arXiv 2608.14397: not re-verified in this pass.
