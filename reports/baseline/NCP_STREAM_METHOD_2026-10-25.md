# NewsCLIPpings streaming evaluation — method declaration (pre-registered)

**Declared:** 2026-10-25, before the run.
**Scope:** pretrained inference only. No training, no fine-tuning, no image storage.

## Question

Can the pinned LAYA-Vision checkpoint judge whether an image belongs with its caption,
on a benchmark where the label cannot be inferred from source metadata?

## Population

- NewsCLIPpings `merged_balanced` validation split: 7,024 annotations, 5,943 unique
  VisualNews images, balanced 50/50 by construction (each caption appears once pristine
  and once falsified).
- Only validation rows. No test rows are read, so the split cannot be selected on.
- Images are streamed from the official VisualNews archive
  (`https://www.cs.rice.edu/~vo9/visualnews/origin.tar`, 97,916,641,280 bytes) using
  parallel HTTP range requests. Each member is decoded, scored, and dropped. Nothing is
  written except predictions and a manifest (measured: 8 kB for two rows).

## Inputs to the model

Per row: the caption text and the image pixels. No ids, no paths, no source fields, no
label. The image filename is never tokenized; the path is used only to open bytes.

## Question set (fixed before running)

| Key | Type | Question |
|---|---|---|
| `native` | choice | Does the image actually belong with the caption as originally published? (`pristine` / `falsified`) |
| `out_of_context` | noul | Is this image used out of context, taken from a different news event than the caption describes? |
| `wrong_image` | noul | Was this caption originally written about a different photograph? |

Primary metric: accuracy of `native`, with balanced accuracy (equal to accuracy at a
50/50 design). Secondary: AUC of both noul questions against the falsified label, macro-F1,
ECE and Brier on `native`, and a per-strategy breakdown by the annotation's
`source_dataset` field (four generation strategies).

## Identity

- Checkpoint: `f2fe3c12cb6d04c59d8a190250bf3fb40fc828dc`, local snapshot.
- Inference settings: fp32, CPU, batch 1 per row, `n_permutations=1`, shipped temperatures,
  no fitted calibration, `strict=true`.
- Library identity is recorded by the loader; per-row latency is stored with each prediction.

## Claim boundary

- Zero-shot, descriptive. No training, no threshold selection, no prompt tuning on these rows.
- The comparison target is the paper's own baselines (CLIP 65%, VisualBERT ~70%) and the
  reported trained systems (CCN 84.7%, SNIFFER 88.4%, LAMAR 84.8%) — none of which is a
  201M typed-decision model evaluated zero-shot. Any comparison must say so.
- VisualNews image terms are unresolved. Using the images locally for evaluation is the
  research norm; redistribution is not claimed.
- The result is a capability probe of one checkpoint, not a statement about multimodal
  misinformation detection in general.

## Verification gates (all must pass before any number is quoted)

1. Coverage: extracted images / 5,943; missing list reported, not hidden.
2. Decode: zero decode failures, or each failure named with its path.
3. Schema: every record has row_id, gold, both noul probabilities, and a choice whose
   probabilities sum to 1.
4. Balance: gold counts are 3,512 pristine / 3,512 falsified; any deviation is reported.
5. Recompute: accuracy and macro-F1 recomputed from the predictions file, not read from prose.
6. Storage: output directory measured; it must contain no images.

## Artifacts

- `data/processed/ncp_stream_v1/predictions.jsonl`
- `data/processed/ncp_stream_v1/manifest.jsonl` (one line per image: path, status, rows, bytes)
