# LAYA Colab Inputs Bundle: Manifest

Built 2026-11-27 on the study VM from the study's own files, after Rafiul
Haider confirmed in chat that his own study files should be processed.
Drive target: LAYA_Colab/inputs/ on the insurance@securesafer.com account
(Drive folder id 13nWFrYESQL2ZFpgC-PmtFGliSc_VTEFH).
Staging copy: ~/workspace/misinfo_run/swarm_tests/colab/staging/inputs/
Full per-file data (every file, size, sha256, Drive id):
manifest_data.json beside this file in the working folder.
Cost: $0.

## Status summary

- Uploaded to Drive and verified by size read-back: every staged file
  except the five listed under "Staged, not uploaded".
- Independent folder-by-folder Drive sweep after the upload (36 folders):
  exactly one discrepancy, the locked PNG named below.
- The notebook Setup 3 gate will still fail until the four checkpoint
  weight files and the remaining probe and tune images are on Drive.
  See "What blocks the gate" at the end.

## Code files (inputs/code/)

All five copied byte-exact from the study folders and uploaded.

| file | bytes | sha256 | source | status |
| --- | --- | --- | --- | --- |
| judge_pilot.py | 10,270 | e4a4d15f3a5160859439c363028b16ddd509e50eec65f114c4e5ac6f64de3d78 | misinfo_run/v2_probe/judge_pilot.py | uploaded, verified |
| audit_scorer.py | 8,198 | 9d0116b96a86a69693712f4a86366c4afeb7581a651c410fe87c6b363e93f75a | misinfo_run/v2_probe/audit_scorer.py | uploaded, verified |
| train_mmf.py | 2,270 | ddef60d47766451450a9e68ee4ae3c8556dd1dbc108661b5dee850564102d185 | misinfo_run/v2_probe/train_mmf.py | uploaded, verified |
| visualnews_stream.py | 15,355 | d311b2c743d83de91f689e8eb248c407b6cc0cdd3cebff055a41786f224196b0 | misinfo_run/visualnews_stream.py (identical to finals/code/ copy) | uploaded earlier by the browser task, hash verified |
| laya_trainer.py | 32,087 | 953cd6cbbf8b2dd581e230fe2f19d67860037ad7caca109f5162235009c70c86 | misinfo_run/laya_trainer.py (identical to finals/code/ copy) | uploaded earlier by the browser task, hash verified |

## Data files (inputs/)

Copied byte-exact from misinfo_run/v2_probe/ unless marked "built".

| file | lines | sha256 | source | status |
| --- | --- | --- | --- | --- |
| probe_items.jsonl | 300 | 9174b6e67945365038565903bfdee2a8857a8013ac41299b9de30dd2c8a3a416 | v2_probe/probe_items.jsonl | uploaded, verified |
| preds_stageA_300.jsonl | 1,500 | 9551933d206f0656812c4e2c82052f27cdf5b9730498f691cb5c7bbaf48c8caa | v2_probe/preds_stageA_300.jsonl | uploaded, verified |
| preds_scale_probe_300.jsonl | 300 | 9a775cac5b8dc9295a81017700775be2c50add260561f54acc355f84a2c23d64 | v2_probe/uplift/preds_scale_probe_300.jsonl (byte-identical to the pulled_uplift copy) | uploaded, verified |
| mmf_train_base.jsonl | 980 | 450518e6c1387fbd220752f53c9ceb912db5c5b9c5f49fc3a6f2cb35c3c2bd91 | v2_probe/mmf_train_base.jsonl | uploaded, verified |
| mmf_tune_base.jsonl | 210 | 202b39800fccbd1d6ab82cd5bc7055a53a046675d790fc8a8da3306be01d89a9 | v2_probe/mmf_tune_base.jsonl | uploaded, verified |
| scale_tune_items.jsonl | 204 | 9cab621609c358eff7b5d9d4d672e4f003601c1a351be04ea1e0206173074a88 | built, see below | uploaded, verified |
| scale_tune_records.jsonl | 408 | c9fd2dd412b47f90fd1a8ca26ccbeb2cc858c6091b143acc326925192e2b81c2 | built, see below | uploaded, verified |
| probe_records.jsonl | 600 | c9fb3f8e7c24b2506f4bd50eff6db147376ffe4ba9a4322bea02d35b41c658a3 | built, see below | uploaded, verified |
| dest_map.json | 466 members | b14868abae480e3b62b5f945302685723b8ea424acade2cdf13c259e22ca4d9f | built by the assembly (member to destination map for the image extraction) | uploaded, verified |

The MMFakeBench test split was never opened, read, or touched. Only the
train and tune base files above were copied.

## The three files that did not exist under the notebook's names

scale_tune_items.jsonl, scale_tune_records.jsonl, and probe_records.jsonl
were not present anywhere in the study folders. They were built from
study material by build_bundle_files.py (beside this manifest in the
working folder), and verified field by field:

- Question texts (V1_NATIVE and the binary question) were imported from
  the study's own v2_probe/uplift/build_scale_records.py, never retyped.
- Record schema mirrors laya_trainer.validate_records: id, image,
  state_text, question{type, instructions, criteria}, label inside the
  criteria range. Label 0 is pristine, 1 is falsified, matching the
  study's gold labels.
- scale_tune_items.jsonl: the Amendment 15 carve's tune split, read from
  v2_probe/uplift/scale_carve.json, in the study's own tune-item format
  {id, caption, gold, image} with the flat scale_images file name.
- scale_tune_records.jsonl: two trainer records per tune item (native
  and binary form), image paths under scale_tune_images/.
- probe_records.jsonl: two trainer records per probe item (native and
  binary form), image paths under probe_images/ using each item's
  image_path from probe_items.jsonl.
- Verification run: every record carries the required fields, labels in
  range, ids match the item files exactly, captions match the items,
  image paths match the items, labels agree with gold on every record.

Count flag, stated plainly: the PRD and the notebook speak of 200 tune
items and notebook cell 17 asserts exactly 200 tune pass-1 rows. The
carve as the study built it holds 204 tune items (100 pristine and 100
falsified target, filled with group slack 4; the build receipt at
v2_probe/uplift/pulled_uplift/uplift_out/build_receipt.json confirms
tune 204). All 204 were staged. Choosing a 200 subset would invent a
selection rule, so the difference is flagged here, not silently fixed.
Resolving it is a registration decision.

## Checkpoints (inputs/ckpts/)

Each folder holds model.safetensors plus vlm_agent_config.json,
backbone/config.json, and processor/ files (chat_template.jinja,
processor_config.json, tokenizer.json, tokenizer_config.json), in the
layout the notebook expects. Every staged weights file passes the
notebook's own header check (header complete, 416 tensors).

| folder | weights bytes | weights sha256 | mapping evidence | status |
| --- | --- | --- | --- | --- |
| scale_probe | 804,696,880 | 7f2566dcff5d02f0766e54ea3c9ba8e19e3e9bf87c3e6e295700e34c8e8c130f | STEP0_GATE_REPORT.md: v2_probe/uplift/pulled_uplift/runs/scale10k_4900/ is the complete folder, copied whole, result.json kept | companion files uploaded, verified; weights staged, not uploaded |
| stageb | 804,696,880 | a598f41d1a1254b6db3bd68657b48c35905d4dc78c3a15b78d4690a11ff1aa13 | identical hash across v2_probe/uplift/ckpts/stageb_245/, the gate report's pulled/stageb_245_model.safetensors, and push_staging/ckpts/stageb_245/ | companion files uploaded, verified; weights staged, not uploaded |
| stagea_winner | 804,696,880 | 9009d385f2fbc37f5309b71367be57aff008435fb381dcd66e64de88cce0146c | matches the recorded sha256 prefix 9009d385f2fbc37f and the HF repo RafiulHaiderbro/laya-vision-fullft-newsclippings X-Linked-ETag exactly; local copy from swarm_tests/loss-masking-audit/ckpt_stagea_winner/; companion files downloaded from the same repo at sha 4656b88849b9573c54d3325b58a042fb712d574a | companion files uploaded, verified; weights staged, not uploaded |
| laya-vision-base | 804,696,880 | 31220803f38b44b8b1649b207c632612c9a35dee0da2ef1ea35d21e4b424be68 | provenance below | companion files uploaded, verified; weights staged, not uploaded |

Base provenance, stated plainly: mainrun_log.md (Stage 1, 2026-11-22)
records "Base checkpoint snapshot (thaitea/laya-vision @ f2fe3c1)
downloaded to models/laya-vision-base (771 MB)"; drivers/run_one_config.py
sets CKPT = models/laya-vision-base; the main-run manifests record the
checkpoint path /workspace/Misinformation/models/laya-vision-base. So
the original base is the public HF repo thaitea/laya-vision at revision
f2fe3c12cb6d04c59d8a190250bf3fb40fc828dc. That exact revision was
downloaded (parallel range download, assembled in order) and its
sha256 matches the repo's X-Linked-ETag for the file. Its
vlm_agent_config.json matches every value the notebook's Run 3 identity
gate checks (backbone HuggingFaceTB/SmolVLM-256M-Instruct, head_layers
2, n_act 2, max_len 1024, head_max_len 256, option_attention block,
image_size 512, readout terminator). One tension to keep visible: the
W1 retrain PRD says no substitute base, naming the public
thaitea/laya-vision repo, may be used. Read against the provenance,
that line bans look-alike bases and other revisions; the recorded
original is this repo at this revision. The parent agent and Rafiul
should confirm that reading before Run 3 relies on it.

## MMF image trees (inputs/mmf_train_images/, inputs/mmf_images/)

Copied whole from v2_probe/mmf_train_images (490 files, 316,387,598
bytes) and v2_probe/mmf_images (210 files, 134,070,431 bytes). Run 3
resolves record images relative to the records folder, so these trees
sit at inputs/ level, as the notebook's train_mmf.py expects.
Hash roll-up (sha256 over the sorted per-file path, size, and hash
lines): mmf_train_images 245444d5bd298cf17454f2cc8fd7f4c7904a6224619e20d94d2320e99cc32754;
mmf_images 0386eca2fd4b98f06590c045137a6d0d8fb646e88243725ef8e6e7361b2dad05.
Uploaded and verified, except one file: mmf_train_images/fever_val_AI_40.png
(1,750,586 bytes) is staged, not uploaded. Its first upload attempt hung
in the connector and the connector still reports an equivalent write
already running for that exact file two hours later; three retries met
the same lock. It is one of 490 train images and does not block Runs 1
or 2.

## Probe and tune images (inputs/probe_images/, inputs/scale_tune_images/)

Status: PARTIAL. 15 of 504 destination files extracted and uploaded.

- The destination map (dest_map.json, uploaded) covers 466 unique tar
  members and 504 destination files (some images serve two items).
  Probe destinations: staging probe_images/ path per probe_items.jsonl
  image_path. Tune destinations: scale_tune_images/ flat names.
- Extraction used the study's own fast_scan.py from
  v2_probe/uplift/push_staging/, run as 8 shards against
  https://www.cs.rice.edu/~vo9/visualnews/origin.tar (97,916,641,280
  bytes).
- Extracted before the scan was stopped: 15 files (8 probe, 7 tune).
  All 15 verified: each is in the destination map and each fully
  decodes as an image under visualnews_stream.verify_image_bytes
  (complete PIL decode).
- Why it stopped: this VM's network path to the Rice host measures
  about 57 to 90 KB/s per connection (one 16 MiB range fetch took 295
  seconds; a single 32 MiB fetch took 403 seconds), and the shards
  advanced about 0.3 GB each in 9 minutes. Walking the 98 GB archive
  from here would take days. The remaining 489 files were not
  extracted.
- Practical route: run the same extraction inside Colab, where the
  network is fast, writing straight into Drive LAYA_Colab/inputs/.
  dest_map.json is already on Drive for that run. That needs a browser
  task, which this assembly could not do.

## Staged, not uploaded (complete list)

1. ckpts/scale_probe/model.safetensors, 804,696,880 bytes,
   sha256 7f2566dcff5d02f0766e54ea3c9ba8e19e3e9bf87c3e6e295700e34c8e8c130f.
2. ckpts/stageb/model.safetensors, 804,696,880 bytes,
   sha256 a598f41d1a1254b6db3bd68657b48c35905d4dc78c3a15b78d4690a11ff1aa13.
3. ckpts/stagea_winner/model.safetensors, 804,696,880 bytes,
   sha256 9009d385f2fbc37f5309b71367be57aff008435fb381dcd66e64de88cce0146c.
4. ckpts/laya-vision-base/model.safetensors, 804,696,880 bytes,
   sha256 31220803f38b44b8b1649b207c632612c9a35dee0da2ef1ea35d21e4b424be68.
   Reason for all four: at this VM's measured upload throughput the
   connector upload of one 800 MB file ran over 25 minutes without
   completing, and the one attempt wedged the connector write lock on
   another file for hours. Four files at that rate are impractical in
   this session. Note stagea_winner and laya-vision-base already exist
   on Hugging Face (the repos named above), so Colab can pull those two
   directly at datacenter speed; scale_probe and stageb exist only in
   the study folders and in staging.
5. mmf_train_images/fever_val_AI_40.png, 1,750,586 bytes, connector
   write lock, see the MMF section.
6. The 489 not-yet-extracted probe and tune images, see the images
   section.

## What blocks the gate

Notebook Setup 3 checks, against Drive: the five code files (present),
the eight data files (present), the four checkpoint folders with
weights (weights missing), and probe_images/ with at least 300 files
(8 present). Unblocking needs: the four weights on Drive (two of them
are on Hugging Face already), and the image extraction finished
(dest_map.json is on Drive; the Colab-side run is the fast route).
