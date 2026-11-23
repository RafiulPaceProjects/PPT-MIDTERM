# Swarm-2 Audit — Notebook Consistency (2026-11-22, read-only)

**VERDICT: FINDINGS** — one documentation finding (Drive-sync evidence, §3). Every numeric consistency check passes exactly: notebook-printed grid scores, the printed winner, `runs/winner.json`, and the per-config `result.json` receipts all agree.

## 1. Pod executed notebook vs receipts

File: `/workspace/Misinformation/LAYA_MainRun_Executed.ipynb`
- **57 cells total, 28 code cells, 9 code cells with outputs** (run in progress — later cells not yet executed into the file).
- Cells with outputs: 8 SETUP · 10 PACKS · 12 DATA · 14 GATES · 16 BASELINES · 20 STREAM PASS 1 · 22 NCP DATA · 24 GRID (6,540 output blocks — full streamed training logs) · 26 SELECTION.
- Note: this is the landed/executed build; its cell indices (grid 24, selection 26) differ from the staged 57-cell source map (grid 19, selection 21). Values, not indices, are what agree — see below.

Grid cell (24) printed `[done]` lines, quoted verbatim:

```
[done] full_rlcd_245: tune macro-F1 = 0.5667 (134s, trainable params = 114,728,323)
[done] lora_rlcd_245: tune macro-F1 = 0.4597 (156s, trainable params = 12,603,715)
[done] full_soft_ce_245: tune macro-F1 = 0.5954 (132s, trainable params = 114,728,323)
[done] lora_soft_ce_245: tune macro-F1 = 0.6282 (157s, trainable params = 12,603,715)
[done] full_rlcd_490: tune macro-F1 = 0.5880 (254s, trainable params = 114,728,323)
[done] lora_rlcd_490: tune macro-F1 = 0.4505 (309s, trainable params = 12,603,715)
[done] full_soft_ce_490: tune macro-F1 = 0.6598 (254s, trainable params = 114,728,323)
[done] lora_soft_ce_490: tune macro-F1 = 0.5726 (302s, trainable params = 12,603,715)
[done] full_rlcd_735: tune macro-F1 = 0.6061 (385s, trainable params = 114,728,323)
[done] lora_rlcd_735: tune macro-F1 = 0.1946 (447s, trainable params = 12,603,715)
[done] full_soft_ce_735: tune macro-F1 = 0.7389 (395s, trainable params = 114,728,323)
[done] lora_soft_ce_735: tune macro-F1 = 0.7187 (516s, trainable params = 12,603,715)
```

Selection cell (26) printed winner line, quoted verbatim:

```
WINNER: {
 "arm": "full",
 "loss": "soft_ce",
 "steps": 735,
 "tune_macro_f1": 0.7389308060360692,
 "out_dir": "runs/full_soft_ce_735",
 "lora_available": true
}
Selection used ONLY the tune split (105 items, 4-class form). The test split has not been touched.
```

Receipt spot-checks (read directly from `runs/<config>/result.json` this audit):

| Config | Notebook print | Receipt `tune_macro_f1` | Match |
|---|---|---|---|
| full_soft_ce_735 (winner) | 0.7389 / 0.7389308060360692 | 0.7389308060360692 | exact |
| full_rlcd_245 | 0.5667 | 0.5666640335831 | rounds exactly |
| lora_soft_ce_735 | 0.7187 | 0.7187008469449485 | rounds exactly |
| lora_rlcd_735 | 0.1946 | 0.19461897706172515 | rounds exactly |

`runs/winner.json` read directly: arm full, loss soft_ce, steps 735, tune_macro_f1 0.7389308060360692 — identical to the selection cell's print and to the winner receipt; it is also the argmax of the 12 printed grid lines. **No discrepancies.**

Bonus consistency: the notebook's cell-22 output currently reads `carve: 2501 items over 2120 images (train 2001 / tune 250 / calib 250) — streaming to save the subset...` — the amendment-(c) carve sizes, produced by the resumed run (see §2).

## 2. Driver status files (`/root/driver_status_*.json`)

| Driver | State | Cells |
|---|---|---|
| A (pid 3517) | `queue_complete` | 6, 24, 26 done (ok) |
| B (pid 3909) | **`error_cell_22`** | 6, 10, 18, 20 done; **22 = error, ok=false** |
| B2 (pid 15349) | `kernel_ready` | 6, 10, 18 done (shadow replay); **22 = running** |
| C (pid 5915) | `queue_complete` | 5, 7, 9, 13, 15, 21, 24 done |
| C2 (pid 6576) | `kernel_ready` | 5, 7, 9, 13, 15, 21, 24 done; **30 = running** (§7d supplementary) |

- **The cell-22 error is still visible**: driver B's status file preserves it — cell 20 finished 18:06:07 ET, cell 22 errored 18:06:08 ET (epoch-verified), driver state `error_cell_22`. It is also narrated in `mainrun_log.md` (carve failed 18:06 ET, metadata/train.json missing). Nothing has overwritten B's record.
- **Resumed by driver B2**: shadow cells 6/10/18 done and cell 22 set running at 18:30:26 ET — the resumed kernel now executing the carve (its in-progress output is what the notebook's cell 22 currently shows; the notebook cell itself no longer displays the old error output, which survives in B's status file and the log).
- Two cells actively running at audit time: B2 cell 22 (carve stream-save) and C2 cell 30 (supplementary tier) — matching the log's account.

## 3. Drive sync state (from `mainrun_log.md`)

- Stated policy (recorded twice in the log): *"Drive syncs: after gates, and after each grid config completes ([done] lines in the grid cell's streamed output trigger a snapshot sync)"*; the notebook-only execution model section adds sync *"after each stage so Rafiul can watch outputs accumulate."*
- **Freshest sync I can evidence with a timestamp: 16:35:20 ET, after the GATES stage** — log MILESTONES section: *"Receipt: runs/gates.json. Drive synced 16:35:20 ET."* (Driver A's cell-6 finish epoch, 16:35:15 ET, corroborates the gates-stage timing.)
- **Finding (documentation, not data):** the log contains no per-sync timestamps or receipts for the claimed grid-config syncs (12 configs completed ~17:33 ET) or any later stage. The mechanism is described and the policy is stated, but the freshest *evidenced* sync remains the 16:35:20 ET gates sync. If the Drive "Research" file is presented as the live record, the run should log each snapshot sync with a timestamp (or a Drive file revision/modified-time read-back) at the next stage boundary to close this gap.

## 4. Staged source notebook (VM)

File: `~/workspace/misinfo_run/LAYA_Colab_Staged_For_Review.ipynb`
- **57 cells total, 28 code cells, 0 outputs, 0 non-null execution counts** — confirmed exactly as expected (clean staged source).

## Summary

Notebook ↔ receipts ↔ winner.json: fully consistent, exact at full precision on the winner and at printed precision on all spot-checks. Driver records preserve the 18:06 cell-22 carve error (driver B) and its resumption (driver B2, cell 22 running since 18:30 ET), with C2 running the supplementary cell 30. Staged source notebook verified clean (57 cells, zero outputs). Sole finding: Drive-sync cadence is claimed by policy in the log but only one sync (gates, 16:35:20 ET) is evidenced with a timestamp.
