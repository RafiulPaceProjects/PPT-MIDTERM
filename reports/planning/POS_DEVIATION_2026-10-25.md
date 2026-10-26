# POS deviation note — combined track

**Date:** 2026-10-25
**Against:** `POS_final.pdf`, submitted 2026-09-28 (Saravani, Etikela, Haider), Objective 5 and Objective 6.
**Author of this note:** Rafiul Haider (combined track).
**Status:** draft for team and instructor review. Not yet signed.

## 1. What the POS committed to

Fine-tuned detection: a captioning pipeline, two fine-tuned Laya variants (Attention, Gate),
six comparison conditions, a text-only Laya baseline, a CLIP image–text embedding classifier,
evaluation on NewsCLIPpings, VERITE and MMFakeBench, accuracy and macro-F1 with paired 95%
CIs across three seeds, targets of 84.8% (NewsCLIPpings) and 76.3% (VERITE), and a Streamlit
application.

## 2. What has been delivered

| Commitment | Delivered | Evidence |
|---|---|---|
| Pretrained evaluation harness, three datasets | Yes, dataset-native routes | `data/workflows/baseline_study/` |
| MMFakeBench evaluation | Yes — official test, 10,000 rows, paired + text-only | `dataset_native_baseline_20261025_test_ablation_v1/` |
| VERITE evaluation | Yes — 1,001 rows, accuracy 35.66% | `dataset_native_baseline_verite_local_images_v1/verite_local_1001_paired/` |
| NewsCLIPpings evaluation | Yes — 7,024 rows, streamed from VisualNews, accuracy 50.83% | `data/processed/ncp_stream_v1/`, `ncp_metrics_2026-10-25.json` |
| Text-only comparison | Yes, same checkpoint (`vision_text`) | same ablation directory |
| Accuracy, macro-F1, intervals | Yes, hash-clustered bootstrap | `mmfakebench_test_ablation_2026-10-25.json` |
| Calibration | Yes, ECE + Brier + reliability bins | same file |
| Fine-tuned Attention / Gate variants | **No** | not started; training is outside the current working policy |
| Captioning pipeline | **No** — substituted by an image-only route | the checkpoint emits typed decisions, not text |
| CLIP embedding classifier | **No** | needs a model download; not authorized |
| Six conditions | **Four** of six | paired, vision_text, image, text-endpoint |
| Three seeds | **Not applicable** — one frozen checkpoint has no seed variance; intervals are cluster-bootstrap | methodology note |
| Streamlit application | **No** | not started |
| 84.8% / 76.3% targets | **Not met** — 35.66% (VERITE), 26.42% (MMFakeBench) | same artifacts |

## 3. Why the scope changed

1. **The working policy forbids training.** The project's own agent/scope rules state that
   fine-tuning is outside the active scope, and the fine-tuning gates require explicit
   approval plus a compute decision. That approval has not been given.
2. **Compute.** The available environment is CPU-only. Fine-tuning two variants across three
   seeds on this machine is not feasible in the remaining time; the original training used a
   GPU.
3. **Data.** Visual class has 49 training examples (147/147/**49**/147). Teaching a visual
   distortion class from 49 images is not a credible claim, regardless of compute.
4. **A finding displaced the plan.** On the official test split, a metadata-only rule reaches
   91.5% while the model reaches 26.4%, and adding the image *lowers* accuracy by 1.5 points
   (95% CI [−0.0244, −0.0054]). Fine-tuning on this split would most likely learn the
   shortcut and produce a higher number with less meaning.

## 4. What is proposed instead

- Report a **verified zero-shot baseline** with a text-only control, cluster-aware intervals,
  calibration, and an explicit description of the benchmark's metadata shortcut.
- Keep **NewsCLIPpings** as the one dataset where the shortcut cannot exist (balanced 50/50 by
  construction) — it is the decisive capability test, and it is now evaluated at chance
  (50.83%, 95% range [49.78, 51.81]).
- Defer fine-tuning to a documented, separately approved phase with GPU access.
- Deliver the Streamlit view over saved predictions if the timeline allows; it needs no model.

## 5. What this note is not

It is not a claim that the POS was wrong. It is a record that the plan changed, why, and what
the evidence now supports. The performance targets are not met and are reported as unmet.

## 6. Decision requested

Instructor acknowledgement of one of:
- **A.** Accept the baseline-and-diagnostic rescope for this submission.
- **B.** Require the fine-tuning phase; this needs GPU access and a revised deadline.
- **C.** Accept a hybrid: baseline now, fine-tuning gate reviewed after the midterm.

Team signature: ______________  Instructor: ______________  Date: __________
