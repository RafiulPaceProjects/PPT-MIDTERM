# Pod phase runbook (resume session) — execute in order, verify each step

Preconditions: probe repair REPAIR-DONE in repair_chain2.log;
assembled_probe_repaired.jsonl built + hashed. VERITE/StageB repairs
may still be running on the VM — pod work proceeds in parallel.

## 0. Frozen P0 comparator (VM)
python3 -c: write frozen_p0.jsonl from probe_items.jsonl
  ({"id", "predicted_label": pair_only_pred_trained}).

## 1. Deploy + access
python3 pod2.py deploy   # note id, runtime ip + publicPort for 22/tcp
# regenerate wrappers from podssh2.sh pattern with the new ip/port:
#   podssh3.sh / podscp3.sh (ProxyCommand connect_proxy.py <ip> <port>)
./podssh3.sh 'nvidia-smi'   # verify

## 2. Push code + inputs FIRST (so the scan can start during setup)
Push to /workspace/v2probe/:
  judge_pilot.py judge_final.py judge_verite.py calib_stageb.py
  train_stageb.py fast_scan.py collect_media.py
  laya_trainer.py + visualnews_stream.py  (from ~/workspace/misinfo_run/)
  scan_dest_map_v2.json
  inputs/: probe_items.jsonl stageb_carve.json + pod_pull/val_metadata.json
  assembled_probe_repaired.jsonl (+ .sha256 of it)
  stageb_items.jsonl assembled_stageb.jsonl stageb_train.jsonl stageb_tune.jsonl
  verite_test_items.jsonl assembled_verite.jsonl
  verite/images/* (from verite_push/images) -> /workspace/v2probe/verite/images/

## 3. Image scan (background, ~1 hr) + setup (foreground, parallel)
for i in 0 1 2 3 4 5: v2env-independent — fast_scan needs only stdlib:
  python3 fast_scan.py --shard $i --shards 6 --wanted scan_dest_map_v2.json
  (run AFTER step 4 creates python? No — system python3 suffices.)
./podssh3.sh 'bash /workspace/v2probe/setup_pod.sh'  # setup_pod.sh pushed too
  -> v2env, models laya-vision-base + ncp-winner, laya-src

## 4. Pilot judging (needs /dev/shm/pilot/*.png from the scan + setup)
/workspace/v2env/bin/python judge_pilot.py \
  --checkpoint /workspace/v2probe/models/ncp-winner \
  --items /workspace/v2probe/inputs/probe_items.jsonl \
  --assembled /workspace/v2probe/assembled_probe_repaired.jsonl \
  --images-dir /dev/shm/pilot --out /workspace/v2probe/preds_pilot30.jsonl \
  --tag stageA_pilot
Pull preds; score on VM: score_stagea.py --preds preds_pilot30.jsonl
  --assembled assembled_probe_repaired.jsonl --items probe_items.jsonl
  --frozen-p0 frozen_p0.jsonl --out pilot_results.json
  (score_pilot.py is the same file as score_stagea.py; pilot n=30 ->
  NO success verdict, registered.)

## 5. Stage B training (needs carve_images from scan + setup)
mkdir /workspace/v2probe/stageb; place stageb_train.jsonl/stageb_tune.jsonl there
cd /workspace/v2probe/stageb && /workspace/v2env/bin/python \
  /workspace/v2probe/train_stageb.py \
  --base /workspace/v2probe/models/laya-vision-base \
  --train-file stageb_train.jsonl --tune-file stageb_tune.jsonl \
  --out-dir /workspace/v2probe/runs/stageb_245 --steps 245
# smoke first: verify image paths resolve (../carve_images) with the
# receipt's n_train_records == 1000 (500 items x2 forms) before trusting.
# START background pull of runs/stageb_245/model.safetensors right after.

## 6. Calib judging + fit (AM6B.2)
/workspace/v2env/bin/python calib_stageb.py \
  --checkpoint /workspace/v2probe/runs/stageb_245 \
  --out /workspace/v2probe/preds_calib_stageb.jsonl
fit on VM: python3 fit_calib.py --calib-preds preds_calib_stageb.jsonl
  -> stageb_calib_fit.json (frozen BEFORE probe eval is scored)

## 7. Dual-checkpoint final traversal (Stage A + Stage B, one pass)
/workspace/v2env/bin/python judge_final.py \
  --ckpt-a /workspace/v2probe/models/ncp-winner --out-a /workspace/v2probe/preds_stageA_300.jsonl --tag-a stageA_300 \
  --ckpt-b /workspace/v2probe/runs/stageb_245 --out-b /workspace/v2probe/preds_stageB_300.jsonl --tag-b stageB_300 \
  --items /workspace/v2probe/inputs/probe_items.jsonl \
  --assembled /workspace/v2probe/assembled_probe_repaired.jsonl \
  --assembled-sha256 <sha256>
Pull both; score on VM:
  score_stagea.py --preds preds_stageA_300.jsonl ... --out stagea_results.json
  score_stageb.py --preds preds_stageB_300.jsonl --calib-fit stageb_calib_fit.json
    --stagea-preds preds_stageA_300.jsonl ... --out stageb_results.json
  score_noul.py --stagea preds_stageA_300.jsonl --stageb preds_stageB_300.jsonl
    --calib-fit stageb_calib_fit.json --out noul_report.json

## 8. VERITE EVIDENCE arm (needs assembled_verite.jsonl)
/workspace/v2env/bin/python judge_verite.py \
  --checkpoint /workspace/v2probe/models/laya-vision-base \
  --items /workspace/v2probe/verite_test_items.jsonl \
  --images-dir /workspace/v2probe/verite/images \
  --assembled /workspace/v2probe/assembled_verite.jsonl \
  --out /workspace/v2probe/preds_evidence.jsonl --tag verite_evidence
Pull -> verite_out/preds_evidence.jsonl; re-run score_verite.py on VM.

## 9. Pull everything + terminate welded
Pull: all preds_*.jsonl, runs/stageb_245/result.json (+ model.safetensors
if the background pull finished), all pod logs.
python3 ~/workspace/runpod/pod.py terminate <new pod id>; whoami verify
spend rate 0 + record balance.
