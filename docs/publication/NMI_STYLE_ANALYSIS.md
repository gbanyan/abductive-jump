# NMI Article style analysis

Sample window: 2024–2026. Access date: 2 September 2026. Only pages labelled **Article** were used for structural analysis; editorials and Comments were read only as policy/positioning signals.

## Sample

| Year | Article | Why sampled |
|---|---|---|
| 2024 | [Leveraging large language models for predictive chemistry](https://www.nature.com/articles/s42256-023-00788-1) | LLM scientific use |
| 2024 | [Augmenting large language models with chemistry tools](https://www.nature.com/articles/s42256-024-00832-8) | Tool-using LLM framework |
| 2024 | [A collective AI via lifelong learning and sharing at the edge](https://www.nature.com/articles/s42256-024-00800-2) | Multi-component AI system |
| 2024 | [A large-scale audit of dataset licensing and attribution in AI](https://www.nature.com/articles/s42256-024-00878-8) | Audit-style evidence |
| 2024 | [Evaluating generalizability of artificial intelligence models for molecular datasets](https://www.nature.com/articles/s42256-024-00931-6) | Benchmark validity |
| 2025 | [Evolutionary optimization of model merging recipes](https://www.nature.com/articles/s42256-024-00975-8) | Evolutionary search and ablations |
| 2025 | [What large language models know and what people think they know](https://www.nature.com/articles/s42256-024-00976-7) | Controlled LLM experiments |
| 2025 | [Visual cognition in multimodal large language models](https://www.nature.com/articles/s42256-024-00963-y) | Cognitive capability benchmark |
| 2025 | [Large language models for scientific discovery in molecular property prediction](https://www.nature.com/articles/s42256-025-00994-z) | Nearest journal topic |
| 2025 | [Explainable AI reveals Clever Hans effects in unsupervised learning models](https://www.nature.com/articles/s42256-025-01000-2) | Mechanism-sensitive evaluation |
| 2025 | [Embodied large language models enable robots to complete complex tasks in unpredictable environments](https://www.nature.com/articles/s42256-025-01005-x) | System evaluation and transfer |
| 2025 | [A framework to evaluate machine learning crystal stability predictions](https://www.nature.com/articles/s42256-025-01055-1) | Benchmark/framework contribution |
| 2025 | [Human-like object concept representations emerge naturally in multimodal large language models](https://www.nature.com/articles/s42256-025-01049-z) | Representation-focused framing |
| 2026 | [Capable language models can outgrow the benefits of collaboration](https://www.nature.com/articles/s42256-026-01268-y) | Matched factorial evaluation |
| 2026 | [Beyond representational alignment with brain-guided language models for robust reasoning](https://www.nature.com/articles/s42256-026-01278-w) | Reasoning and representation |
| 2026 | [Large language models as uncertainty-calibrated optimizers for experimental discovery](https://www.nature.com/articles/s42256-026-01283-z) | Experimental discovery and calibration |

## Recurring structural conventions

1. **Titles state the empirical object and result.** They are declarative but avoid “we,” acronyms and sweeping intelligence claims. Method-brand titles occur when the system itself is the contribution; capability papers more often name the bounded capability.
2. **Abstracts follow problem–gap–method–result–meaning.** They introduce a broad problem in one or two sentences, name the unresolved comparison, specify the controlled design, give two to four quantitative results and close with a bounded implication. Caveats often appear through qualifiers rather than a separate limitation sentence.
3. **Introductions narrow quickly.** A broad motivation is followed by the closest methodological problem, then explicit limitations of existing evaluations, and finally “Here we…” with the experimental contrast and contribution. Philosophical framing is brief and operationalized before the Results.
4. **Results subheadings make claims.** They are topical and readable, not labels such as “Experiment 1.” The first subsection establishes the assay; middle subsections report the decisive comparison and mechanism; later subsections cover robustness, transfer or failure modes.
5. **Figures carry the narrative.** Figure 1 defines the problem and pipeline; Figure 2 usually contains the primary effect; Figure 3 explains mechanism/ablation; Figure 4 handles generalization or robustness. Dense provenance and exhaustive results move to Extended Data.
6. **Statistics accompany the first relevant numerical claim.** Exact sample units and uncertainty are stated locally. Authors distinguish descriptive counts from inferential comparisons and qualify extrapolation beyond the sampled domain.
7. **Discussion opens with the answer.** It separates empirical result, interpretation and scope. Limitations are concrete—dataset, model, domain, construct or deployment—not generic. Recent Articles avoid treating a strong benchmark score as proof of a broad cognitive faculty.
8. **Jargon is introduced through the measurement.** New terms are defined once, visually anchored and then used consistently. Acronym density is low in titles and opening paragraphs.

## Application to this manuscript

- Open with the measurement problem: high-quality hypotheses can remain inside a supplied language, so novelty scores cannot identify representation escape.
- Introduce “bounded representation-level escape” only after defining the incumbent grammar and prospective intervention criterion.
- Keep AJ5 as the assay-validation result and CJ5 as the decisive compositional test.
- Put the proposal–reasoning factorial in the main narrative because it supplies mechanism, not merely an ablation.
- State the main result with counts and uncertainty, then immediately scope it to the tested frozen model and synthetic families.
- Reserve philosophical “jump” language for motivation and Discussion; never use it as a measured variable.
- Use four main figures plus one compact design table; move family tables, dose curves, seed sensitivity and full replay provenance to Extended Data.

## House-style guardrails

- No hype words (“revolutionary,” “genuine,” “human-like”) unless directly tested.
- No anthropomorphic attribution to the model; proposals are emitted by a frozen model inside a human-designed scaffold.
- Prefer “supports,” “is consistent with,” and “within this benchmark” over “proves.”
- State registered operator depth, not global conceptual distance.
- Repeat the three most important boundaries in Abstract, end of Results and Discussion: synthetic families, one frozen model/interface, and supplied meta-level operators.

