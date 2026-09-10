# Data verification for aij-data-01..05, aij-claim-01..05, aij-read-12, aij-read-26

Reviewer: aij-data. Date: 2026-09-10. HEAD `0214bc592aa55c92e5aaeffd298fbe22b07f3e3c` (= tag `aij-review-package-v1`).
Read-only: no artifacts, code, manuscripts or git state were changed. No model calls. All computations use pyarrow in `.venv` against frozen local artifacts and source. Labels: VERIFIED = reproduced locally; CONTRADICTED = source disagrees with the text; UNVERIFIED = not checkable locally.

Summary of verdicts

| ID | Verdict | Change to prior review |
|---|---|---|
| aij-claim-01 | VERIFIED (error confirmed; C_rand not "retained"; C3 and model "retained" is correct) | none |
| aij-claim-02 | VERIFIED for selection asymmetry; the "crossover available to C_rand" part is CONTRADICTED by AST proof (random policy reaches 13 operators, never SUBGRAPH_CROSSOVER) and withdrawn; recommend wording that does not assert a causal advantage | wording adjusted; crossover clause removed |
| aij-claim-03 | VERIFIED (family counts independently reproduced) | none |
| aij-claim-04 | VERIFIED (DeepSeek checkpoint, 4,096-token budgets) | none |
| aij-claim-05 | VERIFIED with one correction (all six conditions overwrite; but conditions do not differ in representation source only) | wording adjusted |
| aij-read-12 / aij-read-26 | RESOLVED: A6 is not the value-only control; value-only = B3 alias (A4); A6 = random untyped ablation, unreported | new evidence |
| aij-data-01 | WITHDRAW as should-fix: an archived output exists in `reports/AIJ_NUMERICAL_CHECKS.json` | downgrade to optional citation |
| aij-data-02 | VERIFIED (dormant exact-enumeration branch) | none |
| aij-data-03 | VERIFIED (call counts; manifest fields located) | none |
| aij-data-04 | VERIFIED (excerpt keys paraphrased) | none |
| aij-data-05 | WITHDRAW: "dynamic" is supported by the preserved launch command and preregistration doc | withdraw |

---

## Task 1. Blind rebinding: loss/gain by population and family; is "retained" valid?

Source: `experiments/nmi_realizer_audit_v1/results/world_results.parquet` (12,056 rows; columns family, policy, source, successful, validated_candidates, world_id, world_seed). Paired per (source, family, seed) between `aligned` and `role_action_blind_binding`.

Reproduction:
```python
import pyarrow.parquet as pq, collections
rows=pq.read_table("experiments/nmi_realizer_audit_v1/results/world_results.parquet").to_pylist()
HO='triadic_relation_reification'; al={}; bl={}
for r in rows:
    k=(r['source'],r['family'],r['world_seed'])
    if r['policy']=='aligned': al[k]=r['successful']
    elif r['policy']=='role_action_blind_binding': bl[k]=r['successful']
for src in ['C3','C_rand','DeepSeek_grammar']:
    byp=collections.defaultdict(collections.Counter); byf=collections.defaultdict(collections.Counter)
    for k in al:
        if k[0]!=src: continue
        a,b=al[k],bl[k]; cat='both_pass' if a and b else 'aligned_only' if a else 'blind_only' if b else 'both_fail'
        byp['heldout' if k[1]==HO else 'known'][cat]+=1; byf[k[1]][cat]+=1
    print(src, dict(byp), {f:dict(c) for f,c in byf.items() if c['aligned_only'] or c['blind_only']})
```

Results (VERIFIED):

| Source | Population | both_fail | aligned_only (lost) | blind_only (gained) | both_pass |
|---|---|---:|---:|---:|---:|
| C3 | known (400) | 0 | 53 | 0 | 347 |
| C3 | held-out (100) | 0 | 0 | 0 | 100 |
| C_rand | known (400) | 333 | 10 | 15 | 42 |
| C_rand | held-out (100) | 87 | 0 | 0 | 13 |
| DeepSeek_grammar | panel (96) | 81 | 7 | 0 | 8 |

By family:
- C3 losses: hidden_regimes 24 (26/50 kept), meta_law 29 (21/50 kept); no other family changes.
- C_rand known: gains are all 15 in latent_common_cause (0 -> 15); losses are meta_law 3 (of 5) and unification 7 (of 7). Held-out unchanged at 13.
- DeepSeek: losses meta_law 4 (9 -> 5), unification 3 (6 -> 3); no gains.

Conclusions:
- "Retains/retained" is accurate for C3 (347 = subset of aligned successes, zero gains) and for the grammar-constrained model (8 = subset, zero gains).
- "C_rand retains 57/400" is CONTRADICTED: 57 = 42 kept + 15 newly succeeding worlds; 10 aligned successes were lost. The prior review's assumption that all 10/15 are known-family is VERIFIED (held-out has no transitions).
- aij-claim-01 proposed wording is consistent with these counts. Recommended exact wording (Section 5.6, replacing the first two sentences of the paragraph starting "Aligned realizer replay reproduces"):

  "Aligned realizer replay reproduces the frozen candidates and verdicts. Role/action-blind rebinding preserves 347/400 known-family and 100/100 held-out C3 successes and 8/96 grammar-constrained successes, with no world succeeding only under blind binding in either source. For C_rand it changes which worlds succeed: 10 known-family aligned successes are lost (meta-law 3, unification 7) and 15 latent-common-cause worlds succeed only under blind binding, giving 57/400 known-family and an unchanged 13/100 held-out. C3 losses are confined to hidden-regime and meta-law worlds."

  S17 replacement for "This policy retained 347/400 known-family and 100/100 held-out C3 worlds, 57/400 and 13/100 C_rand worlds, and 8/96 DeepSeek worlds.":

  "This policy retained 347/400 known-family and 100/100 held-out C3 worlds and 8/96 DeepSeek worlds, with no world gained in either source. For C_rand it lost 10 aligned known-family successes (meta-law 3, unification 7) and gained 15 latent-common-cause worlds (57/400), with 13/100 held-out unchanged."

  Figure 7 caption addition after "(a) Aligned versus role/action-blind binding; annotations are successful-world counts and denominators appear in labels.":

  "The C_rand known-family count rises under blind binding because 15 worlds succeed only under blind binding while 10 aligned successes are lost; C3 and model-panel counts are pure subsets."

## Task 2. Selection policies: grammar-constrained vs C_rand; public-only scoring

Source lines (VERIFIED by reading):
- `src/abductive_jump/fair_interface_experiment.py:147-152` calls `_parse_self_plans(world, final_output, search_seed, required_plans=16)`; `:171-175` selects `max(evaluated, key=(item.score, structural_hash), default=_fixed_candidates(world,1)[0])`.
- `src/abductive_jump/compositional_experiment.py:146-262` (`_parse_self_plans`): each of the 16 plans is applied with `apply_primitive`; every executable plan gets `evaluate_candidate(world.public(), current)` (line ~246). Crossover raises "crossover requires a donor" (line ~232).
- `src/abductive_jump/composition_search.py:53-74` (`evaluate_candidate`): score tuple = (compatible and complete and escaped, compatible, separation > 0.5, separation, escaped, novelty, distinct operators, -observational loss). Inputs: `PublicWorld` only. `worlds.py:117-129` (`World.public`) builds observations via `public_dict` and intervention queries via `query_dict` (`worlds.py:61-69`, inputs and intervention only, no outcome); no validation/falsification split is exposed. Separation (`:35-50`) uses candidate and incumbent fitted expressions on public queries. Therefore the ranking is outcome-blind and public-only. VERIFIED.
- Historical C_self uses the identical `max(..., key=(score, structural_hash))` rule (`compositional_experiment.py:477-481`), and C3's `_select_diverse` (`composition_search.py:246-268`) sorts by the same score tuple then applies a diversity key.
- C_rand (`composition_search.py:438-486`): 48 random four-step paths; every intermediate graph (`evaluated.append(evaluate_candidate(...))`, line ~468) and every final path (`final_evaluations`, line ~478) IS evaluated with the same public score, but retention is `sorted(final_evaluations, key=structural_hash)[:3]` (lines ~480-483), i.e. the evaluated scores are computed and archived but not used for retention. VERIFIED.

Pool size in the grammar condition (VERIFIED from `experiments/nmi_fair_interface_v1/results/deepseek_fair_cself/llm_self_plans.parquet`): executable plans per slot distribution: 0 plans in 8 slots; 2:1, 3:1, 5:4, 6:4, 7:2, 8:2, 9:7, 10:5, 11:6, 12:21, 13:26, 14:43, 15:39, 16:119. Mean 13.7 executable plans per slot; 280/288 slots had at least two.

Operator support of the random policy (AST proof; WITHDRAWS the earlier "crossover available to C_rand" statement):
- `random_search` (`composition_search.py:438-492`) draws actions only from `_start_actions(..., wide=False)` (`:93-144`) and `_continuation_actions` (`:147-228`). An `ast` walk over `composition_search.py` collecting every `GenericPrimitive.<NAME>` attribute reachable from `random_search` through its local call graph (`_start_actions`, `_continuation_actions`, `_added_nodes`, `_next_position`, `evaluate_candidate`, `_query_separation`) yields exactly 13 operators: ADD_CONSTRAINT, ADD_DEPENDENCY, ADD_EDGE, ADD_FUNCTION, ADD_NODE, ADD_TEMPORAL_INDEX, BIND_ARGUMENT, CHANGE_ARITY, CHANGE_NODE_TYPE, CHANGE_OBSERVABILITY, COMPOSE_FUNCTIONS, REIFY_EDGE_AS_NODE, REVERSE_EDGE. `SUBGRAPH_CROSSOVER` is not referenced anywhere in `composition_search.py`. With `wide=False`, ADD_EDGE and the start-level CHANGE_NODE_TYPE branches (`:126-143`) are also skipped, so the nominal random-policy start set is ADD_NODE, ADD_FUNCTION, ADD_CONSTRAINT, REIFY_EDGE_AS_NODE, REVERSE_EDGE.
- Archived C_rand ancestry (`artifacts/composition_ancestry.parquet`, condition `C_RAND_RANDOM_PRIMITIVES`) contains 12 distinct operators (the 13 above minus ADD_EDGE, which is unreachable with `wide=False`) and zero SUBGRAPH_CROSSOVER records. C3 ancestry contains 11 distinct operators (no REVERSE_EDGE, no ADD_EDGE, no crossover).
- The 29-member `GenericPrimitive` set is the declared language; neither compositional search policy samples the full set. The grammar-constrained interface nominally exposes 28 operators (all but crossover, `fair_interface.py:153,198`), so the model path's nominal vocabulary is larger than, not smaller than, the random policy's 13-operator generator; whether a larger nominal vocabulary helps or hurts is not estimated.

Reproduction:
```python
import ast, collections, pyarrow.parquet as pq
tree=ast.parse(open("src/abductive_jump/composition_search.py").read())
funcs={n.name:n for n in tree.body if isinstance(n,ast.FunctionDef)}
prims=lambda n:{a.attr for a in ast.walk(n) if isinstance(a,ast.Attribute) and isinstance(a.value,ast.Name) and a.value.id=="GenericPrimitive"}
calls=lambda n:{c.func.id for c in ast.walk(n) if isinstance(c,ast.Call) and isinstance(c.func,ast.Name) and c.func.id in funcs}
seen=set(); stack=["random_search"]
while stack:
    f=stack.pop()
    if f not in seen: seen.add(f); stack+=list(calls(funcs[f]))
print(sorted(set().union(*(prims(funcs[f]) for f in seen))))   # 13 operators, no SUBGRAPH_CROSSOVER
anc=pq.read_table("artifacts/composition_ancestry.parquet",columns=["condition","operator"]).to_pylist()
print(sorted({r["operator"] for r in anc if r["condition"]=="C_RAND_RANDOM_PRIMITIVES"}))  # 12 operators
```

Assessment for aij-claim-02: the selection asymmetry is real (score-based retention over up to 16 evaluated plans per slot vs structural-hash retention over 48 evaluated paths). Both policies evaluate their candidates with the same public score; they differ in whether that score is used for retention. The earlier claim that crossover is available to C_rand is CONTRADICTED by the source and must not enter the integrated prose. The operator vocabularies also differ (13-operator generator for C_rand vs 28 nominal operators for the model path), in the opposite direction from the withdrawn statement. None of these differences has an estimated effect on the 15 vs 16 outcome, so they should be disclosed as design differences, not asserted as an advantage of known size or direction. Recommended exact wording (Section 5.5, after "The aggregate provides no model advantage over that comparator."):

  "The two policies are not selection-matched. The grammar-constrained path retains, per slot, the highest-scoring executable plan under the same outcome-blind public score used by C3 (typically 12-16 executable plans per slot), whereas C_rand evaluates its 48 paths with that score but retains three by structural hash without using the evaluated scores. The random policy also draws from a 13-operator generator rather than the 28 operators exposed to the model. The aggregate tie is therefore a comparison of complete proposal-plus-selection policies, not an estimate of proposal quality alone; the artifacts do not estimate whether or how much either design difference contributed."

  If the integrator prefers not to introduce the operator-count contrast in the main text, drop the sentence beginning "The random policy also draws" and keep the remainder.

  S14, after "Thus the model-generated plans did not exceed random composition in aggregate and showed a different family-specific motif distribution.": append the same paragraph.

## Task 3. C_rand family counts on the 96-world panel (independent derivation)

Source: `artifacts/compositional_jump_results.parquet` (condition `C_RAND_RANDOM_PRIMITIVES`, `no_jump` false, seeds in the panel list from `experiments/nmi_minimal_sensitivity_v1/panel_manifest.json`, excluding triadic) and `experiments/nmi_fair_interface_v1/results/deepseek_fair_cself/world_results.parquet` (96 rows).

```python
panel=[30014,30012,30029,30025,30011,30023,30000,30032,30001,30037,30002,30015]
cj=pq.read_table("artifacts/compositional_jump_results.parquet").to_pylist()
rand={(r['family'],r['world_seed']):r['condition_success'] for r in cj if r['condition']=='C_RAND_RANDOM_PRIMITIVES' and not r['no_jump'] and r['world_seed'] in panel and r['family']!='triadic_relation_reification'}
model={(r['family'],r['world_seed']):r['condition_success'] for r in pq.read_table("experiments/nmi_fair_interface_v1/results/deepseek_fair_cself/world_results.parquet").to_pylist()}
```

Results (VERIFIED; total 16/96 random, 15/96 model; paired 66/15/14/1 matches `paired_crand_comparison.csv`):

| Family (12 worlds each) | Random only | Model only | Both | Neither | Random total | Model total |
|---|---:|---:|---:|---:|---:|---:|
| property_to_relation | 10 | 0 | 0 | 2 | 10 | 0 |
| coordinate_transform | 3 | 0 | 0 | 9 | 3 | 0 |
| meta_law | 1 | 8 | 1 | 2 | 2 | 9 |
| unification | 1 | 6 | 0 | 5 | 1 | 6 |
| causal_ambiguity, hidden_regimes, latent_common_cause, state_invention | 0 | 0 | 0 | 12 | 0 | 0 |

aij-claim-03 figures are reproduced exactly. Recommended exact wording:
- Main text 5.5, after "and one joint success.": "The family distributions differ: model successes are confined to meta-law (9/12) and unification (6/12), whereas random successes are mostly property-to-relation (10/12) with 3/12 coordinate-transformation, 2/12 meta-law and 1/12 unification (Supplementary S14); these family counts are descriptive."
- S14, after the C_rand paired sentence: "C_rand's 16 panel successes were property-to-relation 10/12, coordinate transformation 3/12, meta-law 2/12 and unification 1/12; the single joint success was a meta-law world. The model condition exceeded random composition only in meta-law and unification, and random composition exceeded the model only in property-to-relation and coordinate transformation. All 21 validated model candidates depended on the single `multi_argument_function` signature."

## Task 4. AJ5: do all six conditions overwrite expression and action, and do they differ only in representation source?

Source: `src/abductive_jump/primary_experiment.py:66-82` (`_phase_one_representation`), `:147-245` (`_run_slot` body). VERIFIED by reading:
- Phase one is a model call in every condition (2 calls per slot in all six; ledger `artifacts/confirmatory/primary-jump/llm_calls.jsonl` shows 2,400 rows per condition).
- Representation source per condition: B0 = graph parsed from the phase-one model output (`parse_theory`); B1 = incumbent mutated by the model's `mutation_plan` (`apply_mutation_plan`); B2 = `world.incumbent` (the phase-one output is not read for the representation); B3 = `_attribute_variant(world.incumbent, slot)` (deterministic, model output not read); B4 = `select_external_proposals(..., diverse=False)` (with replacement); B5 = same portfolio with `diverse=True` (shuffle, without replacement). On any phase-one failure the incumbent is used (`fallback_to_incumbent`).
- Unconditionally for all six: `fitted = fit_representation(public, candidate_representation)` (line ~203); `exact_choice = max(table, key=(absolute_separation, case_id))` (line ~212); after phase two, `payload["representation"] = candidate_representation.canonical_dict()`, `payload["expression"] = fitted.expression.tree`, `payload["selected_intervention_ids"] = [exact_choice]` (lines ~238-241) before `parse_theory` and `evaluate_executable`. The model's phase-two intervention choice is stored only as `model_selected_intervention_ids` (diagnostic). Phase-two JSON that cannot be extracted marks `phase_two_valid` False and skips evaluation; in the archived jump populations `phase_two_valid` is 1,200/1,200 in every condition.
- Shared settings across all six: 3 slots, 700-token cap, temperature 0.2/top-p 0.95, same phase-two prompt builder, same fitter, same action rule, same thresholds (`configs/confirmatory-primary-jump.json`, `summary.json` budget_contract calls_per_slot 2).
- Differences beyond representation source: B1 uses `sample_temperature` 0.7 (`primary_experiment.py:122-123`); B0 and B1 use different phase-one output contracts (`conditions.py:196-198`); B4 vs B5 differ in with/without replacement selection. The S4 phrase "archive accounting and deterministic falsification" for B5: code shows only `diverse=True` (structural uniqueness); J5 falsification is applied identically in every condition. The "deterministic falsification" attribute is therefore not a B5-specific mechanism (UNVERIFIED as a distinct feature; likely legacy wording).

Assessment for aij-claim-05: the overwrite claim is VERIFIED for all six conditions. The proposed clause "so the conditions differ in representation source only" is too strong. Recommended exact wording (Section 4.2, end of first paragraph, replacing "A separate value-only control also remains within the incumbent language." per Task 5):

  "In all six conditions the executable expression is fitted by the scaffold from public observations and the committed intervention is the deterministic maximum-separation action; model-authored expression and action fields are overwritten before evaluation. The conditions therefore differ in the source of the evaluated representation and, for B0 and B1, in the phase-one output contract and sampling temperature; budgets, fitter, action selection and gates are identical."

  Optional Table 4 caption clause: "Expression and committed intervention are scaffold-supplied in every row."

  S4 B5 bullet: consider replacing "three structurally distinct portfolio proposals, archive accounting and deterministic falsification" with "three structurally distinct portfolio proposals selected without replacement (archive analogue); evaluation is identical to B4."

## Task 5. Identity and sources of A6 and the "value-only control"

VERIFIED from source and artifacts:
- `A6_RANDOM_UNTYPED`: "A6 control: random graph edits without kind-specific structural semantics" (`src/abductive_jump/proposals.py:129`, `random_untyped_proposal`); run by `src/abductive_jump/random_ablation.py` with `configs/ablation-a6-jump.json` and `configs/ablation-a6-control.json` (same Phi-4 revision, 700 tokens, 3 slots). Results: `artifacts/confirmatory/ablation-a6-jump/world_results.parquet` 18/400 successes (JSR 0.045); `ablation-a6-control/world_results.parquet` 0/200; `artifacts/ablation_summary.parquet` row A6 jsr 0.045; calls 2,400 + 1,200 = 3,600 (`ablation-a6-*/summary.json`; `artifacts/reproducibility-manifest.json` `triggered_secondary_llm_calls` 3600). A6 is a secondary ablation that the AIJ manuscript never reports; S9 mentions only its call count.
- Value-only control: `artifacts/ablation_summary.parquet` row `A4_VALUE_ONLY` has jsr 0.0 and is computed in `src/abductive_jump/analysis.py:504-508` as `summary_by_condition[B3_ATTRIBUTE_MUTATION]["jsr"]`, i.e. it is an alias of B3, not a separate run. No separate value-only run exists in `artifacts/confirmatory/`.

Consequences for aij-read-12 and aij-read-26: the conjecture that A6 is the value-only control is CONTRADICTED. "A separate value-only control" (main text line 150) is inaccurate as "separate": it is B3 under its historical ablation label A4. Recommended exact wording:
- Main line 150: delete "A separate value-only control also remains within the incumbent language." (it is subsumed by the B3 sentence), or replace with "B3 is the value-only control (historical ablation label A4)."
- Main line 152: "B2/B3 are structural controls, not fair contests over universal capability: their reachable representations cannot satisfy J1."
- S9: replace "AJ5 therefore executed 32,400 prospectively specified calls plus 3,600 A6 calls." with "AJ5 therefore executed 32,400 prospectively specified calls (21,600 across B0-B5 and 10,800 in the three-source factorial). A separately triggered secondary ablation with random untyped graph edits (historical label A6; 18/400 jump worlds, 0/200 controls) used a further 3,600 calls and is not part of the reported comparisons." If the authors prefer not to introduce A6 results, use instead: "…plus 3,600 calls for a triggered secondary ablation that is not reported here."

## Task 6. Re-check of aij-data-01..05

### aij-data-01 (comparator output archival) — WITHDRAW as should-fix
An archived output exists: `reports/AIJ_NUMERICAL_CHECKS.json` entry "Control worlds/cases" with `actual` `[[200,1125,0],[200,1125,0],[100,500,0]]`, `source` `scripts/audit_nmi_control_comparator.py`, `pass` true. It is produced by `scripts/audit_aij_numbers.py:128-130`, which runs the comparator script by subprocess and records worlds/cases/mismatches. My earlier statement that no output is archived was wrong. My independent rerun on 2026-09-10 printed identical values with `max_absolute_error` 0.0. Recommended: optional citation only, e.g. S10 add "(recorded in `reports/AIJ_NUMERICAL_CHECKS.json`)" after "…and 500 in 100 held-out CJ5 controls."

### aij-data-02 (sign-flip branch) — VERIFIED, unchanged
`src/abductive_jump/compositional_analysis.py:93-113`: exact enumeration when `len(nonzero) <= 20` (`p = extreme / 2^k`, no +1), else 10,000 random flips with `(extreme+1)/(replicates+1)`. Discordant counts for reported contrasts (C3 succeeds in every world, so discordant = worlds minus comparator successes): C3-C0 400, C3-C2 400, C3-C1 269, C3-C_rand 348, C3-C_self 400; held-out 100, 100, 87, 100. All used the random-flip branch. Wording as in the prior review stands.

### aij-data-03 (call counts) — VERIFIED, unchanged
Ledger line counts in `artifacts/reproducibility-manifest.json`: primary-jump 14,400 + primary-control 7,200 + factorial-jump 7,200 + factorial-control 3,600 = 32,400 (`preregistered_llm_calls` 32400); ablation-a6-jump 2,400 + ablation-a6-control 1,200 = 3,600 (`triggered_secondary_llm_calls` 3600). CJ5 33,600 = `compositional_jump_results.parquet` llm_calls sum (800 worlds x 7 conditions x 6). Wording as in Task 5 S9 replacement supersedes the earlier aij-data-03 proposal.

### aij-data-04 (S20 excerpt keys) — VERIFIED, unchanged
Record paths differ from excerpt keys as listed in the prior review; values match. Proposed wording unchanged.

### aij-data-05 ("dynamic" quantization) — WITHDRAW
Evidence for "dynamic": `docs/phi4_runtime_extension_manifest.md:8-14` ("vLLM 0.10.2 with dynamic bitsandbytes 4-bit loading") and the preserved container launch command at `:86-94` (`--quantization bitsandbytes --load-format bitsandbytes` on the BF16 `microsoft/phi-4` checkpoint, i.e. vLLM in-flight quantization); `:112-116` "linear weights are dynamically quantized by the bitsandbytes loader … result files remain labeled `bitsandbytes-4bit`"; `docs/abductive-jump-preregistration.md:24` "Quantization: vLLM dynamic bitsandbytes 4-bit"; calibration configs label `bitsandbytes-dynamic-4bit-vllm-default`. Run manifests record only `bitsandbytes-4bit`. The manuscript wording is supported; no change needed. Optional clarification: "with in-flight (dynamic) bitsandbytes 4-bit quantization of the BF16 checkpoint".

### aij-claim-04 (model and budget for the grammar condition) — VERIFIED
`experiments/nmi_fair_interface_v1` configs and `compute_ledger.csv`: DeepSeek-V4-Flash-Vision-Exp, 4,096-token deliberation and serialization budgets, 288 + 288 calls. Historical C_self: Phi-4, 700 tokens (`configs/compositional-confirmatory-existing.json`). Proposed abstract/5.5 wording in the claim review is consistent with the artifacts.

## Cross-check notes for integration

- Figure 7(a) already plots C_rand aligned 52 next to blind 57; the caption addition above makes the figure and text agree.
- If the S9 A6 sentence is expanded, the numbers 18/400 and 0/200 come from `artifacts/confirmatory/ablation-a6-{jump,control}/world_results.parquet` and `artifacts/ablation_summary.parquet`; both are in the frozen release.
- No evidence file, artifact or manuscript was modified during this verification.
