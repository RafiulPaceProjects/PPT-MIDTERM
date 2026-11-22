# LAYA — Experiment History & Forward Plan
Compiled 2026-11-22 from the workspace record (Oct 5 – Oct 25, 2026). Rafiul Haider, Pace Analytics Capstone (CRN 72369), CS 668 Team 3 combined track.

## Phase 0 — Design (Oct 5–12)
- POS Objective 4 settled as caption-assisted / paired Laya: image + text into LAYA-Vision, 4-class on MMFakeBench (original / textual distortion / visual distortion / mismatch).
- Model verified against its card: 421M ModernBERT-large typed-decision model, Apache 2.0, 512-token English context (~320 usable for state), near-chance zero-shot (0.362 vs 0.461 majority on typed-decisions; 0.766 only after fine-tuning), ships over-confident (raw ECE ~0.466).
- Gaps flagged Oct 12: no pinned checkpoint/wording, no calibration measure, captioning bottleneck, option-order flips (~35.7% base), over-long rows skipped not truncated.

## Phase 1 — Baseline study, 105-row tune + 1,000-row validation (Oct 19)
Tune (105 rows, default wording, native macro-F1): text 0.237 · vision+text 0.143 · image 0.223 · paired 0.259 · final 0.312 · fusion 0.238.
1,000-row validation (macro-F1): hosted text 0.203 · local text 0.221 · LAYA-Vision paired 0.199 · TF-IDF grouped OOF (700 dev rows) 0.416.
- Paired route per-class recall (1,000 rows): original 1/300, textual 8/300, visual 22/100, mismatch 289/300 — the model collapses onto "mismatch".
- Binary accuracy 0.695 on paired = the all-Fake floor (predicts Fake for everything), not skill. Fake ROC-AUC ~0.517 ≈ chance.
- Wording experiment (105 rows): candidate paired 0.290 vs incumbent 0.259 (+0.030, 95% CI −0.072…+0.127) — FAILED the frozen improvement rule; incumbent wording retained.
- 300-row paired baseline completed (300/300, no errors/abstentions) as the frozen "before" for fine-tuning. Its macro-F1 sits in a dashboard graphic and was never recorded as a number.
- Frozen fine-tune protocol written (Oct 19): head-only, steps 245/490/735, tune-only selection, success = +0.03 macro-F1, bootstrap LB > 0, no recall drop > 5pp. **Never run.**
- Dataset limits logged: VERITE local 1,001 vs official 1,000 rows; 76 test items connected to validation; NewsCLIPpings images initially only 4 of 5,943 present.

## Phase 2 — Full-dataset baseline stages (Oct 25, Mac mini nightly run)
- Stage 1 NewsCLIPpings stream: 7,024 rows, 5,943/5,943 images, accuracy 0.5083. ✔ verified
- Stage 2 NCP metrics recomputed ✔
- Stage 3 VERITE vision+text: 1,001/1,001 usable, accuracy 0.3586 ✔ verified
- Stage 4 MMFakeBench image-only: 1,000/1,000, accuracy 0.2610 ✔ verified
- Stage 5 Tier-0 determinism: ABORTED — shell bug ('--set vision.batch_size=1' passed as one string). Stage 6 (gates + SUMMARY.json) never confirmed run.
- Fine-tuning was an explicit non-goal of that mission; a FINETUNE_HANDOFF_2026-10-25.md was written for a separate GPU phase — never run.

## What it all means
1. Zero-shot LAYA-Vision does not do this task: ranking is near chance (AUC ~0.52), and its apparent binary accuracy is a constant-prediction floor.
2. A plain TF-IDF baseline (0.416) beats every pretrained LAYA route — the pretrained model is the weakest thing measured, which is exactly why training is the contribution.
3. The failure is a collapse, not noise: one class (mismatch) absorbs almost all predictions. Training must be judged per-class, not by headline accuracy.
4. Small-n experiments can't resolve the target effect: 105 rows give SE ≈ 0.045 macro-F1 vs a +0.03 target — full splits are required, which is why the midterm run uses full datasets.
5. Nothing trained exists yet. Every number above is a baseline.

## Forward plan (decided 2026-11-22)
1. One repeatable notebook (built: LAYA_Full_Experiment_Midterm.ipynb) — config cell, pinned revision f2fe3c12, fixed seed; runs in Colab's interface on a RunPod GPU pod.
2. Baseline pass on full splits of all 3 datasets, native metrics (MMFakeBench 4-class macro-F1; NewsCLIPpings pairing accuracy; VERITE 3-class accuracy).
3. FULL fine-tune (encoder + vision tower + head; freeze dropped by Rafiul's decision 2026-11-22 — a new arm, not the Oct 19 protocol), grid over steps/LR/loss, winner on tune only, test scored once.
4. Trained checkpoint → Hugging Face Hub + Gradio Space (CPU inference is enough for the live demo).
5. Paper through PaperOrchestra (idea summary + experiment logs in), every number/citation verified against saved predictions before submission.
Blocked on: RunPod SSH access + Mac mini online to sync the workspace.
