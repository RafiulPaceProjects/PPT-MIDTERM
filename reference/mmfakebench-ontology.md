# MMFakeBench research ontology

This is a compact, provenance-aware ontology assembled from the Obsidian vault, the project reports, the local LAYA validation output, and the targeted literature search completed 2026-10-18.

## Node types

- **Concept**: a construct or research question, such as veracity, mismatch, source leakage, evidence grounding, or calibration.
- **Paper**: a verified paper or clearly marked discovery lead.
- **Result**: one reported or locally measured result with its protocol attached. Results are not pooled into one leaderboard.
- **Idea**: a hypothesis, experiment, design decision, or open question.

## Edge types

`Paper reports Result`, `Result evaluates Concept`, `Result supports/qualifies/contradicts Concept`, `Idea motivated_by Result/Paper/Concept`, `Idea tests Concept`, and `Concept related_to Concept`.

## Integrity rules

- A mismatch signal is not the same thing as a false claim or deceptive intent.
- Binary and four-way results, validation and test results, and different sample sizes are not directly comparable.
- Source and image-path metadata are audit variables, not model inputs.
- Reported, calculated, inferred, and proposed claims remain distinct.
- Verification status is separate from model confidence and calibration.

The interactive 3D view is generated from the same compact graph data and uses the local notes as provenance. The primary source inventory is `3 Resources/Papers & Datasets/References.md` in the Obsidian vault; local measurements are linked to `data/processed/` and the findings register.
