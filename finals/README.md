# Finals — LAYA Misinformation Detection (Final Phase)

This folder is the home for the **final-phase deliverables** of the CS 668 LAYA
paired (image+text) misinformation-detection study. Everything here is labelled
with its true status as of the date shown — nothing in this folder is a final
result until the main run completes and its outputs land in `results/`.

## Status — 2026-11-22

- **Baseline paper: verified draft complete** (`paper/`). All headline numbers
  in the draft were checked against the saved-predictions audit and the
  experimental log.
- **Main training run: IN PROGRESS** (started 2026-11-22). Full grid —
  full fine-tune + LoRA arms × 2 losses × 3 step budgets — winner selected on
  the tune split only, test scored once, calibration on the reserved split.
- **Publishing targets (on completion):** model →
  `RafiulHaiderbro/laya-vision-fullft-mmfakebench` (Hugging Face Hub);
  demo Space → `RafiulHaiderbro/laya-misinfo-demo`.

## What will land here when the main run completes

- The **executed notebook** (replacing the staged copy in `notebook/`) — the
  run's cell-by-cell record with real outputs and result charts.
- **Grid results + H1–H5 verdicts** in `results/` (12 configs, tune macro-F1,
  winner, test-once numbers, calibration ECE before/after).
- The **final paper** in `paper/` (baseline draft + trained results, known
  draft flags fixed).
- **Model / Space links** added to `results/RESULTS.md`.

## Folder map

| Folder | Contents |
|---|---|
| `status/` | Situation log + change plan (2026-11-22) and the experiment history & plan — the full audit trail of how this phase was run. |
| `paper/` | Verified baseline paper draft (PDF + LaTeX) with a note on its known flags. |
| `notebook/` | The staged Colab notebook (25 cells, 0 outputs, visuals embedded) + note. The executed record replaces it on completion. |
| `code/` | `laya_trainer.py` (trainer built on the laya library primitives), `visualnews_stream.py` (streaming image verifier for NewsCLIPpings), `space_app.py` + `space_requirements.txt` (Hugging Face Space app). |
| `visuals/` | The three explanatory diagrams embedded in the notebook: input, process, model. |
| `results/` | `RESULTS.md` — baseline (BEFORE) numbers now; grid + verdicts on completion. |

## Data terms

No datasets, benchmark images (beyond the three diagrams in `visuals/`), or
row-level predictions are included — same terms as the rest of this repo.
