# aij-guard review: overguarding in the AIJ manuscript

Reviewer: aij-guard (domain: overguarding — excessive caveats, repeated disclaimers, defensive framing, unnecessary hedging; preserve necessary scientific boundaries; propose direct positive wording without overclaim).
Date: 2026-09-10. Read-only review; no manuscript, code, data or git changes were made.

**HEAD:** `0214bc592aa55c92e5aaeffd298fbe22b07f3e3c` (branch `nmi-minimal-targeted-sensitivity-v1`; AIJ manuscript and supplement unmodified in the working tree at review time).

## Coverage

Read in full:
- `manuscript/AIJ_MANUSCRIPT.md` (424 lines), including all seven figure captions, Tables 1–6, declarations and availability statements.
- `manuscript/AIJ_SUPPLEMENTARY_METHODS.md` (263 lines), S1–S20.

Supporting artifacts inspected:
- `manuscript/figures/aij/figure_3_cj5.png` (image) and `manuscript/figures/aij/source_data.json` (text annotations only) — figure text is minimal; caveats live in captions and prose.
- `experiments/nmi_realizer_audit_v1/analysis/condition_summary.csv` — used to confirm numbers that positive rewordings rely on (C3 aligned 400/400 and 100/100; blind binding 347/400, 100/100; C_rand aligned 52/400, 13/100; C_rand blind 57/400, 13/100; DeepSeek grammar aligned 15/96, blind 8/96; `mask_signature:relation_arity_3` removes all 100 held-out C3 worlds; `mask_signature:multi_argument_function` removes all 15 DeepSeek worlds).
- `reports/AIJ_NUMERICAL_CHECKS.json` — B4 success 142 confirmed as pass.
- `reports/AIJ_CLAIM_REGRESSION_AUDIT.md` and `docs/publication/NMI_REJECTION_LESSON.md` — background only, not independent verification.

Coverage limits:
- Cover letter and availability files outside the manuscript (`manuscript/AIJ_COVER_LETTER.md`, `AIJ_DATA_AVAILABILITY.md`, `AIJ_CODE_AVAILABILITY.md`, `AIJ_DECLARATION_OF_GENERATIVE_AI.md`) were not reviewed.
- PDF build output not reviewed.
- Figures 1, 2, 4, 5, 6, 7 images not inspected pixel by pixel; their captions were.
- The tokensave MCP server failed to connect this session (CONNECTION_CLOSED); targeted greps and file reads were used instead.

## Overall verdict

The manuscript is scientifically well bounded and no caveat is factually wrong. The problem is repetition: the same eight or so boundary statements recur three to five times each in the main text, and the "X, not Y" negative-contrast closer appears on 22 distinct main-text lines (29 regex hits) and 22 more in the supplement. The effect is a paper that reads as continually pre-empting an objection rather than stating what it did. Every finding below proposes keeping one authoritative site for each caveat (usually the definitional Methods paragraph plus Section 7) and stating the positive result elsewhere. No proposal raises any claim beyond the frozen evidence.

Hedge-marker counts (main text, `grep`): "not" 52; "does not" 11; "do not" 10; "are not" 8; "is not" 7; "rather than" 6; "cannot" 6; "not a" 5; "explicitly" 4; "deliberately" 2. Lines with the ", not Y" pattern: 25, 29, 71, 79, 95, 146, 152, 154, 160, 180, 190, 196, 208, 216, 254, 287, 293, 305, 313, 333, 345, 347.

Priority legend: must-fix / should-fix / optional. All findings are editorial (tone/redundancy) unless labelled otherwise; none is a factual error.

---

## Title / Abstract

Checked. One should-fix. Revisited at the end (see "Abstract revisited").

### aij-guard-01 · Abstract, line 13 · should-fix
Quote: "Structured composition succeeded in all 400 known-family worlds and 100 worlds from one search-side held-out family, under a hand-authored, family-aligned realization library that already contained the held-out basis."
Reasoning: Correct and necessary once, but the sentence buries the result under three stacked qualifiers ("hand-authored", "family-aligned", "already contained the held-out basis"). One qualifier suffices in the abstract since Sections 4.3, 5.3 and 7 give the rest.
Proposed: "Structured composition succeeded in all 400 known-family worlds and 100 held-out worlds, using a hand-authored realization library that already contained the held-out basis."

## 1. Introduction

Lines 19–27: no issues; the qualifiers define the estimand.

### aij-guard-02 · Introduction, line 29 · should-fix
Quote: "These are informative results about the implemented paths, not a competition over general reasoning ability."
Reasoning: No reader of a paper about a frozen 14B model in synthetic worlds assumes a general reasoning competition. The sentence defends against an objection the paper has not invited. The next sentence already gives the positive framing.
Proposed: delete the sentence; the paragraph then reads "...no aggregate advantage over random composition. The methodological value of these results is that the same end-to-end scoring rule can be joined to evidence explaining what was actually evaluated."

## 2. Background and related work

### aij-guard-03 · 2.2, line 45 · should-fix
Quote: "Representation repair and component evaluation already coexist in these research programs."
Reasoning: A closing concession that pre-empts a novelty objection instead of stating the relation. The preceding sentence already draws the distinction ("Their evaluation targets adaptation...; ours is the provenance...").
Proposed: "We build on that coexistence by auditing a single committed artifact rather than an adapting agent." Or delete the sentence.

### aij-guard-04 · 2.3, line 49 · should-fix
Quote: "This division of labor is explicit; it should not be collapsed into an undifferentiated claim of model reasoning."
Reasoning: "Should not be collapsed" is admonitory and aimed at unnamed readers, not at FunSearch. Editorial tone, not an error.
Proposed: "FunSearch makes this division of labor explicit; our provenance records make the same division checkable at the level of the scored artifact."

### aij-guard-05 · 2.5, line 65 · should-fix
Quote: "This distinguishes evaluation targets, without claiming that adjacent work excludes artifact provenance."
Reasoning: The trailing clause disclaims a claim never made. Defensive.
Proposed: "This distinguishes our evaluation target from theirs."

### aij-guard-06 · 2.2, line 43 · optional
Quote: "Whether a graph is admitted by a declared structural language is decidable in our implementation; whether its predictive function is inexpressible by every possible incumbent expression is a different question. Our membership certificate addresses the former."
Reasoning: This structural-versus-functional caveat also appears at 3.2 line 85, Section 7 line 345, S1 line 10 and S19. Three main-text sites is one too many. Section 3.2 is the definitional home; Section 7 is the limits home.
Proposed: "Our membership certificate is decidable: it tests whether a graph is admitted by a declared structural language (Section 3.2)."

Lines 35–37, 51, 55–59, 63: no issues. Line 51 ("Their success is compatible with a wholly deterministic path...") previews a result inside Related Work but motivates the CJ5 design and reads acceptably.

## 3. Formal framework

### aij-guard-07 · 3.3, line 114 · should-fix (duplicate of 5.1 line 216)
Quote: "If the selected comparator is exact on every scored hidden control case, positive error reduction is impossible; a zero control rate then checks construction-specific consistency rather than estimating a general false-positive rate."
Reasoning: Restated almost verbatim with the data at 5.1 line 216 ("The zero control verdicts are therefore construction-specific checks of the assay, not a measured zero false-positive rate for noisy scientific discovery."). Keep the version attached to the evidence (5.1) and reduce 3.3 to the mechanism.
Proposed for line 114: "If the selected comparator is exact on every scored hidden control case, positive error reduction is impossible (Section 5.1)."

### aij-guard-08 · 3.3, line 116 · optional
Quote: "The gates are an operational contract for these noiseless worlds. The thresholds are not a statistical error-control theorem. No semantic creativity score, explanation quality, model confidence or embedding distance enters J."
Reasoning: The middle sentence denies something no reader would infer from a table of fixed constants. The third sentence is a useful positive statement.
Proposed: "The gates are an operational contract with frozen thresholds for these noiseless worlds. No semantic creativity score, explanation quality, model confidence or embedding distance enters J."

### aij-guard-09 · 3.3, line 89 and 6.4, line 339 · should-fix (main-text duplicate)
Quote (3.3, line 89): "The original commitment digest and timestamp were not persisted. The present audit therefore reconstructs commitment payloads and verifies scored content, rather than independently authenticating the historical reveal order."
Quote (6.4, line 339): "In the historical CJ5 runner, commitment precedes hidden-loss evaluation in control flow, but the original commitment timestamp and digest were not retained in the candidate result. Recording those events at runtime would strengthen a future implementation."
Reasoning: The same disclosure appears in 3.3, 6.4, S8 line 81, S19 line 232 and S20 line 261. Section 3.3 is the right main-text home (it defines the commitment). In 6.4 only the forward-looking recommendation adds anything.
Proposed for 6.4: "Recording the commitment digest and timestamp at runtime, which the historical CJ5 runner did not do (Section 3.3), would strengthen a future implementation."

### aij-guard-10 · 3.1, line 79 · optional
Quote: "They are not interchangeable. ... Exhaustiveness applies to P₀, not to every function expressible under A₀. Nor do we assume that all observation-optimal programs make identical interventional predictions."
Reasoning: Three negations in one paragraph; each is a real boundary, and S1 repeats them for the supplement. Acceptable as is. If tightened, fold the first into the definition.
Proposed: "A₀ specifies admissible structures, whereas P₀ specifies the actual executable comparators examined. ... Exhaustiveness applies to P₀ alone. Observation-optimal programs need not agree on interventions; all reported gains refer to the selected h₀*."

3.2 line 85, 3.4 lines 120–136, Tables 1–2 and captions: no issues. Line 122 ("It does not imply that the component is irrelevant under every alternative design") is the correct one-time statement of replay semantics.

## 4. Experimental framework

### aij-guard-11 · 4.2, line 152 · should-fix
Quote: "B2/B3 and the value-only condition are structural controls, not fair contests over universal capability: their reachable representations cannot satisfy J1."
Reasoning: "Not fair contests over universal capability" is a straw objection. The colon clause is the whole justification. Figure 3 caption and Table 4 already mark these as controls. S4 line 39 states the same for the supplement.
Proposed: "B2/B3 and the value-only condition are structural controls: their reachable representations cannot satisfy J1."

### aij-guard-12 · 4.2, line 154 and 5.2, line 237 · should-fix (duplicate)
Quote (4.2, line 154): "This comparison estimates the effect of the representation source on the complete pipeline, not the necessity of downstream model reasoning."
Quote (5.2, line 237): "The result shows sensitivity to representation input in that path; it does not identify a necessary contribution from the second model call."
Reasoning: Same caveat twice. Keep it once, with the result.
Proposed for 4.2: "This comparison estimates the effect of the representation source on the complete pipeline."
Proposed for 5.2 (positive form): "The result establishes that success in this path is driven by the representation input, with the second model call's fields enforced by the scaffold."

### aij-guard-13 · 4.3 line 180; Fig. 4 caption line 254; 5.3 line 258; 7 line 345 · must-fix (most repeated caveat)
Quotes:
- line 180: "The held-out family therefore tests search-side structural transfer to one adjacent arity-three construction, not discovery of an unseen algebraic form."
- line 254 (Fig. 4 caption): "The held-out algebraic basis was already supplied."
- line 258: "The supplied inventory defines the scope of this holdout: the graph-search target was withheld during known-family confirmation, whereas the triadic realization basis was already available. The result establishes transfer of a bounded graph-search procedure to an adjacent structure under that realization language."
- line 345: "The single held-out family is conceptually adjacent and its basis is pre-supplied."
Reasoning: With the abstract, this boundary appears five times in the main text, plus Table 3 row 1, 5.6 line 303 and Fig. 7 caption (the triadic mask), plus S7 and S8. The signature-mask result (masking `relation_arity_3` removes all 100 held-out successes; confirmed in `experiments/nmi_realizer_audit_v1/analysis/condition_summary.csv`) already proves the point empirically, so the prose need not keep re-asserting it. Keep: abstract, 4.3 line 180 (definitional), 7 line 345 (limits), and the 5.6 mask result. Remove from the 5.3 paragraph and the Fig. 4 caption.
Proposed for line 258: replace the paragraph with "The held-out result therefore establishes transfer of the graph-search procedure to an adjacent arity-three structure whose realization basis was in the frozen inventory (Table 3)."
Proposed for Fig. 4 caption: delete "The held-out algebraic basis was already supplied."

### aij-guard-14 · 4.3 line 162; 5.3 line 256; Fig. 4 caption line 254 · should-fix (triplicate)
Quotes:
- line 162: "Their contrast is between complete search-and-selection policies."
- line 256: "This estimates a complete-policy contrast: organized traversal and outcome-blind fitted ranking together access successful motif triggers more reliably than random paths with structural-hash selection."
- line 254 (caption): "The C3/random contrast includes traversal and selection, not proposal source alone."
Reasoning: Three main-text statements plus S6 line 55. Line 256 is the best one because it says positively what the contrast shows. Keep 4.3 (design) and 5.3 (result); cut the caption's negative clause.
Proposed for Fig. 4 caption: "The C3/random contrast compares complete search-and-selection policies."

### aij-guard-15 · 4.5, line 200 · should-fix
Quote: "Candidate rows describe attrition, never independent replication. ... Family rates are descriptive: many seeds within co-designed generators do not establish breadth over independently authored domains."
Reasoning: The candidate-versus-world point already appears at 3.3 line 112, Fig. 3 caption, 5.7 line 313 and 7 line 349 (five main-text sites, plus S1, S10, S16). The generalization limit belongs in Section 7, where it already sits at lines 345 and 351. In a statistical-analysis paragraph, state the units and stop.
Proposed: "World-level counts and rates are primary; candidate rows describe attrition. ... Family rates are descriptive."

### aij-guard-16 · 4.1 line 146 and 7 line 349 · should-fix (duplicate)
Quote (7, line 349): "Public Git freezes also lack an independent registry timestamp."
Reasoning: Line 146 already says "These public commits are not independent registry timestamps; we describe the experiments as commit-frozen, not formally preregistered." S11 line 113 repeats it in full. The Limitations sentence adds nothing.
Proposed: delete the sentence at line 349; keep line 146 as written.

### aij-guard-17 · 4.5, line 196 · optional
Quote: "It tests the implemented content path, not a retrained or redesigned system."
Reasoning: The "implemented path" scope is stated at 3.4 line 122, here, 5.4 line 279 and 7 line 349. Here it can be positive.
Proposed: "It tests the content path as implemented."

4.4 (lines 184–192): no issues. "Not compute-matched" appears once in the main text, which is right. Table 3 and caption: no issues.

## 5. Results

### 5.1 (lines 206–216, Fig. 2)
No issues beyond aij-guard-07's counterpart at line 216, which should remain as the single site. Line 214 ("Thus fit plus structural departure plus predicted separation is insufficient") is a model of the positive form the rest of the paper should use.

### 5.2 (lines 220–237, Table 4, Fig. 3)
See aij-guard-12. One optional item:

### aij-guard-18 · 5.2, line 235 · optional
Quote: "Both external proposal conditions achieve 35.5% world success. Their shared aggregate does not imply identical candidate trajectories."
Proposed: "Both external proposal conditions achieve 35.5% world success, but their candidate trajectories differ."

### 5.3 (lines 241–258, Table 5, Fig. 4)
See aij-guard-13 and aij-guard-14. Otherwise no issues; line 256 is good.

### 5.4 (lines 262–281, Table 6, Fig. 5)
No issues. Line 279 is a clear positive attribution claim and is correctly scoped.

### 5.5 (lines 285–297, Fig. 6)

### aij-guard-19 · 5.5 line 287 and 6.3 line 333 · should-fix (duplicate)
Quote (5.5, line 287): "These observations identify an execution boundary, not the absence of an internally useful conceptual proposal."
Quote (6.3, line 333): "The appropriate response to pre-execution failure is an attrition diagnosis, not an inference about all conceptual ability."
Reasoning: Same idea twice, plus 7 line 347. Section 5.5 should report the boundary; 6.3 should draw the lesson. The 6.3 sentence is the argumentative one; 5.5 can be shortened to the fact.
Proposed for 5.5: "These observations locate the failure at the execution boundary."

### aij-guard-20 · 5.5, line 293 · should-fix
Quote: "This is evidence of occasional executable use of a supplied representation, not a reliable ceiling or independent representation invention."
Reasoning: "Not ... independent representation invention" denies a claim the design excludes (the representation was supplied by construction). The 3/40 result supports a modest positive statement, with the sample size as the only needed qualifier. S12 line 152 keeps the "minimum positive control" wording for the supplement.
Proposed: "This establishes that model-authored expressions and actions can occasionally pass all gates when the representation is supplied; with 40 worlds it is a floor, not a ceiling."

### 5.6 (lines 301–309, Fig. 7)

### aij-guard-21 · 5.6 line 305; Fig. 7 caption line 309; 3.4 line 122 · should-fix (triplicate)
Quotes:
- line 305: "We retain that intervention as a negative control, not the principal evidence of an irreplaceable realizer."
- line 309 (caption): "Incumbent substitution is retained only as a structural negative control in the supplement."
- line 122: "substituting the comparator expression necessarily removes J3 separation and is a structural negative control."
Reasoning: Three main-text statements of the same point (plus S17 line 202). The intervention is not shown in Fig. 7, so the caption sentence is pure disclaimer.
Proposed: delete the caption sentence. Keep line 305 but shorten: "That intervention is a structural negative control (Section 3.4)."

### aij-guard-22 · 5.6 line 305; Fig. 7 caption line 309; 4.5 line 198; 7 line 349 · should-fix (quadruplicate)
Quotes:
- line 198: "Graphs and slots stay fixed; adaptive re-search is outside the intervention."
- line 305: "All masks use fixed candidate slots rather than renewed adaptive search, so they measure dependence of archived artifacts on the specified realization policy."
- line 309 (caption): "All interventions fix archived candidate slots; no adaptive re-search occurs."
- line 349: "They do not estimate how an adaptive search would compensate after losing a basis."
Reasoning: Four main-text sites plus S17 line 208. Keep 4.5 (method) and 7 (limit). The caption and 5.6 restatements can go, or 5.6 can keep its positive half.
Proposed for line 305: "All masks act on fixed candidate slots, so they measure dependence of the archived artifacts on the specified realization policy."
Proposed for caption: delete "All interventions fix archived candidate slots; no adaptive re-search occurs."

Line 303 ("A zero marginal loss can reflect another available realization route; it is not proof that a signature is universally unnecessary."): acceptable once, because the unification redundancy example needs it. Optional shortening: "A zero marginal loss can reflect another available realization route, as for shared-rule binding in unification worlds."

### 5.7 (line 313)

### aij-guard-23 · 5.7, line 313 · optional
Quote: "These row counts establish reconstruction coverage, not independent experimental replication."
Reasoning: Same point at 7 line 349 ("Deterministic reconstruction strengthens internal traceability but is not independent replication."). Keep Section 7's version.
Proposed: "These row counts establish reconstruction coverage."

## 6. Discussion

6.1, 6.2, 6.3: no issues beyond aij-guard-19. Section 6.2 is the strongest positive writing in the paper.

### aij-guard-24 · 6.4, line 337 · optional
Quote: "Each ingredient has precedent. Their combination makes a claim checkable against a specific artifact: ..."
Reasoning: Opening the "what the procedure adds" section with a concession is defensible and honest, but the order can lead with the contribution.
Proposed: "The combination of these ingredients, each with precedent, makes a claim checkable against a specific artifact: ..."

### aij-guard-25 · 6.4, line 339 · should-fix
Quote: "The validator checks record structure, source hashes and reproduction of this example; it does not certify scientific novelty or manufacture missing timing evidence."
Reasoning: "Manufacture missing timing evidence" is defensive phrasing about a failure mode nobody would attribute to a validator, and "does not certify scientific novelty" already appears in the Table 2 note (line 134), S18 and S20 line 263. Combine with aij-guard-09.
Proposed: "The validator checks record structure, source hashes and deterministic reproduction of this example. Recording the commitment digest and timestamp at runtime, which the historical CJ5 runner did not do (Section 3.3), would strengthen a future implementation."

## 7. Limitations and 8. Conclusion

Section 7 is the correct consolidation site and its sentences are mostly unique there. Duplicates removable per aij-guard-16 and aij-guard-22 are covered above; aij-guard-23 keeps Section 7's version. Line 351 (closing boundary sentence) is appropriate. Conclusion (line 355): no issues; it states the contribution positively.

## Declarations, availability, supplement

### aij-guard-26 · Data availability, line 359 · optional
Quote: "The evidence release is distinct from the present manuscript revision."
Reasoning: Unclear what objection this answers; the previous sentences already explain that the release name is historical and that the code tag is separate.
Proposed: delete, or clarify: "The evidence release predates and is unchanged by the present manuscript revision."

### aij-guard-27 · Declaration of generative AI, line 379 · optional
Quote: "A stable deployed-build identifier was not available for the conversational assistance, so no finer version claim is made."
Reasoning: Honest and harmless; slightly over-explained.
Proposed: "No stable build identifier was available for the conversational assistance."

### aij-guard-28 · S4, line 35 · should-fix
Quote: "This high-level alignment motivated CJ5 and is not hidden as a limitation."
Reasoning: "Is not hidden as a limitation" is a defensive aside about the authors' own candour.
Proposed: "This high-level alignment motivated the generic-primitive design of CJ5."

### aij-guard-29 · S11, lines 125 and 140 · should-fix (duplicate within one section)
Quote (line 125): "The condition therefore tests sensitivity to the original completion cap; it is not compute-matched."
Quote (line 140): "DeepSeek native is explicitly not compute-matched, and the Phi-4 sensitivity changes serving engine together with precision."
Reasoning: Same section, same caveat twice; main text line 188 also states it. Keep line 125 for Phi-budget and line 140 only for the DeepSeek/Phi-8-bit confound. Drop "explicitly" (the word appears four times in the main text and twice in the supplement and reads as protesting).
Proposed for line 140: "DeepSeek native is not compute-matched to the historical cap, and the Phi-4 8-bit sensitivity changes serving engine together with precision."

### aij-guard-30 · S17, line 208 · should-fix
Quote: "The audit fixes candidates that were originally selected under the aligned realizer and therefore does not estimate how search would adapt if rerun under a different realizer. It is a causal sensitivity of the archived end-to-end verdict, not a replacement confirmatory study, a model-conceptualization test or evidence of external scientific generalization."
Reasoning: A three-item list of things the audit is not, after a sentence that already gives the boundary.
Proposed: "The audit fixes candidates originally selected under the aligned realizer. It is a causal sensitivity of the archived end-to-end verdict and does not estimate how search would adapt under a different realizer."

### aij-guard-31 · S18, line 214 · should-fix
Quote: "We make no priority claim for any individual ingredient or for the first combination across all AI literature."
Reasoning: "Across all AI literature" over-extends a disclaimer into something no author can assert either way. The preceding sentence already states the contribution as an implemented coupling.
Proposed: "We claim no priority for any individual ingredient."

### aij-guard-32 · S20, lines 236, 261, 263 · should-fix
Quotes:
- line 236: "The earlier unfilled template remains a capture checklist, not experimental evidence or a substitute for the schema."
- line 261: "Original commitment digest and timestamp were not persisted in the result or call ledger and remain null. Commit-before-hidden-loss ordering is supported by runner control flow; it is not an independently timestamped reveal event. No new timestamp is presented as historical evidence."
- line 263: "Neither mode establishes scientific novelty or verifies unavailable timing facts."
Reasoning: The timestamp point is stated four times within S20 alone (lines 240, 261 ×3, 263), and the template sentence disclaims a file no reader would mistake for evidence.
Proposed:
- line 236: "The earlier unfilled template is a capture checklist."
- line 261: "The original commitment digest and timestamp were not persisted and remain null; commit-before-hidden-loss ordering rests on runner control flow (Section 3.3)."
- line 263: delete the final sentence, or "Validation certifies reproduction of the record, not scientific novelty."

Supplement sections checked with no issues: S1, S2, S3, S5, S6, S7, S8, S9, S10, S12, S13, S14, S15, S16, S19. Their qualifiers are unique within the supplement and are the primary record for the corresponding main-text statements.

---

## Cross-paper consistency pass (overguarding domain)

No caveat contradicts another; the redundancy is consistent in content. Repetition tally across main text (supplement sites in parentheses):

| Boundary statement | Main-text sites | Proposed keep |
|---|---|---|
| Held-out basis pre-supplied (aij-guard-13) | Abstract, 4.3, Fig 4, 5.3, 7 (+S7, S8) | Abstract, 4.3, 7 |
| Candidates are attrition, not replicates (aij-guard-15, -23) | 3.3, 4.5, Fig 3, 5.7, 7 (+S1, S10, S16) | 3.3, Fig 3, 7 |
| Fixed slots, no adaptive re-search (aij-guard-22) | 4.5, 5.6, Fig 7, 7 (+S17) | 4.5, 7 |
| Incumbent substitution is a negative control (aij-guard-21) | 3.4, 5.6, Fig 7 (+S17) | 3.4, 5.6 short |
| Complete-policy contrast (aij-guard-14) | 4.3, 5.3, Fig 4 (+S6) | 4.3, 5.3 |
| Commitment timestamp not persisted (aij-guard-09, -25, -32) | 3.3, 6.4 (+S8, S19, S20 ×4) | 3.3, 6.4 forward-looking only |
| Zero controls are construction-specific (aij-guard-07) | 3.3, 5.1 (+S10) | 5.1 |
| Structural vs functional non-membership (aij-guard-06) | 2.2, 3.2, 7 (+S1, S19) | 3.2, 7 |
| Not preregistered / no registry timestamp (aij-guard-16) | 4.1, 7 (+S11) | 4.1 |
| Execution boundary, not conceptual inability (aij-guard-19) | 5.5, 6.3, 7 | 6.3, 7 |
| Representation source vs second-call necessity (aij-guard-12) | 4.2, 5.2 | 5.2 |

Global pattern: the ", not Y" closer on 22 main-text lines (25, 29, 71, 79, 95, 146, 152, 154, 160, 180, 190, 196, 208, 216, 254, 287, 293, 305, 313, 333, 345, 347). The proposals above remove or convert about half. The word "explicitly" (4 main-text uses, 2 supplement) can be dropped everywhere without loss.

## Abstract revisited

After the section pass, the abstract remains appropriately bounded; only aij-guard-01 is proposed. The sentence "The resulting evidence records distinguish validated system escape, model-authored content and dependence on supplied explanatory forms" and the closing sentence are positive statements that the body supports. No overguarding beyond the stacked qualifier.

## Unresolved checks

- Not re-verified: the AJ5 35.5% bootstrap intervals and the C3 versus C_rand interval values ([0.845, 0.895] and [0.80, 0.93]). The positive rewordings proposed here do not depend on them. (Unverified.)
- Outside this domain, for another reviewer: Section 5.6 says role/action-blind rebinding leaves C_rand with 57/400 known-family successes versus 52/400 under aligned replay. `experiments/nmi_realizer_audit_v1/analysis/condition_summary.csv` confirms both figures (aligned 52, blind 57), so blind rebinding gained five C_rand worlds. The manuscript's verb "retains 57/400" reads oddly for a gain. Not an overguarding issue, but the wording could mislead. (Verified numbers; wording concern only.)
- Figures 1, 2, 4, 5, 6, 7 images were not inspected pixel by pixel; captions were reviewed.
- Cover letter, standalone availability statements and generative-AI declaration files outside the manuscript were not reviewed.

## Three most consequential findings

1. **aij-guard-13** (must-fix): the held-out-basis caveat is stated five times in the main text and again in a figure caption, turning a clean transfer result into an apology. Keep three sites.
2. **aij-guard-22 with aij-guard-21** (should-fix): Section 5.6 and its figure caption carry four restatements of "fixed slots, no re-search" and three of "negative control", crowding out the actual localization result (signature masks and binding sensitivity), one of the paper's strongest positive findings.
3. **aij-guard-09, -25, -32** (should-fix): the unpersisted commitment timestamp is disclosed in 3.3, 6.4 and four times inside S20. One definitional disclosure plus one forward-looking recommendation is enough; the current density signals doubt about the reveal order that the runner control flow does not warrant.

## Finding index

| ID | Location | Priority |
|---|---|---|
| aij-guard-01 | Abstract L13 | should-fix |
| aij-guard-02 | Intro L29 | should-fix |
| aij-guard-03 | 2.2 L45 | should-fix |
| aij-guard-04 | 2.3 L49 | should-fix |
| aij-guard-05 | 2.5 L65 | should-fix |
| aij-guard-06 | 2.2 L43 | optional |
| aij-guard-07 | 3.3 L114 / 5.1 L216 | should-fix |
| aij-guard-08 | 3.3 L116 | optional |
| aij-guard-09 | 3.3 L89 / 6.4 L339 | should-fix |
| aij-guard-10 | 3.1 L79 | optional |
| aij-guard-11 | 4.2 L152 | should-fix |
| aij-guard-12 | 4.2 L154 / 5.2 L237 | should-fix |
| aij-guard-13 | 4.3 L180 / Fig4 L254 / 5.3 L258 / 7 L345 | must-fix |
| aij-guard-14 | 4.3 L162 / 5.3 L256 / Fig4 L254 | should-fix |
| aij-guard-15 | 4.5 L200 | should-fix |
| aij-guard-16 | 4.1 L146 / 7 L349 | should-fix |
| aij-guard-17 | 4.5 L196 | optional |
| aij-guard-18 | 5.2 L235 | optional |
| aij-guard-19 | 5.5 L287 / 6.3 L333 | should-fix |
| aij-guard-20 | 5.5 L293 | should-fix |
| aij-guard-21 | 5.6 L305 / Fig7 L309 / 3.4 L122 | should-fix |
| aij-guard-22 | 5.6 L305 / Fig7 L309 / 4.5 L198 / 7 L349 | should-fix |
| aij-guard-23 | 5.7 L313 | optional |
| aij-guard-24 | 6.4 L337 | optional |
| aij-guard-25 | 6.4 L339 | should-fix |
| aij-guard-26 | Data availability L359 | optional |
| aij-guard-27 | GenAI declaration L379 | optional |
| aij-guard-28 | S4 L35 | should-fix |
| aij-guard-29 | S11 L125/L140 | should-fix |
| aij-guard-30 | S17 L208 | should-fix |
| aij-guard-31 | S18 L214 | should-fix |
| aij-guard-32 | S20 L236/L261/L263 | should-fix |

Totals: 32 findings (1 must-fix, 21 should-fix, 10 optional).
