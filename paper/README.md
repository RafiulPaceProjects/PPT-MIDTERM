# Three-track paper draft

`three_track_paper.tex` → `three_track_paper.pdf` (10 pages, A4, compiled).

Authors: Rafiul Haider (combined track), Harika Etikela (text track), Ananya (image track).
Course: CS 668 Analytics Capstone, Pace University; instructor Dr. Krishna Bathula.

## Build

```bash
cd MIDTERM_PRETRAINED_BASELINE/paper
tectonic -X compile three_track_paper.tex
```

Tectonic is installed via Homebrew (`brew install tectonic`). No BibTeX run is needed; the bibliography is inline.

## What the paper contains

1. Abstract and introduction with three-track framing and four contributions.
2. Related work across WELFake, CIFAKE, MMFakeBench, VERITE, NewsCLIPpings, LAMAR.
3. Datasets table, leakage/overlap audit, exposure and source-metadata notes.
4. Methods: text pipeline, image ladder, combined zero-shot arms, frozen-feature probe, metrics and bootstrap.
5. Results: WELFake table, CIFAKE table, combined table, source-pair analysis, cross-track synthesis.
6. Discussion and limits, including the prompt-mismatch caveat for unimodal arms.
7. Future work: six conditions, Attention/Gate heads over frozen features, targets and decision rule, compute setup, captioning, Streamlit verdict app, ethics/terms.
8. Appendix: artifact list, gates/audit/tier-0, references.

## Visuals

Eight figures and six tables: key-numbers cards, the LAYA-Vision pipeline, the three-track design, WELFake and CIFAKE result charts, the MMFakeBench accuracy chart with ranges, calibration, the 14-pair source-effect lollipop, and a LAYA setup table.

## Provenance and caveats

- Combined-track numbers come from the verified artifacts listed in the appendix (22/22 gates, 28/28 claims audit, tier-0 identical).
- Text and image numbers are reported from the track owners' midterm experiments; they were not independently recomputed here.
- The NewsCLIPpings probe test result (57.4%) is held out; MMFakeBench test numbers are post-hoc.
- No dataset images, rows, or per-item predictions are redistributed in this paper.
- **TODO before submission:** add Ananya's full surname in the author block (the LaTeX source has a `% TODO` marker). Confirm Harika's and Ananya's approval to be listed as authors and to include their track results.
- The paper deliberately keeps the three tracks separate; do not sort the scores into a leaderboard.
