# cs667-deck

Live presentation (reveal.js) and static record (.pptx) for the CS 667 midterm:
*Predicting Restaurant Inspection Grades in New York City* — Rafiul Haider & Shadman Rahman.

## Status

Only the data layer is built so far. The slides, theme, mascot, interactions and
export pipeline are on hold until the missing spec parts arrive (Parts 3–10 of the
build prompt).

| Path | What it is |
|---|---|
| `source/…RestaurantInspections.ipynb` | The executed notebook, the single source of truth (copied from Google Drive, last modified 2026-10-22 00:42 UTC). |
| `source/figures/` | The 15 figures the notebook rendered, extracted byte for byte. |
| `source/html/` | The HTML maps embedded in the notebook outputs: `nyc_zip_3d_hero.html`, `map_density.html`, `nyc_scatter3d.html`. |
| `data/*.json` | DataExports parsed from the notebook's printed outputs. |
| `data/MANIFEST.md` | Source cells and checksum for every export. |
| `data/FIXTURES.md` | Exports checked against the numbers quoted in the spec. |

## Rebuild

```sh
python3 tools/extract_notebook_assets.py   # figures + HTML maps
python3 tools/export_deck_data.py          # data/*.json, MANIFEST.md, FIXTURES.md
```

`export_deck_data.py` exits non-zero while any fixture mismatches. That's
deliberate: it's the numbers QA gate.

## Not recoverable from the notebook

Colab saved these outputs as "Output hidden", so they aren't in the file:
`map_risk_zip.html`, `map_initial_vs_reinspection.html` and `nyc_hex_3d.html`. The
notebook also never wrote `nta_risk_table.csv` or `modeling_table.csv` into its
outputs, and NYC Open Data can't be reached from this environment, so the notebook
can't be re-run here.
