# Similarity audit: blocked at step 0, offline

Run date: 2026-11-24. Status: BLOCKED. No part of the audit ran.
Cost $0. Cumulative swarm spend stays $0 of the $3.00 cap.

## What step 0 verified before the stop

- Snapshot hashes: assembled_probe_repaired.jsonl matches the
  canonical manifest exactly (sha256 f8bc0fadaea7559d9…f7705).
  probe_items.jsonl is byte-identical across its two stored copies
  (sha256 9174b6e679453650…3a416). assembled_verite.jsonl sha256
  db078d90c1517778…1c4b1, recorded in similarity_audit.py's log
  design. VERITE held-out images are local
  (v2_probe/verite_push/images, 663 files) and present.
- Per-item model screen scores for the headline comparison exist
  locally (preds_stageA_300.jsonl, P0 fake_probability; the stored
  read reproduces the record's 0.5911 comparator source,
  noul_report.json).

## Blocker 1: the registered encoder cannot be loaded offline

The PRD names one encoder, openai/clip-vit-base-patch32, no
alternates. Its local Hugging Face cache
(~/.cache/huggingface/hub/models--openai--clip-vit-base-patch32)
holds only config.json in the snapshot. The single weights blob is
suffixed .incomplete at 425,918,775 bytes: the download was
interrupted before it finished, and no processor or tokenizer
files are in the snapshot at all. The encoder therefore cannot be
loaded from local files. Completing the download is a network
call, and all network calls are stopped on the owner's order
(2026-11-24, after repeated approval cards). PRD step 0: if the
registered encoder is not available, the run stops and the PRD
returns to the board. This report is that stop.

## Blocker 2: the NewsCLIPpings probe images are not stored locally

By the study's own discipline, evaluation images are streamed from
the VisualNews origin.tar (https://www.cs.rice.edu/~vo9/visualnews/
origin.tar) and never stored. The 300 probe images exist nowhere
on this machine; the only local NewsCLIPpings images are 35 screen
PNGs in v2_probe/mmf_images, which are not the probe items.
Fetching the probe images is a network call, stopped on the same
order. This blocker stands even if blocker 1 clears: the headline
leg needs both the encoder and a stream pass.

## What unblocks it

One owner-approved network window that allows (a) the Hugging
Face download of openai/clip-vit-base-patch32 to finish, and
(b) one streamed pass over the VisualNews origin.tar. Everything
else the audit needs is already local and verified above. The
audit script is written and saved beside this report
(similarity_audit.py); it runs unchanged once those two calls are
allowed. The VERITE leg needs only the encoder; it can run first
in the same window.
