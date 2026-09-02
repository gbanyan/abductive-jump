from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pyarrow.parquet as pq

from .conditions import Condition


def _condition(final: dict[str, Any], name: str) -> dict[str, Any]:
    return next(row for row in final["condition_results"] if row["condition"] == name)


def _comparison(final: dict[str, Any], fragment: str, family: str) -> dict[str, Any]:
    return next(
        row
        for row in final["comparisons"]
        if fragment in row["comparison"] and row["family"] == family
    )


def _percent(value: float) -> str:
    return f"{100 * value:.1f}%"


def run(root: Path) -> dict[str, Any]:
    artifacts = root / "artifacts"
    reports = root / "reports"
    final_path = artifacts / "final_compositional_verdict.json"
    final = json.loads(final_path.read_text())
    candidates = pq.read_table(artifacts / "compositional_candidates.parquet").to_pylist()
    ancestry = pq.read_table(artifacts / "composition_ancestry.parquet").to_pylist()
    depth_controls = pq.read_table(artifacts / "no_jump_depth_controls.parquet").to_pylist()
    summaries = {
        key: _condition(final, key)
        for key in (
            Condition.C0_FIXED_SPACE.value,
            Condition.C1_ATOMIC_HIGH_LEVEL.value,
            Condition.C2_GENERIC_DEPTH_1.value,
            Condition.C3_GENERIC_COMPOSITION.value,
            Condition.C_SELF_LLM_COMPOSITION.value,
            Condition.C_RAND_RANDOM_PRIMITIVES.value,
            Condition.C5_ORACLE_REPRESENTATION.value,
        )
    }
    c3_rand = _comparison(final, "C_RAND", "SECONDARY_EXISTING")
    random_isolated = c3_rand["estimate"] > 0 and c3_rand["p_holm"] < 0.05
    data_verdict = final["verdict_before_reviewer2"]
    reviewer_verdict = data_verdict
    downgrade_reason = None
    if data_verdict in {"CJ4", "CJ5"} and not random_isolated:
        reviewer_verdict = "CJ3"
        downgrade_reason = (
            "C3 did not significantly exceed the matched random-primitive control; composition "
            "may work, but the structured search heuristic has no isolated advantage."
        )
    final["reviewer2_verdict"] = reviewer_verdict
    final["verdict"] = reviewer_verdict
    final["reviewer2_downgrade"] = downgrade_reason
    final["aj6_candidate_available"] = reviewer_verdict == "CJ5"
    final_path.write_text(json.dumps(final, indent=2, sort_keys=True) + "\n")

    rows = []
    for label, condition in (
        ("C0", Condition.C0_FIXED_SPACE.value),
        ("C1", Condition.C1_ATOMIC_HIGH_LEVEL.value),
        ("C2", Condition.C2_GENERIC_DEPTH_1.value),
        ("C3", Condition.C3_GENERIC_COMPOSITION.value),
        ("C_self", Condition.C_SELF_LLM_COMPOSITION.value),
        ("C_rand", Condition.C_RAND_RANDOM_PRIMITIVES.value),
        ("C5", Condition.C5_ORACLE_REPRESENTATION.value),
    ):
        row = summaries[condition]
        rows.append(
            f"| {label} | {row['existing_successes']}/{row['existing_worlds']} ({_percent(row['jsr'])}) "
            f"| {row['heldout_successes']}/{row['heldout_worlds']} ({_percent(row['heldout_jsr'])}) "
            f"| {row['false_jumps']}/{row['existing_control_worlds']} "
            f"| {row['heldout_false_jumps']}/{row['heldout_control_worlds']} |"
        )
    rho = final["retained_jump_gain"]
    primary = [row for row in final["comparisons"] if row["family"] == "PRIMARY_EXISTING"]
    replayed = sum(bool(row["replay_verified"]) for row in candidates)
    successful_c3 = [
        row
        for row in candidates
        if row["condition"] == Condition.C3_GENERIC_COMPOSITION.value
        and row["validated_jump"]
    ]
    depths = sorted({int(row["ancestry_depth"]) for row in successful_c3})
    report = f"""# Compositional Representation Jump — Final Report

Preregistration commit: `65f2087`. Recorded pre-confirmatory admissibility correction:
`7ecb977`. Frozen antecedent: AJ5 at `dd6e82c`.

## Result

The preregistered data-only decision was **{data_verdict}**. Reviewer #2 returns
**{reviewer_verdict}**.{(' The downgrade reason is: ' + downgrade_reason) if downgrade_reason else ''}

The result does not modify the frozen AJ5 finding. It tests whether that advantage survives
removal of atomic family-level operators and whether it transfers to the prospectively sealed
arity-three relation family.

| Condition | Existing reconstruction JSR | Held-out JSR | Existing FJR | Held-out FJR |
| --- | ---: | ---: | ---: | ---: |
{chr(10).join(rows)}

## Primary tests

The two registered existing-family comparisons were:

{chr(10).join(f"- `{row['comparison']}`: difference {row['estimate']:.4f}, 95% bootstrap CI [{row['ci_low']:.4f}, {row['ci_high']:.4f}], one-sided permutation p={row['p_one_sided']:.6g}, Holm p={row['p_holm']:.6g}." for row in primary)}

Retained jump gain was `rho_J={rho['rho_j']}` with bootstrap interval
`[{rho['ci_low']}, {rho['ci_high']}]`. This ratio is reported alongside its absolute
denominator because a low C1 rate can inflate it.

## Construction and safety

- Successful C3 candidate depths: {depths}; all registered compositional successes require
  depth >=2.
- Replay: {replayed}/{len(candidates)} selected candidates reproduced from frozen seeds and
  raw outputs; ancestry artifact contains {len(ancestry)} record rows.
- C3 combined no-jump FJR: {_percent(final['combined_c3_fjr'])}, Wilson interval
  `[{final['combined_c3_fjr_ci'][0]:.6f}, {final['combined_c3_fjr_ci'][1]:.6f}]`.
- No-jump depth artifact contains {len(depth_controls)} candidate-level rows.
- Successful primitive-sequence distribution is stored without semantic embeddings in
  `final_compositional_verdict.json`.

## Held-out interpretation

The held-out family was never used for LLM/search pilot inference and was not unlocked until
the known-family reconstruction and controls were terminal. It requires an arity-three
reified relation rather than AJ5's binary property relation. The broad idea of relations and
reification was not conceptually novel: both existed in the earlier DSL. The valid claim is
therefore prospective generalization to an unseen structural configuration, not invention
without prior vocabulary.

## Limits

The structured search grammar deliberately spans typed-node, function, relation, and reified
edge strata. This is far weaker than an atomic family answer, but it remains a supplied
structural prior. The deterministic fitter also maps completed graph motifs to a bounded
executable basis. Results concern representation construction under these procedural worlds,
not open-ended science, universal theory invention, or general LLM abduction.

## Final claim

{('Generic local rewrites were compositionally assembled into validated representations and prospectively generalized to the registered held-out structural family.' if reviewer_verdict == 'CJ5' else 'The evidence supports only the bounded claim encoded by ' + reviewer_verdict + '; AJ6 is not established.')}
"""
    (reports / "compositional-representation-jump-final.md").write_text(report)

    sequence_counts = final["successful_sequence_counts"]
    dominant = sequence_counts[0]["successful_candidates"] / max(
        1, sum(row["successful_candidates"] for row in sequence_counts)
    )
    assessments = [
        ("1. Do primitives hide the answers?", "No single primitive validates after the correction (0/17,280 depth-one development checks), but CHANGE_NODE_TYPE and the stratified grammar retain strong typed structural priors. This narrows, rather than nullifies, a compositional claim."),
        ("2. Is the held-out family truly held out?", "Its confirmatory seeds and LLM/search instances were locked through known-family completion. The generator was used only for deterministic unit/reachability tests as preregistered."),
        ("3. Was a structural analogue already seen?", "Yes: AJ5 included binary property-to-relation. Arity-three reification is non-isomorphic but conceptually adjacent. Any claim of vocabulary-free invention is rejected."),
        ("4. Does vocabulary completeness make success inevitable?", f"C5 is the ceiling at {_percent(summaries[Condition.C5_ORACLE_REPRESENTATION.value]['jsr'])}; C2, C_self, and C_rand quantify whether vocabulary alone suffices. The search result must be read against those controls."),
        ("5. Is depth merely more brute-force budget?", "C2 and C3 have the same 192 evaluation capacity; C2 spreads it across depth-one alternatives and C3 uses 48x4. Depth changes topology, not total registered opportunity."),
        ("6. Does C3 simply have more candidates than C0?", "Both execute 192 deterministic candidate evaluations and six LLM calls per world. C0 intentionally has no J1 opportunity; that is the experimental intervention."),
        ("7. Is random search equally good?", f"C3-C_rand difference={c3_rand['estimate']:.4f}, Holm p={c3_rand['p_holm']:.6g}. Structured-search advantage isolated={random_isolated}."),
        ("8. Is LLM-selected composition equally good?", f"C_self existing JSR={_percent(summaries[Condition.C_SELF_LLM_COMPOSITION.value]['jsr'])}; malformed plans consume opportunities and are fully reported."),
        ("9. Did selection see family labels?", "No search API receives family. Code paths use the public graph, observations, outcome-free query schema, structural validity, fit, discrimination availability, and novelty."),
        ("10. Did edit distance leak?", "No search module imports the reachability witness or target distance. Witness plans are isolated in the benchmark-validity module."),
        ("11. Does the heuristic implicitly encode target structure?", "Partly: its generic strata cover typed nodes, bound functions, relations, and reified edges. This is a disclosed structural prior and the principal scope limitation."),
        ("12. Does FJR worsen with depth?", f"C3 combined FJR={_percent(final['combined_c3_fjr'])}; depth gate passed={final['gates']['fjr_pass']}."),
        ("13. Is the incumbent oracle valid?", "Every world uses the frozen exact finite incumbent oracle; incomplete generic motifs are compiled back to that exact incumbent basis after the pilot correction."),
        ("14. Is composition necessary?", f"C3-C2 primary comparison: {primary[1]['estimate']:.4f}, Holm p={primary[1]['p_holm']:.6g}."),
        ("15. Is ancestry replayable?", f"{replayed}/{len(candidates)} candidates replayed; each generic step records hashes, arguments, seed, and depth."),
        ("16. Does one sequence dominate?", f"Largest successful sequence share={_percent(dominant)}. Counts are reported; dominance limits diversity claims but does not change individual J0-J5 validity."),
        ("17. Is held-out success surface similarity?", "It may benefit from the prior binary-relation concept, but opaque labels and prospective arity-breaking interventions prevent a purely lexical explanation."),
        ("18. Is this representation rather than parameter mutation?", "C3 successes require J1 plus completed multi-step motifs. C0/C2 and the G_H antecedent controls separate unchanged/value-only representations."),
        ("19. Is rho inflated by a low denominator?", f"Yes, potentially. C1-C0 absolute denominator is {summaries[Condition.C1_ATOMIC_HIGH_LEVEL.value]['jsr'] - summaries[Condition.C0_FIXED_SPACE.value]['jsr']:.4f}; both rho and absolute JSR differences are reported."),
        ("20. Can this still support only AJ5?", f"Reviewer verdict={reviewer_verdict}. AJ5 remains independently valid. AJ6 candidate language is available only for undowngraded CJ5 and remains strictly procedural."),
    ]
    reviewer = """# Reviewer #2 — Compositional Representation Jump

Role: adversarial post-confirmatory audit. This review may lower but never raise the
preregistered data verdict.

## Disposition

Data verdict: **{data}**. Reviewer verdict: **{reviewer}**.

{reason}

## Attacks

{attacks}

## Final reviewer boundary

The experiment can establish bounded composition of supplied generic structural primitives.
It cannot establish unscaffolded representation invention, general science, or universal
abduction. The earlier AJ5 result survives every compositional-phase outcome.
""".format(
        data=data_verdict,
        reviewer=reviewer_verdict,
        reason=downgrade_reason or "No preregistered fatal leakage or control equivalence requires a downgrade.",
        attacks="\n\n".join(f"### {title}\n\n{text}" for title, text in assessments),
    )
    (reports / "compositional-representation-jump-reviewer2.md").write_text(reviewer)
    return {
        "data_verdict": data_verdict,
        "reviewer_verdict": reviewer_verdict,
        "downgrade_reason": downgrade_reason,
        "report": str(reports / "compositional-representation-jump-final.md"),
        "reviewer2": str(reports / "compositional-representation-jump-reviewer2.md"),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    print(json.dumps(run(args.root), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
