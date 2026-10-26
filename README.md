# CS 668 Midterm — Three-Track Baseline and Paper

Private working repository for the CS 668 Analytics Capstone midterm.

## Contents

- `paper/` — LaTeX source, compiled PDF (10 pages), and build notes for *Three Modalities, Three Tracks*.
- `01_PROJECT_SYNTHESIS.md` — how the pretrained baseline maps to POS Objective 5.
- `03_DEFENSE_QA.md` — prepared defence questions and answers.
- `reports/` — baseline, transfer probe, and planning records.
- `data_summaries/` — public aggregate JSON used by the dashboards.
- `figures/`, `presentation/` — midterm deck assets (PPTX, PDF, build script).
- `reference/` — POS PDF and ontology reference.
- `notebooks/` — analysis notebooks (the original EDA notebook with embedded dataset images is excluded).

## Build the paper

```bash
cd paper
tectonic -X compile three_track_paper.tex
```

## Data terms

No raw benchmark images or row-level predictions are included. MMFakeBench forbids redistribution of images or derived data; NewsCLIPpings/VisualNews terms are unresolved; VERITE images are gated. This repository is private and for coursework only.

## Authors

Rafiul Haider (combined track), Harika Etikela (text track), Ananya (image track).

**TODO:** add Ananya's full surname in `paper/three_track_paper.tex` before public submission.
