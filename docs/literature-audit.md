# Literature audit

Status: pre-experimental audit, 2026-09-02. This document positions the question and fixes distinctions that the implementation must preserve. It is not a novelty claim based on keyword absence.

## Operational target

The target is not unusual text, a high-scoring artifact, or a hypothesis judged interesting. It is a candidate typed representation outside a frozen incumbent language that (i) remains compatible with observations, (ii) commits prospectively to a discriminating intervention, and (iii) beats an exact or bounded incumbent-space oracle on the unseen result. The central factorial separates who proposes the representation from who reasons within it.

## Adjacent work and the remaining test

### LLM evolutionary and quality-diversity search

[FunSearch](https://www.nature.com/articles/s41586-023-06924-6) evolves a designated part of a program inside a user-provided executable skeleton, evaluates candidates automatically, and maintains multiple islands. It establishes that frozen-LLM proposals plus selection can produce strong and occasionally new mathematical constructions. Its search language and evaluator are supplied in advance; it does not isolate escape from an already adequate explanatory representation or compare representation mutation with an incumbent-space oracle under interventions.

[ShinkaEvolve](https://arxiv.org/abs/2509.19349) improves sample-efficient program evolution using parent selection, code-novelty rejection sampling, and model selection. [Darwin Gödel Machine](https://arxiv.org/abs/2505.22954) grows an archive of self-modifying coding agents and validates modifications on coding benchmarks. These motivate archive and ancestry controls, but their unit of novelty is functioning code/agent behavior rather than a formally separated representation genome with prospective causal validation.

Quality-diversity methods, especially MAP-Elites, motivate retaining high-quality candidates across behavioral descriptors rather than selecting only the global best. Here descriptors must be typed structural facts—latent/state/regime counts, relation arity, motifs, ancestry, equation family, and prediction signature—not embedding novelty. Archive occupancy is diagnostic, never a jump verdict.

### AI scientists, hypothesis agents, and falsification

[The AI Scientist](https://www.nature.com/articles/s41586-026-10265-5) automates idea generation, code, experiments, analysis, writing, and review in machine-learning research. [Co-Scientist](https://www.nature.com/articles/s41586-026-10644-y) uses generation, reflection, ranking, evolution, proximity, and meta-review agents and reports empirical biomedical validation. [Robin](https://www.nature.com/articles/s41586-026-10652-y) integrates hypothesis generation, experimental planning, and data analysis. These systems show the value of iterative and falsification-oriented scaffolds, but broad scientific usefulness does not by itself identify a representation-proposal bottleneck. Natural-language novelty/plausibility ratings also cannot certify structural escape.

The present design therefore holds the reasoning model fixed, matches calls/tokens/evaluations/interventions, separates proposal source from reasoning, and assigns every primary truth judgment to executable code.

### Abduction and the “jump” claim

[Zahavy, *LLMs Can't Jump*](https://philsci-archive.pitt.edu/28024/1/Scientific_Invention_Position_Paper%20%2817%29.pdf) frames abduction as a move from experience to new axioms and argues that current text models lack the grounded substrate behind Einstein's conceptual jump. This is a position claim, not the operational benchmark used here. The project tests a narrower mechanism: whether an external typed mutation process improves validated escape in synthetic procedural worlds. It cannot establish that LLMs universally cannot jump, that embodiment is necessary, or that the scaffold reproduces human discovery.

Existing empirical projects using invented worlds and executable held-out predictions are directionally relevant, but predictive success alone can still be ordinary system identification if the correct model is expressible in the supplied grammar. This project makes the incumbent grammar explicit and freezes an escape predicate before evaluation.

### Representation invention, theory change, program synthesis, and symbolic regression

Program synthesis and symbolic regression search executable expressions, often with exact evaluation and complexity control. They are strong baselines and supply oracle machinery where the incumbent grammar is finite. Their ordinary setting searches expressions in a fixed grammar. The study's key comparison is therefore value/equation search inside that grammar versus mutations that alter its typed primitives and relations.

Representation learning usually changes latent features to improve prediction, while constructive induction, predicate invention, ontology revision, and scientific theory-change work explicitly add or revise concepts. These are the closest conceptual ancestors of the representation genome. The differentiator sought here is not “first concept invention,” but a controlled, seed-replicated test coupling formal grammar escape to prospectively frozen intervention gain over the best incumbent expression.

### Causal discovery

Causal discovery formalizes observational equivalence and the identifying power of interventions. It supplies natural benchmark families and exact intervention semantics. However, selecting among DAGs over a fixed observed variable set is not necessarily a representation jump. Latent invention, state invention, property-to-relation conversion, regime construction, and variable/function promotion count only when forbidden by the frozen incumbent grammar.

## Threats fixed before implementation

1. Family generators necessarily encode a ground truth; proposal operators must be generic and receive no family label or hidden truth.
2. A mutation name can leak a solution. Confirmatory proposals receive only typed graph state, permitted generic operators, and observations; lexicalizations are randomized.
3. Structural difference alone is insufficient. Canonical grammar membership proves J1, while prospective loss and falsification prove J3–J5.
4. Added complexity can mimic escape. No-jump and unnecessary/overcomplicated/invalid mutations measure false acceptance.
5. More sampling can mimic a proposal advantage. B0–B5 share frozen accounting constraints and retain a compute-quality frontier.
6. Synthetic success supports only the tested procedural families. A held-out family can strengthen transfer evidence but cannot justify universal claims.

## Candidate contribution, stated conservatively

- A benchmark for validated representation-level escape from locally adequate, explicitly bounded incumbent hypothesis spaces.
- A proposal-versus-reasoning factorial using the same frozen model.
- A deterministic J0–J5 verdict with incumbent oracle, prospective intervention freeze, no-jump false-positive measurement, and structural rather than semantic archive descriptors.

These remain candidate contributions until the implementation and experiments survive adversarial audit.

