# Data and code availability

## Data availability

All synthetic-world definitions, confirmatory result tables, comparison tables, configuration and reproducibility manifests, ancestry records, and replay artifacts underlying the study are present in the repository. The original Phi-4 confirmatory state is preserved by commit, tag and archive branch. The minimal targeted sensitivity protocol, fixed seed panel, model configurations, raw call ledgers, completion validations, replay reports, analysis tables and figure source data occupy the separate `experiments/nmi_minimal_sensitivity_v1` namespace. Historical files are not overwritten or reclassified as extension results. No human, personal, clinical or restricted third-party data were used.

**Pre-submission action:** create an immutable tagged release, deposit it in a DOI-minting repository such as Zenodo, and insert the DOI and accession here. A branch URL alone is insufficient for the final version.

## Code availability

The repository contains the source code for procedural generation, typed representation search, exact incumbent oracles, prospective intervention selection, J0–J5 evaluation, offline historical attrition reconstruction, targeted sensitivity analysis, statistical analysis, figure generation and deterministic replay. The archival release should identify both the publication Git commit and DOI. Frozen `microsoft/phi-4` and `deepseek-ai/DeepSeek-V4-Flash-Vision-Exp` weights are referenced by exact repository identity and revision and are not redistributed; runtime versions, endpoint model metadata and decoding configurations are retained in manifests.

## Reviewer access

At submission, provide editors and referees with access to the complete repository or an anonymized immutable snapshot, including large artifacts if the public archival DOI is not yet active. Verify every path from the evidence-source map in a clean checkout.
