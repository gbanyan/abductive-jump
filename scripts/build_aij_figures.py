"""Render AIJ figures from frozen artifacts; never invoke model inference.

Run from the repository with `.venv/bin/python scripts/build_aij_figures.py`.
The JSON sidecar records plotted data and SHA-256 hashes of every input.
"""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pyarrow.parquet as pq
from matplotlib.patches import FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "manuscript/figures/aij"
SOURCES: dict[str, str] = {}
DATA: dict = {}
BLUE, ORANGE, GREY = "#236A88", "#AC5E26", "#66717B"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                     "axes.spines.top": False, "axes.spines.right": False,
                     "pdf.fonttype": 42, "svg.fonttype": "none"})


def read(path):
    p = ROOT / path
    SOURCES[path] = hashlib.sha256(p.read_bytes()).hexdigest()
    if p.suffix == ".parquet":
        return pq.read_table(p).to_pylist()
    if p.suffix == ".csv":
        with p.open() as stream:
            return list(csv.DictReader(stream))
    return json.loads(p.read_text())


def save(fig, name):
    fig.tight_layout(pad=1.5)
    fig.savefig(OUT / f"{name}.png", dpi=220, facecolor="white")
    fig.savefig(OUT / f"{name}.svg", facecolor="white")
    plt.close(fig)


def box(ax, xy, width, height, text, color=BLUE):
    ax.add_patch(FancyBboxPatch(xy, width, height, boxstyle="round,pad=0.012",
                              facecolor="#F4F6F8", edgecolor=color))
    ax.text(xy[0]+width/2, xy[1]+height/2, text, ha="center", va="center", fontsize=10)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(10, 4.2)); ax.axis("off")
    box(ax, (.02,.59), .25,.27, "FREEZE\nLanguage + comparator set\nPublic observations\nHidden data splits")
    box(ax, (.37,.59), .25,.27, "CONSTRUCT + COMMIT\nRepresentation + expression\nAction + prediction\nSplit hashes")
    box(ax, (.72,.59), .25,.27, "REVEAL + TEST\nHidden intervention outcome\nSeparate falsification cases", ORANGE)
    for x in [.28,.63]: ax.annotate("", (x+.085,.72), (x,.72), arrowprops={"arrowstyle":"->"})
    ax.axvline(.675, ymin=.05, ymax=.94, color=ORANGE, ls="--")
    ax.text(.665,.47,"Outcome reveal",ha="right",color=ORANGE)
    for x, label in zip([.02,.235,.45,.72,.855], ["J0\nIncumbent fit", "J1-J2\nEscape + fit", "J3\nDiscrimination", "J4\nGain", "J5\nSurvival"]):
        box(ax,(x,.13),.19 if x<.6 else .115,.22,label, BLUE if x<.6 else ORANGE)
    save(fig,"figure_1_assay")

    aj = read("artifacts/condition_summary.parquet")
    gates = read("artifacts/nmi_gate_attrition.parquet")
    DATA["AJ5"] = aj
    fig, axes = plt.subplots(1,2,figsize=(10,4.6),gridspec_kw={"width_ratios":[1,1.3]})
    labels=["B0 direct","B1 sampling","B2 fixed space*","B3 attributes*","B4 portfolio","B5 distinct"]
    vals=[r["jsr"]*100 for r in aj]
    axes[0].barh(labels,vals,color=[BLUE,BLUE,GREY,GREY,ORANGE,ORANGE])
    axes[0].errorbar(vals, range(len(aj)),
                     xerr=[[100*(r["jsr"]-r["jsr_ci_low"]) for r in aj],
                           [100*(r["jsr_ci_high"]-r["jsr"]) for r in aj]],
                     fmt="none", ecolor="#192b3b", capsize=3)
    for i,r in enumerate(aj):
        axes[0].text(100*r["jsr_ci_high"]+1,i,f'{round(r["jsr"]*r["jump_worlds"])}/400',va="center",fontsize=9)
    axes[0].invert_yaxis(); axes[0].set_xlim(0,49); axes[0].set_xlabel("Successful worlds (%)")
    axes[0].set_title("a  World-level outcomes")
    for prefix,color in [("B0",BLUE),("B1",GREY),("B4",ORANGE),("B5","#65519A")]:
        r=next(r for r in gates if r["study"]=="AJ5" and r["population"]=="jump" and r["condition"].startswith(prefix))
        axes[1].plot(range(6),[r[f"through_j{i}"] for i in range(6)],"o-",label=prefix,color=color)
    axes[1].set_xticks(range(6),[f"J{i}" for i in range(6)])
    axes[1].set_ylabel("Candidates retained (of 1,200)"); axes[1].legend(frameon=False)
    axes[1].set_title("b  Cumulative candidate attrition")
    save(fig,"figure_2_aj5")

    cj=read("artifacts/compositional_cost_frontier.parquet")
    prefixes=["C0_","C1_","C2_","C_RAND_","C3_","C_SELF_"]
    cj=[next(r for r in cj if r["condition"].startswith(p)) for p in prefixes]
    DATA["CJ5"]=cj
    fig, axes=plt.subplots(1,2,figsize=(10,4.1),sharey=True)
    for ax, key,denom,title in zip(axes,["existing_successes","heldout_successes"],[400,100],["a  Known families","b  Search-side held-out family"]):
        y=np.arange(6); vals=[r[key]/denom*100 for r in cj]
        ax.barh(y, vals,color=[GREY,BLUE,GREY,BLUE,ORANGE,GREY])
        for i,r in enumerate(cj): ax.text(vals[i]+2,i,f'{r[key]}/{denom}',va="center",fontsize=9)
        ax.set_yticks(y,["C0 fixed space*","C1 atomic","C2 depth one","Random policy","C3 structured","Historical self†"])
        ax.set_xlim(0,124); ax.set_xlabel("Successful worlds (%)"); ax.set_title(title)
    axes[0].invert_yaxis()
    save(fig,"figure_3_cj5")

    replay=read("artifacts/nmi_component_audit.json")["c3_without_llm"]
    DATA["C3_replay"]=replay
    fig,ax=plt.subplots(figsize=(10,4.4)); ax.axis("off")
    box(ax,(.02,.55),.26,.30,"DETERMINISTIC PATH\nGraph search -> realizer -> fit\nRanking -> selected action")
    box(ax,(.37,.55),.25,.30,"EVALUATED ARTIFACT\nRepresentation + expression\nParameters + action + prediction")
    box(ax,(.72,.55),.25,.30,"REPLAY WITHOUT MODEL\n2,400 / 2,400 verdicts match\n500 / 500 jump worlds retained",ORANGE)
    for x in [.29,.63]: ax.annotate("",(x+.07,.70),(x,.70),arrowprops={"arrowstyle":"->"})
    box(ax,(.02,.09),.26,.23,"MODEL RESPONSE\nScientific fields overwritten\nExplanation retained, unscored",GREY)
    box(ax,(.37,.09),.60,.23,"Attribution follows the final field, not the presence of a model call.\nReplay tests this implemented path; the inventory records supplied algebra.",GREY)
    save(fig,"figure_4_provenance")

    fair=read("experiments/nmi_fair_interface_v1/analysis/gate_attrition.csv")
    paired=read("experiments/nmi_fair_interface_v1/analysis/paired_crand_comparison.csv")[0]
    DATA["grammar_attrition"]=fair; DATA["paired_worlds"]=paired
    fig,axes=plt.subplots(1,3,figsize=(10.5,4.2),gridspec_kw={"width_ratios":[1,1,1.15]})
    stages=["plan_schema_valid","executable"]
    axes[0].bar(["Schema\nvalid","Executable"],[int(next(r for r in fair if r["stage"]==s)["passed"]) for s in stages],color=[BLUE,ORANGE])
    axes[0].set_ylim(0,5300); axes[0].set_ylabel("Plan opportunities (of 4,608)")
    for i,v in enumerate([4608,3939]): axes[0].text(i,v+90,f"{v:,}",ha="center")
    axes[0].set_title("a  Format to execution")
    axes[1].bar(["Executable\nslots","J1-J2","J3-J5"],[280,236,21],color=[GREY,BLUE,ORANGE])
    for i,v in enumerate([280,236,21]): axes[1].text(i,v+6,str(v),ha="center")
    axes[1].set_ylim(0,330); axes[1].set_ylabel("Selected candidate slots (of 288)"); axes[1].set_title("b  Executed candidates")
    matrix=np.array([[int(paired["both_fail"]),int(paired["comparison_only_success"])],[int(paired["reference_only_success"]),int(paired["both_succeed"])]])
    axes[2].imshow(matrix,cmap="Blues",vmin=0,vmax=75)
    for (i,j),v in np.ndenumerate(matrix): axes[2].text(j,i,str(v),ha="center",va="center",color="white" if v>40 else "black",fontsize=15)
    axes[2].set_xticks([0,1],["Fail","Pass"]); axes[2].set_yticks([0,1],["Fail","Pass"])
    axes[2].set_xlabel("Model-interface world outcome"); axes[2].set_ylabel("Random-policy world outcome"); axes[2].set_title("c  Same 96 worlds")
    save(fig,"figure_5_interface")

    real=read("experiments/nmi_realizer_audit_v1/analysis/condition_summary.csv")
    DATA["realizer"]=real
    def row(s,p,policy): return next(r for r in real if (r["source"],r["population"],r["policy"])==(s,p,policy))
    fig,axes=plt.subplots(1,2,figsize=(10,4.9),gridspec_kw={"width_ratios":[1,1.3]})
    groups=[("C3","known"),("C3","heldout"),("C_rand","known"),("C_rand","heldout"),("DeepSeek_grammar","fixed_known_panel")]
    for d,pol,col in [(-.17,"aligned",BLUE),(.17,"role_action_blind_binding",ORANGE)]:
        rr=[row(s,p,pol) for s,p in groups]
        axes[0].barh(np.arange(5)+d,[100*float(r["jsr"]) for r in rr],height=.31,color=col,label="Aligned" if d<0 else "Blind binding")
        for i,r in enumerate(rr): axes[0].text(100*float(r["jsr"])+1,i+d,r["successes"],va="center",fontsize=8)
    axes[0].set_yticks(range(5),["C3 known (400)","C3 held-out (100)","Random known (400)","Random held-out (100)","Model panel (96)"])
    axes[0].invert_yaxis(); axes[0].set_xlim(0,120); axes[0].set_xlabel("Successful worlds (%)"); axes[0].legend(fontsize=8,frameon=False,loc="lower right"); axes[0].set_title("a  Binding information")
    masks=["relation_arity_3","unobserved_dependency","unobserved_selector","bound_relation","self_composed_function","temporally_indexed_recurrence","multi_argument_function","shared_rule_binding"]
    losses=[sum(int(row("C3",p,"aligned")["successes"])-int(row("C3",p,"mask_signature:"+m)["successes"]) for p in ["known","heldout"]) for m in masks]
    axes[1].barh(["Triadic relation","Unobserved dependency","Hidden selector","Bound relation","Self-composed function","Temporal recurrence","Multi-argument function","Shared-rule binding"],losses,color=ORANGE)
    for i,v in enumerate(losses): axes[1].text(v+2,i,str(v),va="center",fontsize=9)
    axes[1].invert_yaxis(); axes[1].set_xlim(0,125); axes[1].set_xlabel("C3 successes lost (of 500 fixed worlds)"); axes[1].set_title("b  Individual signature masks")
    save(fig,"figure_6_realizer")

    # Reconstruct one already archived world, not a new experiment.
    from abductive_jump.compositional_worlds import generate_heldout_world
    from abductive_jump.worlds import predict
    from abductive_jump.oracle import incumbent_oracle
    world=generate_heldout_world(40000)
    archived=read("artifacts/compositional/confirmatory-heldout/candidate_results.parquet")
    selected=next(r for r in archived if r["world_seed"]==40000 and r["condition"].startswith("C3_") and r["validated_jump"])
    assert selected["exact_designer_intervention_id"]=="test-0"
    assert world.interventions[0].outcome==2268 and world.falsification[0].outcome==1620
    DATA["worked_example"]={"world_id":world.world_id,"seed":40000,"candidate":selected,
                            "intervention_outcome":world.interventions[0].outcome,
                            "falsification_outcome":world.falsification[0].outcome}
    fig,axes=plt.subplots(1,2,figsize=(10,4.1))
    z=np.array([5,6,7]); axes[0].plot(z,[1944]*3,"o--",color=GREY,label="Selected incumbent: 9x³")
    axes[0].plot(z,9*6*z*6,"o-",color=BLUE,label="Realized candidate: 9xzw")
    axes[0].set_xticks(z,["5\nFalsification","6\nObservation","7\nIntervention"])
    axes[0].set_ylabel("Predicted outcome (x = w = 6)"); axes[0].set_ylim(1400,2450); axes[0].legend(fontsize=9,frameon=False)
    axes[0].set_title("a  Observational agreement, hidden separation")
    axes[1].axis("off")
    box(axes[1],(.02,.60),.94,.29,"Graph edits: reify edge -> arity 3 -> bind z -> bind w\nSupplied realizer: xzw basis; fitted coefficient: 9")
    box(axes[1],(.02,.13),.94,.32,"Commit test-0: incumbent 1,944; candidate 2,268\nReveal: 2,268; separate fals-0: 1,620\nAll six gates pass; predictive form was supplied.",ORANGE)
    axes[1].set_title("b  Archived seed 40000")
    save(fig,"figure_7_worked")
    for p in ["src/abductive_jump/compositional_worlds.py", "scripts/build_aij_figures.py"]:
        SOURCES[p]=hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
    (OUT/"source_data.json").write_text(json.dumps({"input_sha256":SOURCES,"data":DATA},indent=2,default=str)+"\n")
    print(f"Rendered 7 figures in {OUT}")


if __name__ == "__main__":
    main()
