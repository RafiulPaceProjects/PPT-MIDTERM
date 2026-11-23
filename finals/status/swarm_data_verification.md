# Swarm Verification — DATA COMPLETENESS (independent, read-only)

**Verified:** 2026-11-22, ~16:26–16:29 ET, directly on the run pod (`/workspace/Misinformation`) via SSH. Nothing was changed or deleted. This is an independent check — counts below were observed live, not copied from the run log.

## 1. Finetune protocol records — ✅ VERIFIED
Path: `data/processed/protocol/mmfakebench_finetune_dev_choice_v2/`

| File | Lines | Expected | Four-way class4 form | Binary (Fake) form |
|---|---|---|---|---|
| train.jsonl | 980 | 980 | 490 | 490 |
| tune.jsonl | 210 | 210 | 105 | 105 |
| calib.jsonl | 210 | 210 | 105 | 105 |

Every file carries **both question forms** in an exact 50/50 split (four-way choice + binary choice). Total 1,400 records = 700 items × 2 forms. `manifest.csv` and `metadata.json` present.

## 2. MMFakeBench val — ✅ VERIFIED
- Annotations (`MMFakeBench_val.json`): **1,000 rows**.
- Image files in `MMFakeBench_val/` tree: **1,000**.
- Annotation `image_path` values are split-root-relative (e.g. `/real/bbc_val_50/BBC_val_0.png`). Joining each against the split root resolves **1,000 / 1,000** — every referenced image exists on the pod. (A naive join against other bases resolves 0 — the paths are only valid relative to the split root; basename match against the tree is also 1,000/1,000.)

## 3. MMFakeBench test — ⚠️ PARTIAL (transfer not complete; not growing during observation)
- Annotations (`MMFakeBench_test.json`): **10,000 rows** ✅.
- Image files in `MMFakeBench_test/` tree: **934** at epoch 1795382743 and **934** again 69 s later (epoch 1795382812).
- **The tree was NOT growing during the observation window** (identical counts 60+ s apart). 934 of the 10,000 annotation basenames are present; **9,066 images still missing**. A tar transfer was seen in flight on the VM side earlier, so this may be a between-batches pause — but at observation time the count was flat. This is the same gap the notebook's DATA cell failed on. Test-once cannot run until the tree completes.

## 4. VERITE — ✅ VERIFIED
- `data/raw/VERITE/VERITE.csv`: **1,001 data rows** (matches the local 1,001-row copy).
- `data/raw/VERITE/images/`: **663 image files**. Matches the expected ~1,001 rows / 663 files exactly.

## 5. NewsCLIPpings — ❌ GAP: train.json and test.json MISSING on the pod
Path: `data/raw/NewsCLIPpings/data/merged_balanced/`

| File | Status | Rows observed | Expected |
|---|---|---|---|
| train.json | **MISSING** | — | ~71,072 |
| val.json | present (0.8 MB) | **7,024** annotations ✅ | 7,024 |
| test.json | **MISSING** | — | ~7,264 |

val.json structure confirmed: top-level dict with an `annotations` list of 7,024 records. **The NewsCLIPpings training-arm carve (amendment (c)) reads train.json — it cannot run until train.json is synced to the pod.** test.json's absence does not block anything in the current design (NCP test is untouched by design), but it is not on the pod if ever needed.

## 6. Disk — ✅ VERIFIED, no shortfall risk
- Pod disk: 50 G total, **9.0 G used, 42 G available** (18%).
- `data/` = 1.6 G (will grow as the remaining ~9,066 test images land — est. +1–2 G), `models/` = 771 M (base checkpoint).
- Projection: 12 grid checkpoints × 0.4–0.8 GB = 4.8–9.6 GB; + winner copy + calibrated copy ≈ 1.6 GB; + NCP arm (2 budget runs + winner) ≈ 2.4 GB. **Worst-case additional load ≈ 14–17 GB → projected peak ≈ 25 GB of 50 GB.** Fits with ~25 GB headroom. No shortfall risk even if every checkpoint lands at the top of the size band.

## Gap list (for the coordinator)
1. **NCP train.json missing on pod** — blocks the amendment-(c) NewsCLIPpings training-arm carve. (test.json also missing; not blocking by design.)
2. **MMFakeBench test images 934 / 10,000, flat across two counts 69 s apart** — transfer incomplete and not visibly progressing during observation; 9,066 images outstanding. Blocks test-once (and currently fails the DATA cell).
3. Everything else verified exactly: protocol 980/210/210 both-forms, MMF val 1,000/1,000 fully resolvable, VERITE 1,001/663, NCP val 7,024, disk ample.
