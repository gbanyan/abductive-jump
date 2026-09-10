# AIJ manuscript review: Readability domain (aij-read)

- Reviewer role: aij-read (readability: paragraph purpose, logical flow, missing definitions, terminology consistency, sentence complexity, accessibility for Artificial Intelligence journal readers)
- Date: 2026-09-10
- HEAD at review: `0214bc592aa55c92e5aaeffd298fbe22b07f3e3c`, branch `nmi-minimal-targeted-sensitivity-v1`
- Files reviewed in full: `manuscript/AIJ_MANUSCRIPT.md` (424 lines), `manuscript/AIJ_SUPPLEMENTARY_METHODS.md` (263 lines)
- Figures viewed: `manuscript/figures/aij/figure_1_assay.png` through `figure_7_worked.png` (all seven linked figures)
- Read-only review: no manuscript, code, data or git changes were made. Line numbers refer to `manuscript/AIJ_MANUSCRIPT.md` unless marked SUPP (`manuscript/AIJ_SUPPLEMENTARY_METHODS.md`).
- Prior `reports/AIJ_*` files were not used as verification.

Finding count: 32 IDs (aij-read-01 to aij-read-32; IDs 18 and 29 were checked and closed with no issue, see the "Checks closed without a finding" section). Actionable findings: 30.

Priority key: must-fix / should-fix / optional. "Error" means an inconsistency or undefined term a reader cannot resolve from the text; "editorial" means a preference that improves flow.

---

## 1. Title and abstract

### aij-read-01 (should-fix, error: undefined terms) — line 13
Quote: "external typed proposals produced validated escapes in 142" and "one search-side held-out family".
Reasoning: Neither phrase is defined in the abstract. A reader cannot tell that the proposals are designer-supplied (B4/B5, Section 4.2 line 150) or what "search-side" qualifies (explained only at line 180 and line 258).
Proposed replacement: "In 400 synthetic worlds, designer-supplied typed transformation proposals produced validated escapes in 142, compared with one each for two language-model proposal conditions. Structured composition succeeded in all 400 known-family worlds and in 100 worlds from one held-out family, under a hand-authored, family-aligned realization library that already contained the held-out algebraic basis."

### aij-read-02 (should-fix, error: wrong connective, undefined term) — line 13
Quote: "Conversely, historical self-composition failed before executable evaluation."
Reasoning: The preceding sentence concerns C3 replay; "Conversely" does not contrast with it. "Historical self-composition" (C_self) is not defined before line 162.
Proposed replacement: "By contrast, the original model-authored composition condition failed before any proposal reached executable evaluation."

### aij-read-03 (optional, editorial) — line 13
Quote: "A post-hoc inference-free replay reproduced all 2,400 candidate verdicts: deterministic components supplied the evaluated theories, ranking and interventions."
Reasoning: The colon asserts the conclusion without saying what the replay removed (model output; see line 196 and line 279).
Proposed replacement: "A post-hoc replay with all model output removed reproduced all 2,400 candidate verdicts, showing that deterministic components supplied the evaluated theories, ranking and interventions in that path."

---

## 2. Introduction

### aij-read-04 (optional, editorial) — line 29
Quote: "The experiments provide a deliberately exact setting for this analysis." and "Repairing a different model-proposal interface yields executable graph edits but no aggregate advantage over random composition."
Reasoning: "Exact" is ambiguous (it means noiseless and deterministic, per line 142). "A different model-proposal interface" refers to something not yet introduced.
Proposed replacement: "The experiments provide a deliberately noiseless, deterministic setting for this analysis." and "Repairing the output format of a model-proposal interface yields executable graph edits but no aggregate advantage over random composition."

No other Introduction issues. Paragraph purposes are clear and the three-part contribution statement at line 27 maps onto Sections 3, 4 and 5.

---

## 3. Related work

### aij-read-05 (optional, editorial) — line 43
Quote: "Our membership certificate addresses the former."
Reasoning: "Certificate" is first used here and only defined at line 85 ("The certificate concerns structural non-membership").
Proposed replacement: "Our structural membership check (Section 3.2) addresses the former."

Sections 2.1, 2.3, 2.4 and 2.5 checked with no issues.

---

## 4. Formal framework

### aij-read-06 (must-fix, error: undefined labels used before introduction) — line 89 and line 142
Quote: line 89 "In the historical CJ5 implementation, prediction precedes hidden-loss evaluation in the runner's control flow."; line 142 "AJ5 contains eight procedural families".
Reasoning: Line 89 is the first appearance of CJ5; AJ5 first appears at line 142. Neither label is expanded or introduced as an experiment series anywhere in the main text or supplement (grep confirmed no "(AJ5)"/"(CJ5)" expansion in either file). An AIJ reader meets both labels cold.
Proposed correction: add at the end of the Introduction (after line 27): "We report two commit-frozen experiment series: AJ5, which supplies atomic, family-level representation transformations, and CJ5, which composes generic local graph rewrites." Change line 89 to: "In the historical implementation of the compositional experiments (CJ5, Section 4.3), prediction precedes hidden-loss evaluation in the runner's control flow." Unverified: what the labels abbreviate; the authors should confirm if an expansion is wanted.

### aij-read-07 (should-fix, editorial: logical flow) — lines 89 to 95
Quote: "In the historical CJ5 implementation ... Supplementary S20 identifies recorded, reconstructed and unavailable fields." (three sentences inside line 89)
Reasoning: The commitment definition is interrupted by the caveat about the unpersisted digest and reconstruction before the reader has seen the gates or Table 1.
Proposed correction: move those three sentences to the end of Section 3.3 (after line 116) or into Section 3.4, where reconstructed provenance is discussed (line 120).

### aij-read-08 (should-fix, error: table/text inconsistency; punctuation) — line 95 and Table 1 row J1 (line 100)
Quote: line 95 "The implementation conjoins V(T) with each of J1-J5; the table shows the additional gate-specific requirements."; Table 1 J1 row "R∉A₀, with V(T)".
Reasoning: Text says V(T) applies to every gate J1 to J5, but the J1 row alone mentions V(T), implying it is J1-specific. Also "J1-J5" uses a hyphen whereas the rest of the paper uses en dashes (e.g. "J0–J5" line 262).
Proposed correction: J1 row: "R∉A₀". Add to the Table 1 note (line 106): "V(T) is conjoined with every gate J1–J5." Replace "J1-J5" with "J1–J5" at line 95, at line 297 ("J1-J2 and 21 pass J3-J5"), and at SUPP line 232.

### aij-read-09 (must-fix, error: terminology inconsistency, undefined term) — line 112
Quote: "The bounded expansion event is J(T)=J0∧J1∧J2∧J3∧J4∧J5. A world succeeds if at least one of its three retained candidates passes J. The jump success rate is the proportion of jump worlds that succeed."
Reasoning: The same event carries four names: "bounded expansion event" (line 112), "validated escape" (abstract, Sections 5 and 6), "jump success rate"/"jump worlds" (line 112, line 142) and "validated jump"/JSR/FJR (SUPP S1, S4, S10, S12). "Jump" is never defined in the main text. "Jump worlds" vs "control worlds" is only implicitly defined at line 144.
Proposed correction, insert after the J(T) sentence at line 112: "We call a world in which this event occurs a validated escape. Archived artifacts and the supplement use the historical term validated jump for the same event; jump worlds are worlds constructed so that an escape is reachable, and control worlds are worlds whose truth stays inside the incumbent program set."

### aij-read-10 (optional, editorial: repetition) — line 114 and line 216
Quote: line 114 "If the selected comparator is exact on every scored hidden control case, positive error reduction is impossible; a zero control rate then checks construction-specific consistency rather than estimating a general false-positive rate."; line 216 "Under this construction no candidate can achieve strictly positive error reduction. The zero control verdicts are therefore construction-specific checks of the assay, not a measured zero false-positive rate..."
Reasoning: Near-identical argument in both places.
Proposed correction: keep the Section 5.1 version (line 216) and delete the last sentence of line 114.

### aij-read-11 (optional, editorial: format) — line 136
Quote: "Procedure box. Freeze the evaluated object and public/hidden contract; trace each scored field ...; report the changed fields, verdict and supplied forms."
Reasoning: Six steps in one semicolon chain.
Proposed correction: format as a numbered list of six steps with the same wording.

---

## 5. Methods and experimental setup

### aij-read-12 (should-fix, error: orphan condition) — lines 150 and 152
Quote: line 150 "A separate value-only control also remains within the incumbent language."; line 152 "B2/B3 and the value-only condition are structural controls".
Reasoning: The value-only control appears in no table (Table 4 lists B0–B5), no figure (Figure 3 shows B0–B5) and no supplement section (SUPP S4 lists B0–B5 only). Its results are never reported.
Proposed correction: delete both mentions, or add where it is reported. If it is the "A6" condition of SUPP line 87 (see aij-read-26), say so in both places, e.g. line 150: "A separate value-only control (historical identifier A6, Supplementary S9) also remains within the incumbent language." Unverified: whether A6 and the value-only control are the same condition.

### aij-read-13 (should-fix, error: undefined label) — line 184
Quote: "Temperature is 0.2 except AJ5 B1 mutation plans and factorial P0 at 0.7".
Reasoning: P0 is undefined in the main text; the factorial at line 154 uses descriptive names (model-proposed, external-portfolio, supplied-correct). P0/P1/P2 appear only in SUPP S4 line 37.
Proposed replacement: "Temperature is 0.2 except AJ5 B1 mutation plans and the model-proposed arm of the representation-source factorial (P0 in Supplementary S4), which use 0.7".

### aij-read-14 (should-fix, error: undefined term) — line 186
Quote: "Legacy-interface conditions vary precision/serving, output budget, model or one validator-only repair."
Reasoning: "Legacy interface" is not defined before use. It refers to the historical C_self prompt and parser (line 162, line 285, SUPP S13).
Proposed replacement: "Legacy-interface conditions reuse the historical self-composition prompt and parser of Section 4.3 and vary precision/serving, output budget or model, or add one validator-only repair."

### aij-read-15 (should-fix, error: missing introduction of second model; undefined "native") — line 188
Quote: "The DeepSeek service identifies `deepseek-ai/DeepSeek-V4-Flash-Vision-Exp` ... Native reasoning is returned separately from the final parser answer."
Reasoning: The paragraph introduces a second model with no statement of its role or which conditions use it. "Native" is unexplained until SUPP S11 line 123.
Proposed correction: open the paragraph with "The sensitivity panel adds one second model checkpoint, used in the matched, native, supplied-representation and grammar-constrained conditions." Replace the reasoning sentence with "In the native condition the service returns its reasoning text separately from the final answer that the parser reads."

### aij-read-16 (should-fix, error: missing prerequisite fact) — line 190
Quote: "This replaces the proposal-plus-explanation allocation, preserving six calls per world, but changes interface and token allocation together."
Reasoning: The historical two-calls-per-slot allocation is stated only in SUPP S9 line 87; the main-text reader cannot see why six calls is the preserved number.
Proposed replacement: "This replaces the historical two calls per slot, one proposal and one explanation, so each world still receives six calls, but it changes interface and token allocation together."

### aij-read-17 (optional, editorial: cryptic reference) — line 162
Quote: "Conditional ceilings and unequal-semantics references are reported separately in the supplement."
Reasoning: C5 is never named in the main text; the sentence is opaque without SUPP S6 line 53.
Proposed replacement: "A supplied-target conditional ceiling (C5) is reported in Supplementary S6 because its operation semantics differ from C1."

Sections 4.1, 4.3 realizer table (Table 3) and 4.5 checked with no other issues. The eleven-policy count at line 198 reconciles with Table 3 (1 aligned, 1 substitution, 1 rebinding, 8 masks for nine signatures minus the incumbent).

---

## 6. Results

### 6.1 Section 5.1 with Figure 2 (file `figure_7_worked.png`)

### aij-read-19 (should-fix, error: undefined archive labels) — line 212 (Figure 2 caption)
Quote: "Archived held-out seed 40000 supplies the observations, committed test-0 and separate fals-0 outcome."
Reasoning: "test-0" and "fals-0" are archive identifiers (SUPP S20 line 240) with no gloss in the main text. Figure content (1,944 / 2,268 / 1,620; edits reify edge, arity 3, bind z, bind w) matches lines 206 to 208.
Proposed replacement: "Archived held-out seed 40000 supplies the observations, the committed intervention case (archive label test-0) and the separate falsification case (fals-0)."

### aij-read-20 (should-fix, error: ambiguous notation) — line 214
Quote: "In AJ5, B4/B5 likewise retain 112/110 control candidates through J3, with none surviving J4."
Reasoning: "112/110" reads as a fraction.
Proposed replacement: "In AJ5, B4 and B5 likewise retain 112 and 110 control candidates, respectively, through J3, with none surviving J4."

### 6.2 Section 5.2 with Table 4 and Figure 3 (file `figure_2_aj5.png`)

### aij-read-21 (should-fix, error: apparent contradiction) — line 237
Quote: "The representation-source factorial yields 0/400 for model-proposed representations, 142/400 for the external portfolio and 400/400 for supplied-correct representations."
Reasoning: Two paragraphs earlier (line 235, Figure 3) B0 and B1 each score 1/400. A reader will read 0/400 for "model-proposed" as a contradiction unless told this is a separate run (SUPP S4 line 37: P0/P1/P2 factorial).
Proposed replacement: "The representation-source factorial, a separate run from B0 and B1, yields 0/400 for model-proposed representations, 142/400 for the external portfolio and 400/400 for supplied-correct representations."

Figure 3 panel labels and caption agree with the retention counts at line 235 (B4: 823/573/270/154; B5: 838/562/262/145; B0: 65/22/4/1; B1: 546/375/118/1).

### 6.3 Section 5.3 with Table 5 and Figure 4 (file `figure_3_cj5.png`)

### aij-read-22 (optional, editorial: label mismatch) — line 254 (Figure 4 caption) and line 309 (Figure 7 caption)
Quote: Figure 4 y-axis label "Random policy"; Figure 7 labels "Random known (400)", "Random held-out (100)", "Model panel (96)"; text and Table 5 use "C_rand".
Proposed correction: add "(C_rand, labelled Random policy)" to the Figure 4 caption, or relabel the figure rows "C_rand (random policy)". For Figure 7, add to the caption "Random denotes C_rand; Model panel denotes the grammar-constrained condition."

Counts and the 0.87 paired differences (348/400, 87/100) check against Figure 4 (400/400 vs 52/400; 100/100 vs 13/100).

### 6.4 Section 5.4 with Table 6 and Figure 5 (file `figure_4_provenance.png`)

### aij-read-23 (should-fix, error: one condition, four names) — line 186, Table 6 header line 264, line 293, SUPP S4/S12
Quote: line 186 "A separate 40-world positive control"; Table 6 "Supplied-representation sensitivity source"; line 293 "The separate supplied-representation DeepSeek control"; SUPP "P2", "balanced DeepSeek supplied-representation control", "minimum positive control".
Proposed correction: use "supplied-representation control" everywhere. Line 186: "A separate 40-world supplied-representation control, which serves as a positive control for executable use of a supplied graph, supplies the correct representation while evaluating the model-authored expression and action without overwrite." Table 6 header: "Supplied-representation control source".

Figure 5 content (2,400/2,400 verdicts; 500/500 jump worlds) matches line 279.

### 6.5 Section 5.5 with Figure 6 (file `figure_5_interface.png`)

### aij-read-24 (optional, editorial: punctuation) — line 289
Quote: "Wilson 95% interval 9.7-24.2%".
Reasoning: Hyphen; the supplement uses en dashes ("9.7–24.2%", SUPP line 166; "2.6–19.9%", SUPP line 152).
Proposed replacement: "Wilson 95% interval 9.7–24.2%".

Counts at lines 289 and 291 (4,608; 3,939; 280/288; 236; 21; 66/15/14/1) match Figure 6 panels a to c.

### 6.6 Sections 5.6 and 5.7 with Figure 7 (file `figure_6_realizer.png`)

Figure 7 values (347/400, 100/100, 57/400, 13/100, 8/96; masks 100/100/50/50/50/50/50/0) match lines 301 and 303. No issues.

---

## 7. Discussion

### aij-read-25 (optional, editorial: ambiguous verb) — line 321
Quote: "remaining within that language does not resolve a claim of invention."
Proposed replacement: "remaining within that language does not by itself settle whether the construction counts as invention."

Sections 6.2 to 6.4 checked with no issues. "A fourth path" at line 327 follows correctly from the three cases listed at line 325.

---

## 8. Limitations and Conclusion

No issues. Each limitation paragraph maps to a results subsection; the conclusion restates the contribution without new terms.

---

## 9. Supplement and declarations

### aij-read-26 (should-fix, error: undefined label) — SUPP line 87
Quote: "AJ5 therefore executed 32,400 prospectively specified calls plus 3,600 A6 calls."
Reasoning: "A6" is defined nowhere in either file (grep: single occurrence).
Proposed correction: gloss or delete. If A6 is the value-only control of main-text line 150: "plus 3,600 calls for the value-only control (historical identifier A6)". Unverified: the identity of A6.

### aij-read-27 (should-fix, error: unexpanded acronyms) — SUPP lines 12, 39, 95, 103, 148
Quote: SUPP line 95 "Two-sided Wilson intervals summarize JSR/FJR."; SUPP line 39 "their zero JSR"; SUPP line 103 "rho_J=(JSR_C3−JSR_C0)/(JSR_C1−JSR_C0)"; SUPP line 148 "JSR was 0/400".
Reasoning: S1 gives the full names but never the acronyms.
Proposed correction at SUPP line 12: "The jump success rate (JSR) is the proportion of jump worlds with a validated candidate. The false-jump rate (FJR) applies the identical decision to control worlds..."

### aij-read-28 (optional, editorial: unused definition) — SUPP line 12
Quote: "Abductive precision is the number of validated candidates divided by candidates passing J0–J3."
Reasoning: Defined once and never used in either file.
Proposed correction: delete, or keep and mark as a glossary term reported in archived tables.

### aij-read-30 (optional, editorial: duplication) — SUPP lines 117 and 121
Quote: line 117 "An outcome-blind SHA-256 ranking selected 12 of the 50 historical CJ5 seeds ... fixed 96-world paired panel. The positive control used the first five selected seeds in each family (n=40)."; line 121 "The new protocol used a separate namespace and a commit-frozen panel selected by outcome-blind salted SHA-256 ranking. The same 12 existing seeds were applied to each of eight known families, yielding 96 paired worlds ... (n=40)."
Proposed correction: merge the two subsections "Freeze identifiers and panel selection" and "Minimal targeted sensitivity protocol" so panel selection is described once.

S13, S14, S17, S19, S20, Data availability, Code availability, Author contributions, Funding, Competing interests and the generative AI declaration checked with no readability issues.

---

## 10. Cross-paper consistency pass

### aij-read-31 (should-fix, error: three "language" notions) — lines 51, 254, 258, 321
Quote: line 51 "remaining inside a larger designer-supplied meta-language"; line 254 (Figure 4 caption) "Generic search under a fixed realization language"; line 258 "under that realization language"; line 321 "remain expressible in a supplied meta-language".
Reasoning: The paper uses the incumbent structural language A₀, a "designer-supplied meta-language", and a "realization language" without saying whether the last two are the same object.
Proposed correction: define once at Section 4.3 after Table 3 (after line 178): "We refer to the 29 primitives together with the nine realizer signatures as the supplied meta-language; escapes from A₀ remain inside it." Then replace "realization language" with "supplied meta-language" at lines 254 and 258.

### aij-read-32 (optional, editorial) — line 184
Quote: "Historical experiments use frozen `microsoft/phi-4`".
Reasoning: The short name "Phi-4" appears in the main text only in the declaration (line 379) but throughout the supplement.
Proposed replacement: "Historical experiments use frozen `microsoft/phi-4` (Phi-4), revision ...".

Additional cross-paper observations (no separate ID):
- "Scaffold" is used four times (lines 154, 192, 237, 355) without a gloss; line 192 comes closest. Optional: at line 154 write "the deterministic scaffold (realizer, fitter, ranking and action selector)".
- Table 3 (main) and the S8 table (SUPP lines 69–79) have identical content; consistent.
- Control-case counts reconcile: SUPP line 91 (1,125 AJ5; 1,125 + 500 CJ5) equals main line 216 (1,125 and 1,625).
- Figure file names do not follow figure numbers (Figure 2 is `figure_7_worked.png`); no reader impact.

Abstract revisited after the full read: the fixes in aij-read-01, 02 and 03 suffice; the final two sentences are clear.

---

## 11. Checks closed without a finding

- aij-read-18 (closed): line 198 "Eleven policies include aligned replay, incumbent-expression substitution, role/action-blind rebinding and eight individual non-incumbent signature masks." Count reconciles (1+1+1+8) with Table 3's nine signatures minus the incumbent. No issue.
- aij-read-29 (closed): SUPP line 91 control-case counts vs main line 216. Consistent (1,125 + 500 = 1,625). No issue.

---

## 12. Three most consequential findings

1. aij-read-06: AJ5 and CJ5 are used before introduction and never defined.
2. aij-read-09: four names for the central success event, with "jump" undefined in the main text.
3. aij-read-14 and aij-read-15 together: Section 4.4 introduces "legacy interface", a second model and "native reasoning" without explanation, which makes Section 5.5 hard to follow.

---

## 13. Sections checked with no issues

Introduction lines 19 to 27; Sections 2.1, 2.3, 2.4, 2.5, 3.1, 3.2, 3.4 body, 4.1, 4.5, 5.6, 5.7, 6.2, 6.3, 6.4, 7, 8; Data and Code availability; SUPP S2, S3, S5, S7, S8, S13, S14, S15, S16, S17, S18, S19, S20.

---

## 14. Coverage limits and unresolved checks

- Numerical values were not verified against artifacts; only figure-versus-text agreement was checked where it affects reading. Numerical audit is another reviewer's domain.
- Not opened: `manuscript/AIJ_EVIDENCE_RECORD_EXAMPLE.json`, `reports/AIJ_*`, the PDF build under `output/`. PDF-only rendering issues are unchecked.
- The tokensave MCP server failed to connect this session (CONNECTION_CLOSED), so no code-level lookup was performed; `.tokensave/tokensave.db` was not queried.
- Unresolved for the authors: the identity of "A6" (SUPP line 87) and whether it is the value-only control of main-text line 150 (aij-read-12, aij-read-26); the intended expansions, if any, of AJ5 and CJ5 (aij-read-06).
- All proposed wordings are readability edits; none alters a reported number or result.
- No files other than this report were written; no git state was changed.
