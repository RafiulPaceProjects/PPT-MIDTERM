# PRD: W1 retrain (recovery for the loss-masking audit)

Slug: w1-retrain. Registered 2026-11-27. Status: BOARD-PASSED
2026-11-27, with the board's fixes applied (see Board pass).
This is a short recovery PRD. It exists because the
loss-masking-audit PRD's step 0 gate FAILED on 2026-11-24
(STEP0_GATE_REPORT.md in swarm_tests/loss-masking-audit/): the
W1-trained checkpoint (train_S, MMFakeBench Phase 3) is absent
from every store the study can reach, and the audit's controls
leg may not run without it. The gate report names the recovery:
retrain W1 on the recorded recipe, or re-register the audit
without the MMFakeBench leg. The owner chose the retrain route
by approving this setup on 2026-11-27. Runtime: Colab free GPU.

## The exact recipe (copied from the record, never re-derived)

From the original run's result.json
(v2_probe/runs/noul_drilldown/mmf/train_S/result.json), its
vlm_agent_config.json, and the driver that produced it
(v2_probe/train_mmf.py, which this run executes unmodified):

- Base: the laya-vision-base checkpoint the original run loaded
  (its config records backbone HuggingFaceTB/SmolVLM-256M-Instruct,
  head_layers 2, n_act 2, max_len 1024, head_max_len 256,
  option_attention block, dtype fp32, image_size 512, readout
  terminator).
- Driver: train_mmf.py, unmodified. It replicates
  laya_trainer.train_full_finetune with the class4 tune-form
  selection the original run used.
- Arm: full. Loss: soft_ce. Vision tower frozen.
- Steps: 245. Seed: 0. Batch: 8 (the module default the driver
  passes). lr_encoder 1e-5, lr_head 1e-3.
- Train file: mmf_train_base.jsonl (980 records, as the original:
  n_train_records 980). Tune file: mmf_tune_base.jsonl (class4
  tune read, 105 class4 items in the original).
- Original run's fingerprints, for the identity checks below:
  trainable parameters 114,728,323; loss_first 1.7355; loss_last
  0.0966; tune macro-F1 (class4) 0.6533; tune accuracy 0.6571.

## Protocol, in order

0. Base identity gate, fail-closed (board fix 1). The base
   checkpoint travels in the Colab inputs bundle as the
   laya-vision-base directory the original run used, with its
   vlm_agent_config.json. Before training: the config must match
   the recorded values above, and after set_trainable the
   trainable parameter count must equal 114,728,323 exactly, and
   the train file must hold exactly 980 records. Any mismatch
   stops the run. No substitute base (including the public
   thaitea/laya-vision repo) may be used under this PRD; a
   different base is a new registration, because the audit's
   frozen read was taken on a checkpoint trained from this base.
1. Timing smoke. A 30-step timing run (the study's pricing
   pattern) projects the 245-step wall time. If the projection
   exceeds 30 minutes, the run stops and reports rather than
   training uncheckpointed: the notebook's checkpoint rule is a
   verified save at least every 30 minutes of wall time, and
   train_mmf.py is a single monolithic call. Expected duration
   from the record's step rates is minutes, so this gate should
   never fire; it exists so the checkpoint rule has no silent
   exception.
2. Train. train_mmf.py runs once, exactly as recorded, writing
   its result.json beside the checkpoint.
3. Verify and pull. The finished checkpoint is verified where it
   sits, then copied to Drive (persistent storage) and verified
   again there: safetensors header completeness (file size
   covers 8 + header + data end; expected 804,696,880 bytes and
   416 tensors, the size of every sibling checkpoint), and a
   clean load through laya.load_vlm. Verify-on-save: size and
   sha256 read back and compared after the copy; a failed verify
   retries the copy and never reports success silently. This is
   the Amendment 14 truncation lesson, the failure this whole
   recovery exists because of: the original W1 weights died
   unverified on a terminated pod.
4. Tune smoke read. The driver's own class4 tune metrics are
   reported beside the original fingerprints. Registered band:
   tune macro-F1 within 0.05 of 0.6533 is a pass. Outside the
   band, the checkpoint is still delivered, but it is labelled
   SUSPECT in the results JSON and the audit does not proceed on
   it until the board reviews the deviation. The band is a smoke
   check on a different GPU's arithmetic, never a confirmation
   of anything (board fix 2).

## Success criterion (the whole PRD)

A complete, verified W1-trained checkpoint, trained on the exact
recorded recipe, sitting in persistent storage (Drive, and back
on the study VM after the session), passing step 3's header and
load checks and step 4's smoke band. On success, the
loss-masking-audit's step 0 gate is re-run against the new
checkpoint; if the gate passes, the audit's step 1 may proceed
under its own PRD. This PRD delivers a checkpoint and nothing
else: no audit number, no claim.

## Split and the closed set

Training reads the MMFakeBench development-side records the
original run trained on (mmf_train_base.jsonl) and the tune file
for its smoke read. HARD RULE: the MMFakeBench test set is
closed. It was scored exactly once. Nothing in this PRD touches
it, and the retrain does not change that status in any way.

## Budget and stop rule

$0. Colab free GPU (owner approval 2026-11-27). 245 steps at
batch 8 over 980 records is about two epochs; minutes of GPU.
Stop rules: any step-0 mismatch, a step-1 projection over 30
minutes, or a step-3 verify that fails twice. In every stop, what
exists is reported as it stands; a partial checkpoint is never
labelled complete.

## Board pass

BOARD-PASSED 2026-11-27, with fixes. Four critics argued against
the draft: novelty, methods, statistics, feasibility. Novelty
recorded no claim to argue with: this is a recovery, not a
result, and the PRD says so. The sharpest objection came from
the methods critic: the original base lived at a pod path
(/workspace/v2probe/models/laya-vision-base) and its public
identity was never recorded, so a retrain from a look-alike base
would produce a checkpoint the audit could not honestly use,
while looking exactly like success. The fixes they won, applied
above:

1. The base identity gate (protocol step 0): config match,
   exact trainable parameter count, exact record count, and a
   ban on substitute bases under this PRD.
2. The tune band is a smoke check with a SUSPECT label, not a
   verdict; a retrained checkpoint is a new checkpoint, and the
   audit re-gates on it under its own PRD rather than inheriting
   the lost checkpoint's status.
3. The 30-minute checkpoint rule is given teeth for a monolithic
   training call: the timing smoke gate (protocol step 1), so
   the rule is enforced by stopping, not waived by convenience.
4. Verify-on-save is specified at both writes (local and Drive),
   with size and hash read back, because an unverified copy is
   the original failure repeating itself.

Concession recorded: GPU arithmetic differs across hardware, so
the retrained checkpoint will not be bit-identical to the lost
one even on the exact recipe. The study's position, recorded in
the gate report, is that the recipe is the recovery; this PRD
adds the fingerprints and the smoke band so "the recipe" is
checked, not trusted.

## What would change the paper's claims, and what changes nothing

Nothing in the paper changes either way. Success unblocks the
loss-masking audit, whose own PRD states what its outcomes would
change. Failure leaves the audit's MMFakeBench leg blocked, and
the remaining recovery is the gate report's other branch:
re-register the audit without that leg.
