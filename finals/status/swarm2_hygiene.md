# Protocol Hygiene Audit — LAYA Main Run (swarm2)

**Auditor:** swarm2 subagent (read-only) · **When:** 2026-11-22 ~19:06 ET, mid-run (grid + selection complete; supplementary 13/15; NCP carve in progress; test-once / calibration / publish stages not yet run — which is itself the expected state for Rules 1 and 3).
**Sources:** pod filesystem via `podssh.sh` (all paths under `/workspace/Misinformation`), `runs/packs.json`, training-record files, and `~/workspace/misinfo_run/mainrun_log.md`. Nothing was modified except this report.

---

## Rule 1 — TEST UNTOUCHED: **KEPT**

Evidence (pod, live):
- `runs/.test_scored` — **does not exist** (`ls: cannot access 'runs/.test_scored': No such file or directory`).
- `find data/processed/midterm -iname "*test*"` — **zero matches**. The midterm tree holds only the three baseline folders (mmfakebench val / newsclippings val / verite).
- `find runs -iname "*test*"` — **zero matches**. No winner test predictions exist anywhere in `runs/`.
- `data/reports/` contains exactly one file: `ablation_test_paired.predictions.jsonl` (22,146,070 bytes) — the October base-model ablation baseline, present as the expected bootstrap comparator. Per the rule's own terms this is **not** a violation; no *winner* test output exists beside it.

The test split has not been scored by any trained checkpoint at audit time.

## Rule 2 — METADATA BAN: **KEPT** (MMFakeBench) / **UNVERIFIABLE — no records yet** (NewsCLIPpings carve)

Evidence (pod, live):
- MMFakeBench training records `data/processed/protocol/mmfakebench_finetune_dev_choice_v2/train.jsonl`: all **980 rows** read; the union of keys across every row is exactly `{id, image, label, question, state_text}`. A case-insensitive scan for any key containing "source" returns **none** — no `text_source`, no `image_source`, no equivalent source-metadata field exists in the records, so none can reach the model inputs (context text + image + question).
- Auditor's transparency note (not a violation): the `image` value is a file locator path whose dataset folder names (e.g. `bbc_val_50`, `chatgpt_match_val_50`) reflect the benchmark's own on-disk layout. The path is used to load pixels; it is not a record field fed to the model as text, and the banned fields themselves are absent.
- NewsCLIPpings carve: **no record files exist yet** — `newsclippings_finetune_v1/` contains only the `images/` tree (the carve is still in its stream-save phase; records are written when the pass completes). The ban therefore cannot be checked on NCP records at audit time; re-check once the carve writes its `.jsonl` files.

## Rule 3 — SELECTION HYGIENE: **KEPT**

Evidence — `runs/packs.json` read in full (pod, live):
- **Temperatures are `null` in all three packs** (mmfakebench, newsclippings, verite) — calibration has not leaked ahead of its stage.
- Checkpoint pointers exactly as designed: mmfakebench → `"WINNER"`, newsclippings → `"NCP_WINNER"`, verite → `"models/laya-vision-base"` (eval-only transfer pack still pointed at the base checkpoint).
- `noul_threshold` = 0.5 in all three packs (the untuned default — no threshold fitting has occurred early either).

## Rule 4 — NCP CARVE PROVENANCE: **KEPT** (on log evidence; record-level check pending carve completion)

Evidence — `mainrun_log.md`, carve/metadata sections:
- The failure and fix are documented openly: carve cell errored 2026-11-22 18:06 ET (`metadata/train.json` missing — only val.json had ever been synced; the 352 MB train.json exceeds the 50 MB device-upload cap). Fix plan recorded *before* execution: rebuild train/test metadata from the VisualNews `origin/data.json` member of the same tar and **verify the build by reproducing `metadata/val.json` exactly from the same source**.
- "CARVE UNBLOCKED" section (~18:35 ET): `data.json` located as the tar's last member (header at byte 97,560,363,520; 356,272,348 bytes) and extracted pod-side; built `metadata/train.json` (**59,876 referenced ids**) + `test.json` (6,147) with the Mac path convention applied; **referenced-id coverage train 59,876/59,876, test 6,147/6,147, missing 0**; **captions verified identical to the Mac val.json entries**; and **verified through the run's own loader: `load_records` returns train 71,072 / val 7,024 / test 7,264 rows** — exactly the official Merged-Balanced split sizes and exactly the counts this audit was asked to look for. The evidence is present and internally consistent.
- Precision note: the log's verification wording is "captions verified identical to the Mac val.json entries" plus exact loader counts on all three splits — substantively the val-reproduction check that was planned, though not phrased as a byte-exact val.json diff. The log also discloses a provenance difference with no metric impact (Mac metadata files carry enriched fields — entities/title/timestamp — that no run code path reads).
- **Images saved so far: 272**, all under `images/bbc/…` (consistent with the tar's contiguous source-block layout — BBC is encountered first; the remaining sources land as the read proceeds). Because the carve's record files are not yet written (Rule 2 note), split-membership of the saved images currently rests on the verified metadata + the carve cell's train-only design; it becomes directly auditable when the carve writes its records.

## Rule 5 — SUPPLEMENTARY ISOLATION: **KEPT**

Evidence (pod, live):
- Canonical `runs/*/result.json` count = **exactly 12**, and the 12 are precisely the registered grid: `{full, lora} × {rlcd, soft_ce} × {245, 490, 735}` — no supplementary receipt has leaked into the canonical glob that the selection cells (21/33) assert on.
- Supplementary receipts live only under `runs/supplementary/*/result.json` — **13** present at audit time (of 15 planned; the tier is still executing). Isolation holds in both directions.

---

## Summary table

| # | Rule | Verdict |
|---|---|---|
| 1 | Test untouched | **KEPT** |
| 2 | Metadata ban | **KEPT** (MMF) · **UNVERIFIABLE yet** (NCP — no carve records written) |
| 3 | Selection hygiene (null temperatures, pack pointers) | **KEPT** |
| 4 | NCP carve provenance (official train split only) | **KEPT** on log evidence (loader counts 71,072 / 7,024 / 7,264; coverage complete; 272 images saved) |
| 5 | Supplementary isolation (canonical == 12) | **KEPT** |

No violations found. Two items are structurally not-yet-checkable rather than failed: the NCP carve's record-level metadata-ban and split-membership checks, both of which become auditable the moment the carve pass writes its record files.
