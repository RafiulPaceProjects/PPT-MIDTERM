# VERITE image-root discrepancy (resolved for the text-only comparison)

**Found:** 2026-10-25, while assembling the cross-dataset claims table.
**Severity:** blocks any VERITE comparison across runs. Does not invalidate the MMFakeBench or NewsCLIPpings results.

## What happened

Two VERITE paired runs exist, and they read **different image files for the same 1,001 rows**:

| Run | Manifest | Image root | Accuracy |
|---|---|---|---|
| `c4749c27…` (cited by the site, dashboard and closeout) | `dataset_native_baseline_verite_local_images_v1/verite_local_1001_paired` | `data/raw/VERITE/images/` | 0.3566 |
| `90742b57…` (protocol v2 directory) | `dataset_native_baseline_20261021_v2/verite_local_all1001_paired` | configured root | 0.3478 |
| `e9c2bd51…` (new text-only control, this session) | `dataset_native_baseline_20261026_baseline_v1/verite_vision_text` | `/Users/rafiulhaider/Documents/windmill/data/verite/VERITE/images/` | 0.3586 |

Measured comparison between `c4749c` and `e9c2bd51`:

- same length (1,001 rows) — yes
- same gold sequence — **yes**
- same text sequence — **yes**
- same image sequence — **no: 986 of 1,001 image SHA-256 values differ**

Example row 0: `true_0.jpg` at `data/raw/VERITE/images/` hashes `6d06c9c8…`; the same filename under the windmill root hashes `3723f499…`.

## Why it matters

The image bytes are the model's input. Different bytes mean the two numbers measure different stimuli. Therefore:

1. The site's 35.66% and the protocol-v2 34.78% are not two estimates of one quantity; they are two different datasets that share row identities.
2. The new text-only control (0.3586) cannot be compared with the site's paired number (0.3566) until the roots are reconciled.
3. Any "the image adds/does not add X" claim on VERITE is unsupported until one root is declared canonical and both arms are rerun on it.

## What is not affected

- MMFakeBench: one image root, verified, unchanged.
- NewsCLIPpings: images come from the streamed VisualNews archive, not from either VERITE root.

## Required resolution

1. Identify both collections: file counts, byte sizes, provenance (which came from the official archive, which from a mirror or re-encode).
2. Declare one canonical root in `study.json`, with a hash manifest.
3. Rerun both VERITE arms (paired and vision_text) on the canonical root, new output directory.
4. Retire the non-canonical number from the site and dashboard, or label it as a distinct population.

## Update, 2026-10-25 (reviewed against the harness)

The text-only comparison is **not** blocked. `engine.py::model_state` builds the `vision_text` input as `{'context': text}` only; the image path is attached for the `paired` branch alone. The image root recorded in a text-only manifest therefore never enters the model.

Empirical check: a rerun of the text-only arm against the canonical `data/raw/VERITE/images` root reproduced identical `input_state_sha256`, labels, and probabilities on all 202 rows it completed before being stopped for time (maximum probability delta 0.0; saved under `verite_vision_text_canonical_partial_20261025/`).

What remains open is narrower: which image root the **paired** VERITE numbers should cite. The current site number (0.3566, run `c4749c27…`) uses the verified official archive staged at `data/raw/VERITE/images` (664 files; 663/663 referenced basenames; decode inventory 1,001/1,001). The older paired run at the windmill root (0.3478, run `90742b57…`) is historical. Recommendation: add an explicit canonical-root setting to `study.json` (defense in depth, for future runs) and keep the historical run labelled, not merged.


## Resolution (2026-10-25)

1. **Roots identified.** The canonical root is the verified official archive staged at `data/raw/VERITE/images` (664 files, 663/663 referenced basenames present, decode inventory 1,001/1,001; SHA-256 `e9e3c723…` for the source ZIP). The windmill root is the earlier copy (495 files; historical inventory 716 decodable, 8 decode errors, 277 missing).
2. **Canonical root declared.** `study_verite_local_images_v1.json` points at `data/raw/VERITE`; the current paired run `c4749c27…` (accuracy 0.3566) uses it. The older paired run `90742b57…` (0.3478) is historical and is not used in the claims table, report, or dashboard.
3. **Text-only arm is image-independent.** `engine.py::model_state` returns only `{'context': text}` for the `vision_text` branch; no image enters the model. An empirical check reran the text-only arm against the canonical root: the first 202 completed rows produced identical `input_state_sha256`, labels and probabilities (maximum delta 0.0). The rerun was stopped as unnecessary and preserved at `verite_vision_text_canonical_partial_20261025/`.
4. **No paired rerun is required.** The paired arm already uses the verified canonical root; the text-only arm consumes no images; rows, text and gold align 1,001/1,001. The paired-versus-text comparison is valid.
5. **Remaining action.** Keep the 34.78% windmill-root number labelled historical; do not publish it as a second estimate of the same quantity.
