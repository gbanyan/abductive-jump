# NMI realizer-dependence audit v1

This namespace contains a post-confirmatory, inference-free causal audit of the fixed motif-to-basis realizer. It does not alter or replace AJ5, CJ5 or the separately frozen model-sensitivity results.

The protocol freezes three archived candidate sources and eleven realization policies before counterfactual replay. Candidate representations, slots and world panels are fixed. Each counterfactual expression is fitted only to public observations, and its maximum-separation public intervention query is committed before evaluation against hidden outcomes. No language-model endpoint is contacted.

Run after verifying the protocol and source hashes:

```bash
python scripts/run_nmi_realizer_audit_v1.py
```

Results must be written once to `results/`, validated against the aligned archived verdicts and analyzed at the world level. Candidate rows are attrition units, not independent replicates.
