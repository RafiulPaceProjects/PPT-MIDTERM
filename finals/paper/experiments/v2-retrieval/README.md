# Experiment fork — v2 retrieval study (SearXNG evidence arm)

This branch (`exp/v2-retrieval`) is a FORK of the paper path for experimenting with the
retrieval-augmented LAYA idea: caption -> NLP entity extraction (+ deepseek-flash claim
formulation) -> SearXNG search -> evidence snapshots -> LAYA judges pair+evidence on
NewsCLIPpings, against the v1 record's H2 null (trained 0.5104 vs baseline 0.5141,
7,024 validation rows).

Rules of the fork:
- The main paper line (finals/paper/draft/, versions v0.x -> v1.0) is NOT touched here.
- This fork has its OWN version series: exp-v0.1, exp-v0.2, ... tagged paper-exp-v2-*.
  A fork version exists only when the paper gate passes on this branch's draft.
- Numbers may enter this draft only from (a) the v1 final_results_bundle.json, or
  (b) the v2 probe's own verified artifacts in ~/workspace/misinfo_run/v2_probe/,
  each with its source named in the CHANGELOG entry that introduces it.
- Contamination controls from the probe design are part of the study, not optional:
  fact-check domains excluded in the headline arm, included in a reported second arm.
- PROMOTION RULE: nothing from this fork merges into the main paper line unless the
  probe produces verified results AND the owner elects to promote it. Until then this
  is an experiment draft, labelled as such everywhere it appears.
