# Loss masking audit: step 0 inventory gate report

Run date: 2026-11-24 (owner approval same day). PRD step 0 is a
fail-closed gate. Result: GATE FAILED. The controls leg does not
run, the audit leg is not delivered alone, and this PRD returns to
the board for re-registration of its criteria, exactly as the PRD
directs.

## Inventory, per checkpoint

Header completeness check: file size against the safetensors
header's data end (byte count must cover 8 + header + data end).

- Scale probe (Amendment 15), v2_probe/uplift/pulled_uplift/runs/
  scale10k_4900/model.safetensors: PRESENT, header complete
  (804,696,880 bytes, 416 tensors).
- Stage B, v2_probe/pulled/stageb_245_model.safetensors: PRESENT,
  header complete (804,696,880 bytes, 416 tensors).
- Arm W, v2_probe/pulled/wiki_stageb_245_model.safetensors:
  PRESENT, header complete (804,696,880 bytes, 416 tensors).
- VERITE adapted, v2_probe/uplift/pulled_uplift/verite/
  adapted_245r/model.safetensors: PRESENT, header complete
  (804,696,880 bytes, 416 tensors).
- Stage A winner (the v1 NewsCLIPpings winner): not on local disk;
  confirmed through its recorded route, the Hugging Face repo
  RafiulHaiderbro/laya-vision-fullft-newsclippings. Downloaded
  2026-11-24 into this run's folder and header-checked: COMPLETE
  (804,696,880 bytes, 416 tensors, sha256 prefix 9009d385f2fbc37f).
- W1-trained (MMFakeBench Phase 3, train_S: single wording W1,
  trained from the base checkpoint, full arm, soft_ce, vision
  frozen, 245 steps): ABSENT. Its run directories, both the working
  copy (v2_probe/runs/noul_drilldown/mmf/train_S) and the pulled
  copy (v2_probe/pulled_pod/runs/noul_drilldown/mmf/train_S), hold
  only vlm_agent_config.json, processor files, backbone config,
  and result.json (3.5 MB total). No model.safetensors, no
  pytorch_model.bin, no other weight file exists anywhere under
  ~/workspace/misinfo_run. The Hugging Face account holds exactly
  two model repos, the two v1 winners; there is no repo for the
  W1-trained checkpoint. The weights existed only on the
  terminated drilldown pod and were never pulled.

## The exact blocker

The controls leg needs the W1-trained checkpoint for the
MMFakeBench gray-image descriptive read at its frozen form
(temperature 2.462, threshold 0.65). That checkpoint is absent and
unrecoverable from any store this run can reach. PRD step 0: if a
required checkpoint is absent, the controls leg does not run and
the PRD returns to the board for re-registration of its criteria;
it does not silently deliver the audit leg alone.

## Cost

$0 spent. Cumulative swarm spend stays $0 of the $3.00 cap. No pod
was started. The Stage A winner download is a free Hugging Face
pull and is kept in this folder for the re-registered run.
