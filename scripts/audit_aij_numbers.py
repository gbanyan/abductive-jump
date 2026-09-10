"""Read-only checks of frozen numerical claims, plus audit-report generation.

Does not run inference or modify historical artifacts. Assertions cover empirical
counts and configurations; paragraph inventory separately records manual coverage.
"""
from __future__ import annotations
import csv
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
CHECKS = []
SOURCES = {}


def read(path):
    p=ROOT/path
    SOURCES[path]=hashlib.sha256(p.read_bytes()).hexdigest()
    if p.suffix==".parquet": return pq.read_table(p).to_pylist()
    if p.suffix==".csv":
        with p.open() as f: return list(csv.DictReader(f))
    return json.loads(p.read_text())


def check(name,actual,expected,source):
    if isinstance(expected,float): good=abs(float(actual)-expected)<1e-10
    else: good=actual==expected
    CHECKS.append({"claim":name,"actual":actual,"expected":expected,"source":source,"pass":good})
    assert good, (name,actual,expected)


def select(rows,**keys):
    return next(r for r in rows if all(r[k]==v for k,v in keys.items()))


def main():
    CHECKS.clear()
    SOURCES.clear()
    src="artifacts/condition_summary.parquet"; aj=read(src)
    for r,n in zip(aj,[1,1,0,0,142,142]):
        check(r["condition"]+" success",round(r["jsr"]*r["jump_worlds"]),n,src)
        check(r["condition"]+" worlds",r["jump_worlds"],400,src)
        check(r["condition"]+" controls",(r["control_worlds"],r["fjr"]),(200,0.0),src)
    src="artifacts/proposal_reasoning_factorial.parquet"; factorial=read(src)
    fs=sorted({r["proposal_source"] for r in factorial})
    for label,n in zip(fs,[0,142,400]):
        rr=[r for r in factorial if r["proposal_source"]==label and not r["no_jump"]]
        check(label+" factorial",(len(rr),sum(r["condition_success"] for r in rr)),(400,n),src)
    src="artifacts/compositional_cost_frontier.parquet"; cj=read(src)
    for p,known,held in [("C0",0,0),("C1",131,0),("C2",0,0),("C3",400,100),("C_RAND",52,13),("C_SELF",0,0)]:
        r=next(r for r in cj if r["condition"].startswith(p))
        check(p+" known/heldout",(r["existing_worlds"],r["existing_successes"],r["heldout_worlds"],r["heldout_successes"]),(400,known,100,held),src)
    src="artifacts/compositional_comparisons.parquet"; contrasts=read(src)
    for family,ci in [("SECONDARY_EXISTING",(.845,.895)),("HELDOUT",(.80,.93))]:
        r=next(r for r in contrasts if "C_RAND" in r["comparison"] and r["family"]==family)
        for key,v in zip(["estimate","ci_low","ci_high"],[.87,*ci]): check(f"C3/random {family} {key}",r[key],v,src)
    src="artifacts/nmi_gate_attrition.parquet"; gates=read(src)
    for prefix,expected in [("B0",[65,22,4,1,1]),("B1",[546,375,118,1,1]),("B4",[823,573,270,154,154]),("B5",[838,562,262,145,145])]:
        r=next(r for r in gates if r["population"]=="jump" and r["condition"].startswith(prefix))
        check(prefix+" cumulative gates",[r[f"through_j{i}"] for i in range(1,6)],expected,src)
    for prefix,expected in [("B4",[600,112,0]),("B5",[600,110,0]),("C3",[900,283,0])]:
        r=next(r for r in gates if r["population"]=="control" and r["condition"].startswith(prefix))
        check(prefix+" control attrition",[r["candidates"],r["through_j3"],r["through_j4"]],expected,src)
    r=next(r for r in gates if r["population"]=="control" and r["condition"].startswith("C3"))
    check("C3 controls J1/J2",[r["through_j1"],r["through_j2"]],[800,567],src)
    src="artifacts/nmi_component_audit.json"; replay=read(src)["c3_without_llm"]
    for k,v in {"candidate_gate_matches":2400,"candidate_rows":2400,"jump_successes":500,"jump_worlds":500,"control_worlds":300,"false_jumps":0}.items(): check("C3 replay "+k,replay[k],v,src)
    for src,expected in [("artifacts/replay-validation.json",{"verified_theories":10800}), ("artifacts/compositional-replay-validation.json",{"verified_candidates":16800,"ancestry_rows":35533,"mismatches":0}), ("experiments/nmi_minimal_sensitivity_v1/analysis/replay_report.json",{"candidate_rows":2772,"mismatches":0,"model_calls_made":0}), ("experiments/nmi_fair_interface_v1/results/deepseek_fair_cself/replay_report.json",{"candidate_rows":288,"mismatches":0,"model_calls_made":0})]:
        rr=read(src)
        for k,v in expected.items():
            key="replay_mismatches" if k=="mismatches" and "replay_mismatches" in rr else k
            check(src+" "+k,rr[key],v,src)
    src="experiments/nmi_minimal_sensitivity_v1/offline/historical_cself_attrition.json"; hist=read(src)
    check("Historical responses/plan opportunities",[hist["historical_population"][k] for k in ["worlds","proposal_responses","plan_opportunities"]],[400,1200,19200],src)
    check("Historical cap/strict JSON",[hist["diagnostics"][k] for k in ["nonempty_responses","responses_at_completion_token_cap","strict_complete_json_responses"]],[1200,1200,0],src)
    src="experiments/nmi_fair_interface_v1/analysis/analysis.json"; fair=read(src)
    for stage,v in [("plan_schema_valid",4608),("executable",3939),("J1",236),("J2",236),("J3",21),("J4",21),("J5",21)]:
        check("Grammar "+stage,select(fair["gate_attrition"],stage=stage)["passed"],v,src)
    for stage,tokens in [("deliberation",1179648),("serialization",574538)]:
        rr=select(fair["compute_ledger"],stage=stage)
        check(stage+" calls/tokens",[rr["calls"],rr["completion_tokens"]],[288,tokens],src)
    src="experiments/nmi_fair_interface_v1/analysis/paired_crand_comparison.csv"; rr=read(src)[0]
    check("96-world paired table",[int(rr[k]) for k in ["both_fail","reference_only_success","comparison_only_success","both_succeed","reference_successes","comparison_successes","worlds"]],[66,15,14,1,16,15,96],src)
    src="experiments/nmi_fair_interface_v1/analysis/validated_signature_distribution.csv"; rr=read(src)
    check("Selected executable signature counts",{r["structural_signature"]:int(r["selected_executable_candidates"]) for r in rr},{"incumbent_basis":258,"bound_relation":1,"multi_argument_function":21},src)
    src="experiments/nmi_minimal_sensitivity_v1/analysis/world_summary.csv"; rr=read(src)
    for r in rr:
        check(r["condition"]+" sensitivity successes",int(r["successes"]),3 if r["condition"]=="deepseek_p2" else 0,src)
    src="experiments/nmi_minimal_sensitivity_v1/analysis/compute_ledger.csv"; compute=read(src)
    expected={"phi8_cself":(576,231773),"deepseek_matched_cself":(576,237792),"deepseek_native_cself":(576,2249518),"phi8_cself_repair":(864,433373),"deepseek_p2":(120,485312),"phi4_4bit_budget_cself":(576,528976)}
    for label,(calls,tokens) in expected.items():
        r=select(compute,condition=label)
        check(label+" calls/tokens",(int(r["llm_calls"]),int(r["completion_tokens"])),(calls,tokens),src)
    check("Native length/stop",json.loads(select(compute,condition="deepseek_native_cself")["finish_reasons"]),{"length":518,"stop":58},src)
    check("P2 capped calls",json.loads(select(compute,condition="deepseek_p2")["finish_reasons"])["length"],116,src)
    src="experiments/nmi_minimal_sensitivity_v1/analysis/phi_budget_gate_attrition.csv"; rr=read(src)
    for label,sch,exe in [("phi4_4bit_budget_cself_full",4642,9),("phi4_4bit_budget_cself_heldout",1289,0)]:
        for stage,value in [("plan_schema_valid",sch),("executable",exe)]: check(label+" "+stage,int(select(rr,condition=label,stage=stage)["passed"]),value,src)
    src="experiments/nmi_minimal_sensitivity_v1/analysis/gate_attrition.csv"; rr=read(src)
    check("Fixed-panel budget schema",int(select(rr,condition="phi4_4bit_budget_cself",stage="plan_schema_valid")["passed"]),993,src)
    for stage,v in [("parse_valid",4),("executable",4),("J1",4),("J2",4),("J3",3),("J4",3),("J5",3)]: check("P2 "+stage,int(select(rr,condition="deepseek_p2",stage=stage)["passed"]),v,src)
    src="experiments/nmi_realizer_audit_v1/analysis/condition_summary.csv"; rr=read(src)
    for source,pop,n in [("C3","known",347),("C3","heldout",100),("C_rand","known",57),("C_rand","heldout",13),("DeepSeek_grammar","fixed_known_panel",8)]:
        check(source+" "+pop+" blind binding",int(select(rr,source=source,population=pop,policy="role_action_blind_binding")["successes"]),n,src)
    for sig,n in [("relation_arity_3",100),("unobserved_dependency",100),("bound_relation",50),("multi_argument_function",50),("self_composed_function",50),("temporally_indexed_recurrence",50),("unobserved_selector",50),("shared_rule_binding",0)]:
        losses=sum(int(select(rr,source="C3",population=p,policy="aligned")["successes"])-int(select(rr,source="C3",population=p,policy="mask_signature:"+sig)["successes"]) for p in ["known","heldout"])
        check("C3 signature loss "+sig,losses,n,src)
    for src,n in [("experiments/nmi_realizer_audit_v1/results/candidate_results.parquet",36168),("experiments/nmi_realizer_audit_v1/results/world_results.parquet",12056)]: check("realizer rows",len(read(src)),n,src)
    src="experiments/nmi_realizer_audit_v1/analysis/gate_attrition.csv"; rr=read(src)
    for source,n in [("C3",1168),("C_rand",1040),("DeepSeek_grammar",236)]:
        check(source+" incumbent substitution J2",int(select(rr,source=source,policy="motif_disabled",stage="J2")["passed"]),n,src)
        check(source+" incumbent substitution J3",int(select(rr,source=source,policy="motif_disabled",stage="J3")["passed"]),0,src)
    src="experiments/nmi_minimal_sensitivity_v1/panel_manifest.json"; panel=read(src)
    check("Panel ordered seeds",panel["selected_seeds"],[30014,30012,30029,30025,30011,30023,30000,30032,30001,30037,30002,30015],src)
    check("Panel cardinality",len(panel["selected_worlds"]),96,src)
    check("P2 panel",panel["p2_positive_control"]["total_worlds"],40,src)
    src="configs/confirmatory-primary-jump.json"; cfg=read(src)
    check("Historical generation",cfg["generation"],{"max_tokens":700,"temperature":.2,"top_p":.95},src)
    check("Historical context/temperature",(cfg["context_limit"],cfg["sample_temperature"]),(4096,.7),src)
    check("Gate thresholds",cfg["gate_thresholds"],{"delta_cf":.1,"delta_falsification":.1,"epsilon_candidate_obs":1e-12,"epsilon_falsification":1e-12,"epsilon_obs":1e-12,"min_prediction_separation":.5},src)
    # Reconstruct already archived controls, without touching artifacts or calling a model.
    result=subprocess.run([sys.executable,str(ROOT/"scripts/audit_nmi_control_comparator.py")],capture_output=True,text=True,check=True)
    controls=json.loads(result.stdout)
    check("Control worlds/cases",[(r["worlds"],r["cases"],r["exact_mismatches"]) for r in controls],[(200,1125,0),(200,1125,0),(100,500,0)],"scripts/audit_nmi_control_comparator.py")
    src="manuscript/figures/aij/source_data.json"; plotted=read(src)
    check("Worked example outcomes",[plotted["data"]["worked_example"][k] for k in ["seed","intervention_outcome","falsification_outcome"]],[40000,2268,1620],src)
    supplementary_checks()
    section_review_checks()
    report=["# AIJ numerical audit", "", "No model inference or new experimental population was run. Historical artifacts are read-only. Empirical assertions and manual protocol review are separate checks.", "",f"Automated checks: **{len(CHECKS)} passed, 0 failed**.", "", "| Claim | Verified value | Canonical source |", "|---|---|---|"]
    for c in CHECKS:
        report.append(f'| {c["claim"]} | `{c["actual"]}` | `{c["source"]}` |')
    report += ["", "## Manual numerical/protocol review", "",
               "Main Sections 3–4: gate thresholds and validity prerequisites checked against executable.py/gates.py; comparator selection against oracle.py; opportunity counts against frozen configs. The validity prerequisite V(T) was made explicit during this audit. Main Section 5 and figure captions: counts, intervals and denominators checked above. Percentages are arithmetic from world/plan counts, not candidate-level inferential estimates.",
               "", "Supplement S1–S8: seed ranges, 29/28 primitive distinction, 48 × four-step paths, three retained slots, 16 plans/slot, nine realizer signatures and thresholds checked against configs, protocol files, generic primitive manifest and composition.py. S9–S10: archived call counts and bootstrap settings checked against historical summaries, analysis.py and compositional_analysis.py; tail quantities retain their non-P interpretation.",
               "", "Supplement S11–S17: panel seeds, token counts, attrition, replay, per-family cells and signature effects checked against the analysis CSV/JSON and frozen protocol/runtime manifests. Operational counts and excluded runs are additionally audited in the accompanying source inventory. Commit hashes and version strings are identifiers, not experimental estimates. References and dates are handled by the citation audit.",
               "", "No empirical estimate required a new experiment. The inherited phrase 'DOI archive' was corrected to the actual public preservation archive; no DOI deposit is claimed. The main-text runtime cross-reference was corrected from S11 to S15.",
               "", "## Input SHA-256", ""]
    report += [f"- `{p}`: `{h}`" for p,h in sorted(SOURCES.items())]
    (ROOT/"reports/AIJ_NUMERICAL_AUDIT.md").write_text("\n".join(report)+"\n")
    (ROOT/"reports/AIJ_NUMERICAL_CHECKS.json").write_text(json.dumps({"checks":CHECKS,"input_sha256":SOURCES},indent=2)+"\n")
    print(f"{len(CHECKS)} numerical/configuration checks passed")



def section_review_checks():
    """Verify added descriptive claims directly from the frozen world tables."""
    src = "experiments/nmi_realizer_audit_v1/results/world_results.parquet"
    rows = read(src)
    paired = {}
    for r in rows:
        if r["policy"] in {"aligned", "role_action_blind_binding"}:
            key = (r["source"], r["family"], r["world_id"])
            policies = paired.setdefault(key, {})
            assert r["policy"] not in policies, (key, "duplicate policy")
            policies[r["policy"]] = bool(r["successful"])
    grouped = {}
    family_transitions = {}
    for (source, family, world_id), policies in paired.items():
        assert set(policies) == {"aligned", "role_action_blind_binding"}, world_id
        a, b = policies["aligned"], policies["role_action_blind_binding"]
        category = "both_pass" if a and b else "lost" if a else "gained" if b else "both_fail"
        population = "heldout" if family == "triadic_relation_reification" else "known"
        grouped.setdefault((source, population), Counter())[category] += 1
        family_transitions.setdefault((source, family), Counter())[category] += 1
    for key, expected in {
        ("C3", "known"): (0, 53, 0, 347),
        ("C3", "heldout"): (0, 0, 0, 100),
        ("C_rand", "known"): (333, 10, 15, 42),
        ("C_rand", "heldout"): (87, 0, 0, 13),
        ("DeepSeek_grammar", "known"): (81, 7, 0, 8),
    }.items():
        actual = tuple(grouped[key][k] for k in ("both_fail", "lost", "gained", "both_pass"))
        check("Blind-binding paired transitions " + "/".join(key), actual, expected, src)
    for family, expected in {
        "latent_common_cause": (0, 15), "meta_law": (3, 0), "unification": (7, 0),
    }.items():
        counts = family_transitions[("C_rand", family)]
        check("C_rand binding lost/gained " + family, (counts["lost"], counts["gained"]), expected, src)

    panel_source = "experiments/nmi_minimal_sensitivity_v1/panel_manifest.json"
    panel = read(panel_source)
    keys = {(r["family"], r["world_seed"], r["world_id"]) for r in panel["selected_worlds"]}
    check("Unique fair-comparison panel worlds", len(keys), 96, panel_source)
    random_source = "artifacts/compositional_jump_results.parquet"
    random_rows = [r for r in read(random_source)
                   if r["condition"] == "C_RAND_RANDOM_PRIMITIVES" and not r["no_jump"]
                   and (r["family"], r["world_seed"], r["world_id"]) in keys]
    model_source = "experiments/nmi_fair_interface_v1/results/deepseek_fair_cself/world_results.parquet"
    model_rows = read(model_source)
    lookups = []
    for label, values, path in [("C_rand", random_rows, random_source), ("Grammar", model_rows, model_source)]:
        lookup = {(r["family"], r["world_seed"], r["world_id"]): bool(r["condition_success"]) for r in values}
        check(label + " exact panel identity", len(values) == len(lookup) == 96 and set(lookup) == keys, True, path)
        lookups.append(lookup)
    random, model = lookups
    expected_random = {"property_to_relation": 10, "coordinate_transform": 3, "meta_law": 2, "unification": 1}
    for family in sorted({k[0] for k in keys}):
        family_keys = [k for k in keys if k[0] == family]
        check("C_rand matched-panel family " + family,
              (len(family_keys), sum(random[k] for k in family_keys)),
              (12, expected_random.get(family, 0)), random_source)
    transitions = Counter((random[k], model[k]) for k in keys)
    check("Raw-world grammar/random paired table",
          tuple(transitions[k] for k in [(False, False), (True, False), (False, True), (True, True)]),
          (66, 15, 14, 1), random_source + "; " + model_source)
    check("Joint grammar/random success family", sorted(k[0] for k in keys if random[k] and model[k]),
          ["meta_law"], random_source + "; " + model_source)


def supplementary_checks():
    """Additional family, operational and runtime claims in S11-S17."""
    src="experiments/nmi_minimal_sensitivity_v1/analysis/per_family.csv"
    for r in read(src):
        expected={"coordinate_transform":1,"hidden_regimes":2}.get(r["family"],0) if r["condition"]=="deepseek_p2" else 0
        check(r["condition"]+" "+r["family"],(int(r["successes"]),int(r["worlds"])),(expected,5 if r["condition"]=="deepseek_p2" else 12),src)
    src="experiments/nmi_fair_interface_v1/analysis/per_family.csv"
    for r in read(src):
        check("Grammar family "+r["family"],(int(r["successes"]),int(r["worlds"])),({"meta_law":9,"unification":6}.get(r["family"],0),12),src)
    src="experiments/nmi_realizer_audit_v1/analysis/per_family.csv"
    for r in read(src):
        if r["policy"]!="role_action_blind_binding" or r["source"] not in ["C3","DeepSeek_grammar"]: continue
        expected=({"hidden_regimes":26,"meta_law":21}.get(r["family"],int(r["worlds"]))) if r["source"]=="C3" else {"meta_law":5,"unification":3}.get(r["family"],0)
        check("Binding "+r["source"]+" "+r["family"],int(r["successes"]),expected,src)
    src="experiments/nmi_extension_v1/results/EXTENSION_TERMINATED.json"
    check("Superseded complete shards",read(src)["completed_verified_shards_before_stop"],8,src)
    for condition,executed in [("deepseek_matched",(0,0)),("phi_constrained",(28,1)),("phi_repair",(0,0))]:
        for pop,n,exe in zip(["known_jump","heldout_jump"],[400,100],executed):
            stem=f"experiments/nmi_extension_v1/results/{condition}/{pop}"
            src=stem+"/world_results.parquet"; rows=read(src)
            check("Excluded "+condition+" "+pop+" worlds",(len(rows),sum(r["condition_success"] for r in rows)),(n,0),src)
            src=stem+"/llm_self_plans.parquet"; rows=read(src)
            check("Excluded "+condition+" "+pop+" plans",(len(rows),sum(r["executable"] for r in rows)),(n*48*(2 if condition=="phi_repair" else 1),exe),src)
    for src,n in [("experiments/nmi_extension_v1/results/deepseek_native/known_jump/llm_calls.jsonl",404),("experiments/nmi_extension_v1/results/phi_budget/known_control/llm_calls.jsonl",1043),("experiments/nmi_extension_v1/results/_incomplete/phi_budget/known_jump_attempt_001_executor_session_terminated/llm_calls.jsonl",202)]:
        raw=(ROOT/src).read_bytes(); SOURCES[src]=hashlib.sha256(raw).hexdigest()
        check("Excluded partial call records",len(raw.splitlines()),n,src)
    src="experiments/nmi_fair_interface_v1/operational_pilots/serial_runner_excluded/llm_calls.jsonl"
    raw=(ROOT/src).read_bytes(); SOURCES[src]=hashlib.sha256(raw).hexdigest()
    rows=[json.loads(line) for line in raw.splitlines()]
    check("Excluded throughput pilot",(len(rows),len({r["world_id"] for r in rows}),sum(bool(r["full_output"]) for r in rows)),(31,8,15),src)
    for shard in [0,2,3]:
        src=f"experiments/nmi_fair_interface_v1/operational_pilots/starved_parallel_shards_excluded/shard_{shard}/llm_calls.jsonl.transport-errors"
        raw=(ROOT/src).read_bytes(); SOURCES[src]=hashlib.sha256(raw).hexdigest()
        check("Timeout-only shard "+str(shard),len(raw.splitlines()),4,src)
    src="experiments/nmi_fair_interface_v1/results/deepseek_fair_cself/initial_replay_report.json"
    check("Initial metadata mismatches",read(src)["replay_mismatches"],576,src)
    src="experiments/nmi_fair_interface_v1/results/deepseek_fair_cself/verification_correction_001.json"; corr=read(src)
    check("Corrected manifests",corr["verified_shards"],4,src)
    for stage in ["deliberation","serialization"]:
        m=corr["verified_stage_manifests"][stage]
        check("DeepSeek runtime "+stage,(m["engine_version"],m["quantization"]),("0.25.2.dev0+g752a3a504.d20260714","fp8-weights+nvfp4-kv-cache"),src)
    src="experiments/nmi_minimal_sensitivity_v1/results/phi8_cself/summary.json"
    check("Phi8 runtime",read(src)["model_manifest"]["engine_version"],"transformers-4.56.1+bitsandbytes-0.47.0",src)
    # Every printed freeze identifier must resolve locally to a commit.
    text=(ROOT/"manuscript/AIJ_SUPPLEMENTARY_METHODS.md").read_text()
    for value in sorted(set(re.findall(r"`([0-9a-f]{7,40})`",text))):
        result=subprocess.run(["rtk","proxy","git","rev-parse","--verify",value+"^{commit}"],cwd=ROOT,capture_output=True,text=True,check=True)
        check("Freeze commit "+value,result.stdout.strip().startswith(value),True,"Git object database")


if __name__=="__main__": main()
