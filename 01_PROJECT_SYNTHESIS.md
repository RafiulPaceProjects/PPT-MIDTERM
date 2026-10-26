# How the pretrained baseline fits the POS

**Scope:** combined track (Objective 5) of the CS 668 project "Multimodal Misinformation Detector: Text and Image Fake-News Classification" (POS dated 09-28-2026). Results as of 2026-10-25.

## 1. The question this midterm answers

The POS asks how well a fine-tuned Laya model detects out-of-context, misleading image-text pairs, compared with a text-only version of the same model and a direct image-text embedding classifier. Any fine-tuned result needs a reference point. The midterm builds that reference: what the pretrained LAYA-Vision checkpoint does before any task training, and how much signal its frozen representation already carries.

That gives the midterm two layers:

1. **Zero-shot baseline.** The frozen checkpoint answers each benchmark's own question with no training, prompt tuning or threshold tuning.
2. **Frozen-feature probe.** A linear classifier is trained on the checkpoint's frozen features, following the published train-on-NewsCLIPpings, test-on-target protocol. The checkpoint's weights stay fixed. The probe measures how much a trained head could recover before any fine-tuning.

Fine-tuning itself (Objective 5's Attention and Gate variants) is the next stage and is not part of this midterm.

## 2. The ontological backbone

The POS describes three channels of misinformation, and each maps to one track. The three datasets of the combined track label those same channels in different ways. That shared set of concepts is how the three tracks connect.

| Concept | What goes wrong | POS track | MMFakeBench label | VERITE label | NewsCLIPpings label |
|---|---|---|---|---|---|
| Textual distortion | the claim in the text is false | Text track (Obj. 1 and 2) | textual veracity distortion | miscaptioned (bridge, see below) | none |
| Visual distortion | the image is manipulated or generated | Image track (Obj. 3 and 4) | visual veracity distortion | none | none |
| Cross-modal inconsistency | a real image and a real caption are paired out of context | Combined track (Obj. 5) | mismatch | out-of-context | falsified |
| Consistent pair | nothing is wrong | all tracks | original | true | pristine |

Three things follow from this table.

- MMFakeBench is the only dataset that labels all three concepts. That makes it the place where the three tracks can be compared on one population, and it is why the baseline reports MMFakeBench per class.
- Cross-modal inconsistency is the concept all three combined-track datasets share. That is why NewsCLIPpings (the POS's core comparison) and VERITE true-vs-out-of-context are the right targets for the transfer probe.
- VERITE "miscaptioned" mapping to textual distortion is a bridge, not a fact from VERITE's documentation. In VERITE, a real image keeps its true context and the caption is rewritten into a false claim, so the falsity enters through the text. Treat it as an interpretation.

The project ontology (`data/ontology/mmfakebench-ontology.md`) adds integrity rules. The baseline follows each one:

| Ontology rule | How the baseline applies it |
|---|---|
| A mismatch signal is not the same as a false claim or deceptive intent | Results are reported as agreement with dataset labels, never as detecting deception |
| Binary and four-way results, validation and test results, and different sample sizes are not directly comparable | Each table names its task, split and n; VERITE three-class (35.7%) is kept apart from VERITE true-vs-OOC (54.9% probe) |
| Source and image-path metadata are audit variables, not model inputs | The model never sees source names or paths; the 91.5% source-name rule is reported as an audit, never as a model |
| Reported, calculated, inferred and proposed claims stay distinct | Published numbers are labelled non-comparable; bridges and proposals are marked as such |

## 3. Experiment map

| # | Experiment | POS element it serves | Concept | Status | Key result (n) | Main artifact |
|---|---|---|---|---|---|---|
| E1 | Zero-shot, image + text, three datasets | Obj. 5 reference point for fine-tuned Laya | all | done | MMFakeBench macro-F1 20.4% (9,999, post-hoc test); VERITE accuracy 35.7% (1,001); NewsCLIPpings accuracy 50.8% (7,024 validation) | `BASELINE_CLAIMS_2026-10-25.md` |
| E2 | Same checkpoint, text only | Obj. 5 "text-only Laya baseline" | all | done (MMFakeBench, VERITE) | MMFakeBench 27.9% accuracy (10,000); VERITE 35.9% (1,001) | same |
| E3 | Image only, 1,000-row sample | Modality ablation (extension) | all | done | 26.1% accuracy (1,000-row sample) | same |
| E4 | Source-metadata audit | POS problem statement: do detectors learn content or superficial patterns? | audit | done | a rule that reads only source names reaches 91.5% on MMFakeBench test (9,999) | `mmfakebench_test_ablation_2026-10-25.json` |
| E5 | Image effect by source pair | POS question: does combining modalities help? | cross-modal | done | pooled −1.51 pp (9,999 rows); per source pair −18.0 to +18.4 pp (14 pairs) | `MMFAKEBENCH_SOURCE_PAIR_EFFECT_2026-10-25.md` |
| E6 | Frozen-feature linear probe, NewsCLIPpings train to targets | Obj. 5 "direct image-text embedding classifier" (with LAYA's own embeddings) and the held-out test requirement | cross-modal | done | NewsCLIPpings test 57.4% vs zero-shot 51.1% (7,264, held out); VERITE true-vs-OOC 54.9% vs 50.5% (663) | `transfer_probe/FULL_REPORT_ncp_transfer_probe_v1_2026-10-25.md` |
| E7 | Published-number verification | Obj. 5 stretch targets | none | done | 84.8% and 76.3% are binary true-vs-OOC results from LAMAR (arXiv:2504.06010v3, Table 3) | `dashboard/published_supplement.json` |
| E8 | Calibration (ECE, Brier) | Calibration as in Obj. 2, carried into the combined track | none | done | text-only better calibrated than image + text on MMFakeBench (ECE 1.2% vs 8.2%) | `BASELINE_CLAIMS_2026-10-25.md` |

Not done, and not claimed: the captioning pipeline, the fine-tuned Attention and Gate variants, the six comparison conditions, three training seeds, a CLIP embedding classifier, and the Objective 6 verdict application. The two dashboards present results; they are not the Objective 6 app.

## 4. Why this counts as a pretrained baseline

- **Frozen model.** One checkpoint (`f2fe3c12…`), weights never updated, one fixed question bank. No prompt selection and no threshold tuning.
- **Same rows across arms.** Paired and text-only arms are scored on identical rows, so their difference isolates the image.
- **Floors beside every score.** Constant-majority guessing, chance, and the source-metadata rule sit next to the model, so no number is read alone.
- **Uncertainty that respects duplicates.** 95% bootstrap ranges resample whole image clusters (exact bytes), 2,000 resamples, seed 20261018.
- **Held-out evidence where possible.** The NewsCLIPpings test split was read once, after the probe protocol was frozen. MMFakeBench test numbers are labelled post-hoc because that split had been inspected earlier.
- **Audit trail.** 22 of 22 pipeline gates, 28 of 28 audited numbers, identical outputs across batch sizes, and an integrity gate that reproduced the saved zero-shot run exactly before the probe was trained.

The probe belongs in a pretrained baseline because it changes nothing in the model. Linear probing is the standard way to measure what a frozen representation encodes. Here it shows that LAYA's features carry some pairing signal (+6.24 pp on held-out NewsCLIPpings test, 95% range 4.76 to 7.70) that its zero-shot answer does not use. That headroom is what the fine-tuning stage has to build on.

## 5. Where the project and the POS disagree, with proposed resolutions

| Issue | What the POS says | What the work shows | Proposed resolution |
|---|---|---|---|
| Model identity | "fine-tune two Laya variants (Attention and Gate)" | Attention and Gate are LAMAR integration methods (LAMAR [E2E, Attention] and [E2E, Gate]); LAYA has no such variants | Implement Attention and Gate as fusion heads over frozen LAYA features, a direct extension of the linear probe, and name them that way |
| VERITE stretch target | 76.3% on VERITE | 76.3% is binary true-vs-OOC. The baseline's VERITE headline (35.7%) is three-class. LAMAR's own three-class figure is 54.9% | Compare 76.3% only with the true-vs-OOC probe result (54.9%); keep the three-class result separate |
| NewsCLIPpings stretch target | 84.8% held-out test | Same native task as the probe; probe 57.4% on the held-out test | Report it as not met, as the POS asks |
| Held-out test | "held-out test accuracy" | NewsCLIPpings test held out; MMFakeBench test post-hoc; VERITE has no training split and serves as an external test | Keep the labels; only NewsCLIPpings test counts as held out |
| Confidence intervals | "paired 95% confidence intervals across three training seeds" | Paired cluster-bootstrap ranges on identical rows; the probe is deterministic, so seeds do not vary it | Keep the paired ranges; add three seeds when a stochastic head is trained |
| Six comparison conditions | named but not listed | none | Proposal for the team: (1) zero-shot image + text, (2) zero-shot text only, (3) frozen-feature linear probe, (4) Attention head, (5) Gate head, (6) CLIP embedding classifier. Conditions 1 to 3 are done |
| Cross-dataset overlap | "audit for identifier/hash overlap across datasets" | MMFakeBench test contains 1,500 mismatch rows whose source is NewsCLIPpings. The probe was never scored on MMFakeBench, so its numbers are unaffected | Any model trained on NewsCLIPpings and evaluated on MMFakeBench must first audit image-hash overlap |
| Compute | free Colab GPU | local Apple GPU (MPS); CPU too slow for the probe pipeline | Record the change; the frozen-feature pipeline fits a laptop |
| Captioning pipeline | required for Obj. 5 | not built | Open item for the fine-tuning stage |
| Image access | "confirm dataset access early" | NewsCLIPpings images streamed from the VisualNews archive, never stored; reuse terms unresolved | Keep the disclosure; no redistribution |

## 6. How the findings answer the POS problem statement

The POS asks whether detectors learn factual inaccuracy or superficial patterns, and whether combining text and image helps.

- **Superficial patterns.** On MMFakeBench, source names alone predict 91.5% of test labels. Any model's aggregate MMFakeBench score has to be read against that audit before it says anything about content.
- **Does the image help?** Zero-shot, mostly no. On MMFakeBench the pooled effect is −1.51 pp and splits into −18.0 to +18.4 pp by source pair. On VERITE it is −0.20 pp with a range spanning zero. On NewsCLIPpings the zero-shot model calls nearly every pair falsified.
- **Is the information there at all?** Yes, weakly. The probe on frozen features recovers +6.24 pp on held-out NewsCLIPpings test. It transfers to VERITE true-vs-OOC only partly (+4.37 pp, range −1.36 to 9.95, spanning zero).

## 7. What this sets up for the final submission

1. Train Attention and Gate fusion heads over frozen LAYA features on NewsCLIPpings train, select on validation, score NewsCLIPpings test and VERITE true-vs-OOC once: the same pipeline as the probe.
2. Add the CLIP embedding classifier (condition 6) on the same rows.
3. Run three seeds for any stochastic head and keep the paired cluster bootstrap.
4. Audit image-hash overlap before any MMFakeBench evaluation of a NewsCLIPpings-trained model.
5. State the stretch targets plainly: currently not met (57.4% vs 84.8% on NewsCLIPpings test; 54.9% vs 76.3% on VERITE true-vs-OOC).
