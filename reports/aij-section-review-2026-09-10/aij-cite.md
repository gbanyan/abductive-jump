# aij-cite review: citation correctness

Reviewer: aij-cite (one of five independent domain reviewers).
Domain: bibliographic metadata, whether original sources support attached claims, predecessor attribution, missing essential references.
Review date: 2026-09-10.

**HEAD reviewed:** `0214bc592aa55c92e5aaeffd298fbe22b07f3e3c` (from `git rev-parse HEAD`, re-confirmed at save time).

Branch: `nmi-minimal-targeted-sensitivity-v1`. Both `manuscript/AIJ_MANUSCRIPT.md` and `manuscript/AIJ_SUPPLEMENTARY_METHODS.md` were unmodified in the working tree at review time. Files reviewed: those two, `manuscript/figures/aij/*` (existence only), and `reports/AIJ_CITATION_AUDIT.md` as background only, not as verification.

Read-only review: no manuscript, code, data or git changes were made. Evidence is frozen; proposals below are wording corrections only.

## Method

All 42 reference entries were checked against primary records fetched on 2026-09-10:

- Crossref REST API (`api.crossref.org/works/<DOI>`) for every DOI-bearing entry (refs 2, 5, 6, 8, 10–13, 18–21, 28–30, 32–35, 38, 41, 42).
- arXiv abstract pages for every preprint (refs 17, 23–27, 36, 37, 39) and arXiv HTML full text for refs 24 and 39.
- ACL Anthology (refs 15, 28, 38), ICLR proceedings (ref 14), PMLR proceedings (ref 16), ICML 2026 virtual site (refs 22, 23).
- Europe PMC abstracts for Nature / Scientific Reports papers (refs 13, 18–21, 29).
- OpenLibrary ISBN records for the books (refs 3, 4, 31; also Langley et al. 1987 for a proposed addition).
- Full-text PDFs read via `pdftotext`: ref 33 (Timber), ref 34 (HYDRA), ref 35 (Goel et al.), ref 40 (AQ17 report), ref 22 (Zahavy author PDF).
- Edinburgh institutional record for ref 41; C. S. Peirce archive item for ref 1.
- Citation-coverage script: every number 1–42 is cited in the main text; the supplement cites only main-list numbers (6–9, 20, 24, 26, 32, 34–41).

Coverage limits are listed at the end.

## Summary: three most consequential findings

1. **aij-cite-01 (must-fix)** Introduction cites HypoArena [25] among systems that "explicitly expand principle spaces, mechanistic model classes or causal structures". HypoArena is a benchmark and expands nothing.
2. **aij-cite-02 (should-fix)** Ref 42 (Bonanno) is used to support a claim about vocabulary change that the paper does not make.
3. **aij-cite-05 / aij-cite-06 (should-fix)** Two venue facts are incomplete or unverifiable: Zahavy's paper is an ICML 2026 position paper, not only a PhilSci preprint; and PMLR volume 306 does not exist yet, so the PiEvo volume number is author-asserted only.

---

## Title / Abstract

No citations. The abstract's "operationalizes a longstanding representation-search distinction" is supported by [7–9,32,40] in the Introduction. No issues.

## 1. Introduction

### aij-cite-01 · must-fix
- Location: `manuscript/AIJ_MANUSCRIPT.md:21` — "Some explicitly expand principle spaces, mechanistic model classes or causal structures [23–26]."
- Evidence: [25] Zhong et al., arXiv 2607.15766 (https://arxiv.org/abs/2607.15766) introduces HypoArena, a benchmark of 988 cases built from "reconstructed pre-conclusion contexts" with pairwise judging. It does not expand any hypothesis space. [23] PiEvo ("expanding principle space", https://arxiv.org/abs/2602.06448v2), [24] MDA ("M-open expansion", https://arxiv.org/abs/2608.09696v4) and [26] EvoSCM (causal structures/mechanisms revised, https://arxiv.org/abs/2609.01526) do.
- Type: error (wrong citation range).
- Proposed replacement: "Some explicitly expand principle spaces, mechanistic model classes or causal structures [23,24,26]."

### aij-cite-03 · optional
- Location: `manuscript/AIJ_MANUSCRIPT.md:21` — "agent-evaluation research shows that parsers, tool interfaces and execution scaffolds can change scores in both directions [36–38]."
- Evidence: [36] UniACE v3 abstract reports "large bidirectional score changes and model-ranking reversals" (https://arxiv.org/abs/2605.27898v3). [37] argues harness-induced variance can exceed model-induced variance (https://arxiv.org/abs/2605.23950). [38] TraceElephant (https://aclanthology.org/2026.acl-long.912/) is a failure-attribution benchmark and reports no score changes.
- Type: editorial precision.
- Proposed replacement: "agent-evaluation research shows that parsers, tool interfaces and execution scaffolds can change scores in both directions [36,37], and that complete traces are needed to attribute failures [38]."

Other Introduction citations ([7–9,32,40]; [10–20]) checked and supported.

## 2. Background and related work

### 2.1 Abduction and theory revision

Verified: [1] Peirce 1878, Popular Science Monthly 13, 470–482 (https://cspeirce.omeka.net/items/show/7). [2] Harman, Phil. Rev. 74(1), 1965, 88–95 (Crossref 10.2307/2183532). [3] Lipton 2nd ed., Routledge 2004 (OpenLibrary ISBN 9780415242035). [30] Pearl 2nd ed. 2009 (Crossref 10.1017/CBO9780511803161). [31] Peters/Janzing/Schölkopf 2017 (OpenLibrary ISBN 9780262037310). [41] ABC: Edinburgh record abstract states "abduction adds new axioms, belief revision deletes conflicting axioms, while reformation changes the language of the theory" (https://www.research.ed.ac.uk/en/publications/abc-repair-system-for-datalog-like-theories/; Crossref 10.5220/0006959703350342, pp. 335–342, 2018). [33] Timber: full PDF confirms qualitative model fragments, competing explanations, metareasoning-based revision (Cognitive Science 42 (2018) 1110–1145; https://www.qrg.northwestern.edu/papers/Files/QRG_Dist_Files/QRG_2018/FriedmanEtAlCogSci2018.pdf).

### aij-cite-02 · should-fix
- Location: `manuscript/AIJ_MANUSCRIPT.md:37` — "Belief update and revision can change accepted sentences within a fixed logical vocabulary; their semantic characterization is different from changing the vocabulary itself [42]."
- Evidence: Bonanno's abstract (AIJ 339 (2025) 104259; arXiv https://arxiv.org/abs/2310.11506; Crossref 10.1016/j.artint.2024.104259) characterizes KM update and AGM revision via Kripke-Lewis frames and concludes the two are "much the same". It says nothing about vocabulary change. The second clause is the authors' inference placed under the citation.
- Type: claim not supported by source (attribution error).
- Proposed replacement: "Belief update and revision, as characterized semantically by Bonanno [42], change the accepted sentences of a fixed logical vocabulary. Changing the vocabulary itself is a different operation, which that characterization does not address."

### 2.2 Constructive induction and representation change

Verified: [7] Muggleton & Buntine 1988, ICML-5, pp. 339–352 — confirmed via the ACM DL index entry (10.5555/3091765.3091809) surfaced in search; direct ACM page returned 403 (see unresolved). [8] Stahl, Machine Learning 20(1–2) (1995) 95–117 (Crossref 10.1023/A:1022638219164). [9] Donoho & Rendell, JAIR 2 (1995) 411–446; abstract supports both clauses, including "systems that produce only small, local changes to a theory have limited value for accomplishing complex structural alterations" (https://arxiv.org/abs/cs/9504101). [32] Muggleton/Lin/Tamaddoni-Nezhad, Machine Learning 100 (2015) 49–73 (Crossref). [4] Boden 2nd ed. (Routledge; OpenLibrary lists 2003 for ISBN 9780415314534, Routledge/reviews list 2004 — keep 2004, not an error). [5] Wiggins, KBS 19(7) (2006) 449–458; [6] Wiggins, NGC 24(3) (2006) 209–222 (Crossref). [34] HYDRA: full PDF confirms "heuristics-guided search over model changes" (AIJ 334 (2024) 104161; https://www.dekleer.org/Publications/ADomainIndepent.pdf). [35] Goel et al.: full PDF confirms "Both the framework components and the entire system are evaluated" (AIJ 331 (2024) 104111; https://hrilab.tufts.edu/publications/goeletal24aij.pdf). [39] arXiv HTML confirms a "Predict-Verify-Refine cycle" with dynamic predicate invention, online/continual (https://arxiv.org/html/2602.17217). [40] AQ17 report PDF confirms new attributes generated from hypotheses and reformulation of training examples (https://www.mli.gmu.edu/papers/91-95/92-3.pdf).

### 2.3 Search-based AI discovery

Verified: [10] Schmidt & Lipson, Science 324 (2009) 81–85; [11] AI Feynman, Sci. Adv. 6(16) (2020) eaay2631; [12] Fawzi et al., Nature 610 (2022) 47–53; [13] Romera-Paredes et al., Nature 625 (2024) 468–475, Europe PMC abstract confirms "pairing a pretrained LLM with a systematic evaluator" (all via Crossref/Europe PMC).

### aij-cite-04 · should-fix (missing predecessor)
- Location: Section 2.3 opening, `manuscript/AIJ_MANUSCRIPT.md:49`.
- Evidence: Section 2.3 begins search-based discovery in 2009. The AIJ audience will expect the classical heuristic-search discovery programme (BACON and successors), which framed discovery as search within a representation and is the origin of the representation-versus-search framing the paper says it operationalizes. Verified record: P. Langley, H. A. Simon, G. L. Bradshaw, J. M. Żytkow, Scientific Discovery: Computational Explorations of the Creative Processes, MIT Press, 1987 (OpenLibrary ISBN 9780262121163).
- Type: missing essential reference.
- Proposed new opening sentences for 2.3: "Computational scientific discovery was first cast as heuristic search over a fixed representation of laws and data [Langley et al. 1987]. Symbolic regression and physics-informed equation discovery continue this line with quantitative evaluators over expressive program spaces [10,11]."
- Proposed reference entry: "P. Langley, H. A. Simon, G. L. Bradshaw, J. M. Żytkow, Scientific Discovery: Computational Explorations of the Creative Processes, MIT Press, 1987."

### aij-cite-07 · should-fix (missing essential reference)
- Location: Section 2.3 after the FunSearch sentence (`manuscript/AIJ_MANUSCRIPT.md:49`), or Section 2.4.
- Evidence: The manuscript's central provenance concern is a model proposing structure while a deterministic fitter supplies coefficients. LLM-SR is the standard instance of exactly that split. ICLR 2025 proceedings abstract (verified): "The LLM iteratively proposes new equation skeleton hypotheses, drawing from its domain knowledge, which are then optimized against data to estimate parameters." Record: P. Shojaee, K. Meidani, S. Gupta, A. Barati Farimani, C. K. Reddy, LLM-SR: Scientific Equation Discovery via Programming with Large Language Models, ICLR 2025 (https://proceedings.iclr.cc/paper_files/paper/2025/hash/28df8e730c054c5331855fd4d5403ba9-Abstract-Conference.html; arXiv 2404.18400).
- Type: missing essential reference.
- Proposed addition: "LLM-SR makes the same division explicit for equation discovery: the model proposes equation skeletons and a numerical optimizer fits their parameters [LLM-SR]. Such splits are precisely where field-level provenance is needed."
- Proposed reference entry: "P. Shojaee, K. Meidani, S. Gupta, A. Barati Farimani, C. K. Reddy, LLM-SR: Scientific Equation Discovery via Programming with Large Language Models, ICLR, 2025. https://arxiv.org/abs/2404.18400"

### 2.4 Language-model hypothesis generation and scientific agents

Verified: [14] Wang et al., ICLR 2024, six authors, compiles hypotheses to Python programs (ICLR proceedings page). [15] Zhou et al., NLP4Science 2024, 117–139 (https://aclanthology.org/2024.nlp4science-1.10/). [16] Huang et al., PMLR 267 (2025) 25372–25437, endpoint huang25n, sequential falsification with statistical guarantees (https://proceedings.mlr.press/v267/huang25n.html). [17] Lu, Lu, Lange, Foerster, Clune, Ha, arXiv 2408.06292 (v3, Sept 2024). [18] Gottweis et al., Nature 655 (2026) 487–496; [19] Ghareeb et al., Nature 655 (2026) 497–505; [20] Boiko et al., Nature 624 (2023) 570–578 — Crossref + Europe PMC abstracts support "automate research workflows, integrate scientific tools, or validate selected proposals experimentally". [24] MDA v4 HTML verified: "an ablation of MDA without M-open exploration", and "every numeric quantity — the parameter posterior, the marginal evidence, the model posterior p(m|D), the VoI design score, and the forecast — is computed by Bayesian inference, never by the LLM" (https://arxiv.org/html/2608.09696v4). [26] EvoSCM abstract: "designs discriminative interventions, and commits to falsifiable predictions" (https://arxiv.org/abs/2609.01526). [25] HypoArena HTML: reference "is withheld from generation and enters the arena only as an anonymous competitor" (supports "reference separation"); Bradley–Terry–Davidson pairwise judging plus six-dimension rubric; no live experiments (supports the contrast drawn) (https://arxiv.org/html/2607.15766). [27] Chen et al., arXiv 2510.15614 (v1 Oct 2025, v3 May 2026). [28] Liu et al., Findings of ACL 2026, 13187–13207 (https://aclanthology.org/2026.findings-acl.644/). [21] Bellemare-Pepin et al., Sci Rep 16 (2026) 1279 — Europe PMC abstract confirms divergent-creativity measures. [29] Ding & Li, Sci Rep 15 (2025) 9587 — Europe PMC abstract confirms a simulated-lab reconstruction of a Nobel-worthy discovery ("historical discovery reconstructions" is a fair gloss).

### aij-cite-05 · should-fix
- Location: `manuscript/AIJ_MANUSCRIPT.md:404` — ref 22 "T. Zahavy, LLMs Can't Jump, PhilSci-Archive preprint 28024, 2026. https://philsci-archive.pitt.edu/28024/"
- Evidence: The paper is an accepted ICML 2026 position paper: https://icml.cc/virtual/2026/poster/67091 ("Position: LLMs can't jump", Tom Zahavy, track "Position Paper Posters"). Author PDF (https://www.tomzahavy.com/files/llms-cant-jump.pdf) is dated 27 January 2026, Google DeepMind, self-described as "This position paper". The PhilSci-Archive record exists (search index shows item 28024 titled "LLMs can't jump.") but the site rejected direct access ("The requested URL was rejected"), so its deposit metadata is unverified. Citing only the preprint understates the venue.
- Type: incomplete bibliographic record.
- Proposed replacement: "T. Zahavy, Position: LLMs can't jump, in: Proceedings of the 43rd International Conference on Machine Learning (ICML), 2026, position track; preprint PhilSci-Archive 28024. https://philsci-archive.pitt.edu/28024/"

### aij-cite-06 · should-fix
- Location: `manuscript/AIJ_MANUSCRIPT.md:405` — ref 23 "... ICML, PMLR 306, 2026; author version. https://arxiv.org/abs/2602.06448v2"
- Evidence: The PMLR volume number comes only from the authors' arXiv comment ("Proceedings of the 43rd International Conference on Machine Learning (ICML 2026)"). `https://proceedings.mlr.press/v306/` returned "Page not found" on 2026-09-10; the PMLR index (https://proceedings.mlr.press/) lists no ICML 2026 volume (v300 = AISTATS 2026, v305 = CoRL 2025, v307 = NLDL 2026). ICML 2026 acceptance itself is verified (https://icml.cc/virtual/2026/poster/65369).
- Type: unverifiable metadata (not shown to be wrong).
- Proposed replacement: "Y. Pu, T. Lin, H. Chen, Principle-Evolvable Scientific Discovery via Uncertainty Minimization, in: Proceedings of the 43rd International Conference on Machine Learning (ICML), 2026, to appear in PMLR; author version arXiv:2602.06448v2. https://arxiv.org/abs/2602.06448v2" — restore the volume and pages once the PMLR page exists.

### aij-cite-08 · should-fix (missing adjacent work)
- Location: `manuscript/AIJ_MANUSCRIPT.md:59` — "Zahavy's position motivates the question of generating explanatory premises [22]; our assay evaluates a bounded, executable instance of representational change."
- Evidence: A direct empirical operationalization of Zahavy's "jump" already exists: D. Shi, X. Li, J. M. Hernández-Lobato, When the Canonical Completion Is Wrong: Formalizing and Measuring the Jump in Large Language Models, arXiv 2608.26187 (submitted 22 Aug 2026, revised 4 Sep 2026; https://arxiv.org/abs/2608.26187). It formalizes jump instances via canonical (Kan) completions and measures whether frontier models leave the default (248 trials, nine instances). Its abstract references "a prominent position [that] holds that LLMs are structurally incapable of such jumps"; the fetched excerpt did not name Zahavy explicitly (unverified detail). Because the manuscript claims to operationalize representational change motivated by Zahavy, omitting a competing operationalization weakens the related-work claim. A second reply, P. Balani, S. Panda, "LLMs Don't Pay for the Jump", arXiv 2608.14397 (14 Aug 2026), explicitly responds to Zahavy and is optional.
- Type: missing adjacent reference.
- Proposed replacement: "Zahavy's position motivates the question of generating explanatory premises [22]; Shi et al. measure a related 'jump' as departure from a canonical completion in text tasks [Shi 2026]. Our assay instead evaluates a bounded, executable instance of representational change with hidden-outcome validation."
- Proposed reference entry: "D. Shi, X. Li, J. M. Hernández-Lobato, When the Canonical Completion Is Wrong: Formalizing and Measuring the Jump in Large Language Models, arXiv preprint, 2026. https://arxiv.org/abs/2608.26187"

### 2.5 Evaluation and attribution of hybrid systems

Verified: [36] Zhu et al., UniACE v3 (v1 27 May 2026, v3 1 Sep 2026; bidirectional score changes; trace-based failure attribution). [37] Zhang et al., position paper, v1 7 May 2026. [38] Chen et al., ACL 2026 long, 19888–19905; "responsible agent and decisive step of a failure" confirmed. Claims supported. No issues.

## 3. Formal framework
No external citations. No issues.

## 4. Experimental framework
No external citations; model identifiers are outside this domain. No issues.

## 5. Results (5.1–5.7; Figures 2–7; Tables 4–6)
No external citations in any subsection. Figure files exist under `manuscript/figures/aij/` (figure_1_assay … figure_7_worked, png+svg, source_data.json). No issues in this domain.

## 6. Discussion
6.3 cites [36–38] for harness evaluation identifying misattribution risks: supported. 6.1, 6.2, 6.4 carry no citations. No issues.

## 7. Limitations / 8. Conclusion
No citations. No issues.

## Supplement (S18 is the only cited section)

`manuscript/AIJ_SUPPLEMENTARY_METHODS.md:214` — "Model Discovery Agent explicitly separates proposal from Bayesian inference, reports an expansion-component ablation and caches calls [24]." All three verified in v4 HTML: ablation "no M-open"; "never by the LLM"; "every call is cached for reproducibility". [7–9,32,40,41], [34,35,39], [26], [36–38] consistent with main-text use. The supplement cites only main-list numbers; every number 1–42 is cited in the main text. No issues.

## Reference-list metadata (all 42 checked)

All titles, authors, journals, volumes, years and page ranges match primary records (Crossref / arXiv / ACL / ICLR / PMLR / OpenLibrary), with these editorial notes:

### aij-cite-09 · optional
- Ref 7 (`AIJ_MANUSCRIPT.md:389`) lacks publisher. Proposed: "S. Muggleton, W. Buntine, Machine invention of first-order predicates by inverting resolution, in: Proceedings of the Fifth International Conference on Machine Learning, Morgan Kaufmann, 1988, pp. 339–352."

### aij-cite-10 · optional
- Ref 16 (`AIJ_MANUSCRIPT.md:398`) lacks proceedings name. Proposed: "K. Huang, Y. Jin, R. Li, M. Y. Li, E. Candès, J. Leskovec, Automated Hypothesis Validation with Agentic Sequential Falsifications, in: Proceedings of the 42nd International Conference on Machine Learning, PMLR 267 (2025) 25372–25437. https://proceedings.mlr.press/v267/huang25n.html"

### aij-cite-11 · optional
- Ref 39 (`AIJ_MANUSCRIPT.md:421`): the arXiv page lists the first author as "Enrique Crespo-Fernandez" (no accent); manuscript has "Crespo-Fernández". Match the source spelling unless the author's own usage with the accent is known.

### aij-cite-12 · optional
- Ref 40 (`AIJ_MANUSCRIPT.md:422`): the report cover identifies the GMU Center for Artificial Intelligence / Machine Learning and Inference Laboratory and shows both "92-3" and "P92-2 / MLI92-2"; the exact report number is ambiguous on the cover. Proposed: "J. Wnek, R. S. Michalski, Hypothesis-driven Constructive Induction in AQ17: A Method and Experiments, Report MLI 92-2, Center for Artificial Intelligence, George Mason University, Fairfax, VA, 1992. https://www.mli.gmu.edu/papers/91-95/92-3.pdf" (report number to be confirmed by the authors).

Other metadata notes (no action): Ref 4 Boden year 2004 retained (OpenLibrary 2003 vs Routledge 2004). Ref 33 Crossref shows online 2017-12-27, print 2018, vol 42 — manuscript's 2018 is correct. Ref 13 online 2023, issue 2024 — manuscript's 2024 is correct. Ref 42 issued Feb 2025, vol 339 — correct. Ref 2 Crossref lists first page only (88); 88–95 is correct.

## Cross-paper consistency pass

Citation numbering, supplement-to-main mapping and claim wording are consistent across both files. After aij-cite-01 and aij-cite-08 are applied, the abstract makes no claim the reference list cannot support. Abstract revisited at end: no change needed beyond those.

## Sections checked with no issues
Title/Abstract; 2.1 (except aij-cite-02); 2.2; 2.5; 3; 4; 5.1–5.7 with Figures 2–7 and Tables 4–6; 6; 7; 8; Data/Code availability; declarations; Supplement S1–S17, S19, S20 (no citations); S18.

## Finding index

| ID | Priority | Location | Type |
|---|---|---|---|
| aij-cite-01 | must-fix | Intro, line 21, [23–26] | wrong citation range |
| aij-cite-02 | should-fix | 2.1, line 37, [42] | claim exceeds source |
| aij-cite-03 | optional | Intro, line 21, [36–38] | citation precision |
| aij-cite-04 | should-fix | 2.3, line 49 | missing predecessor (Langley et al. 1987) |
| aij-cite-05 | should-fix | ref 22, line 404 | incomplete venue (ICML 2026 position) |
| aij-cite-06 | should-fix | ref 23, line 405 | unverifiable PMLR volume |
| aij-cite-07 | should-fix | 2.3/2.4, line 49 | missing essential reference (LLM-SR) |
| aij-cite-08 | should-fix | 2.4, line 59 | missing adjacent work (Shi et al. 2026) |
| aij-cite-09 | optional | ref 7, line 389 | missing publisher |
| aij-cite-10 | optional | ref 16, line 398 | missing proceedings name |
| aij-cite-11 | optional | ref 39, line 421 | author-name spelling |
| aij-cite-12 | optional | ref 40, line 422 | institution/report number |

Total: 12 findings (1 must-fix, 6 should-fix, 5 optional).

## Unresolved checks and coverage limits

- Direct landing pages blocked (HTTP 403 or login redirect): Springer (ref 8), Nature (refs 13, 18, 19, 21), ScienceDirect (ref 42), Routledge (refs 3, 4), MIT Press (ref 31), ACM DL (ref 7), PhilSci-Archive (ref 22). Each was verified instead through Crossref, Europe PMC, OpenLibrary, arXiv, the Edinburgh record or the ICML site. These are secondary-but-authoritative index records, not the publisher pages.
- Ref 7 page range (339–352) rests on the ACM DL index entry (10.5555/3091765.3091809) as shown in search results and the author PDF's existence; the ACM record page itself was not readable, and the author PDF (https://www.doc.ic.ac.uk/~shm/Papers/cigol.pdf) had non-extractable font encoding.
- PMLR volume for ICML 2026 (refs 22, 23) cannot be verified until PMLR publishes it.
- PhilSci-Archive item 28024 deposit date and item type: unverified (site rejected access); existence confirmed only via search-index title.
- Books (refs 3, 4, 30, 31) verified for metadata only, not re-read.
- Full texts read: refs 22, 24, 25, 33, 34, 35, 39, 40. All other claim checks rely on abstracts and proceedings/landing metadata, not full rereading.
- Whether Shi et al. (aij-cite-08) name Zahavy explicitly: unverified from the fetched excerpt.
- dblp API returned empty responses (rate-limited); Semantic Scholar API returned 429. Neither was needed for a final determination.
- tokensave MCP was unavailable this session (connection closed); no code analysis was required for this domain.
