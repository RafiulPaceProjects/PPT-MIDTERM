# Swarm-2 Independent Receipt Audit — LAYA Main Run
Audited: 2026-11-22 ~19:06 ET, read-only, directly from the pod's receipt files (`runs/*/result.json`, `runs/supplementary/*/result.json`, `runs/winner.json`). Independent of the run's summaries and of the earlier receipt deep check.

## VERDICT: CLEAN — no integrity defects
Four observations named below (one signed-zero loss value, one field-name schema difference in LoRA receipts, the known non-learning loss traces, and 2 of 15 supplementary receipts not yet written at audit time). Nothing missing, nothing inconsistent within a family, winner verified.

## 1. Grid — canonical runs/ (exactly 12 receipts ✓)
Common to all 12: seed **20261122**, base **thaitea/laya-vision** @ revision **f2fe3c12cb6d04c59d8a190250bf3fb40fc828dc**, n_train_records **980**, tune_metric_form **class4**, per-step loss count == steps, **0 NaN/Inf** in every loss array, all recalls in [0,1]. Trainable params constant per arm: full = **114,728,323** (×6), lora = **12,603,715** (×6, all r16).

| config | tune F1 | tune acc | steps | loss first → last | recalls orig/text/vis/mismatch |
|---|---|---|---|---|---|
| full_rlcd_245 | 0.5667 | 0.5619 | 245 | 1.0259 → 1.4507 | .281/.906/.600/.484 |
| full_rlcd_490 | 0.5880 | 0.6000 | 490 | 1.0259 → 0.0079 | .500/.906/.600/.387 |
| full_rlcd_735 | 0.6061 | 0.6190 | 735 | 1.0259 → 0.0000 | .375/.938/.700/.516 |
| full_soft_ce_245 | 0.5954 | 0.6000 | 245 | 0.6355 → 0.3509 | .375/.906/.700/.484 |
| full_soft_ce_490 | 0.6598 | 0.6667 | 490 | 0.6355 → 0.0004 | .594/.906/.800/.452 |
| **full_soft_ce_735** | **0.7389** | 0.7429 | 735 | 0.6355 → 0.00004 | .656/.969/.700/.613 |
| lora_rlcd_245 | 0.4597 | 0.5905 | 245 | 1.1059 → 1.2085 | .281/.969/.000/.710 |
| lora_rlcd_490 | 0.4505 | 0.6095 | 490 | 1.1059 → 0.8332 | .875/.969/.000/.161 |
| lora_rlcd_735 | 0.1946 | 0.3333 | 735 | 1.1059 → 1.1352 | 1.000/.062/.100/.000 |
| lora_soft_ce_245 | 0.6282 | 0.6571 | 245 | 0.7618 → 0.5416 | .375/.969/.400/.710 |
| lora_soft_ce_490 | 0.5726 | 0.5810 | 490 | 0.7618 → 0.1720 | .312/.875/.500/.581 |
| lora_soft_ce_735 | 0.7187 | 0.7048 | 735 | 0.7618 → 0.2776 | .531/.875/.600/.742 |

## 2. Supplementary — runs/supplementary/ (13 receipts present of 15 planned)
Isolation holds: the canonical glob contains exactly the 12 grid configs; no supplementary receipt leaked into it, and no grid receipt sits in supplementary/. All 13 present receipts: seed 20261122 (except the seed check, by design), same base/revision, n_train 980, form class4, loss count == steps, 0 NaN/Inf.

| config | tune F1 | trainable | lr_encoder | loss first → last | recalls orig/text/vis/mismatch |
|---|---|---|---|---|---|
| full_lr2e-5_soft_ce_490 | 0.6871 | 114,728,323 | 2e-05 | 0.6355 → 0.000005 | .406/.906/.800/.677 |
| full_lr2e-5_soft_ce_735 | 0.7178 | 114,728,323 | 2e-05 | 0.6355 → **−0.0** | .562/.906/.700/.645 |
| full_lr5e-6_soft_ce_490 | 0.6217 | 114,728,323 | 5e-06 | 0.6355 → 0.1971 | .625/.844/.700/.419 |
| full_lr5e-6_soft_ce_735 | 0.6438 | 114,728,323 | 5e-06 | 0.6355 → 0.0121 | .562/.906/.800/.387 |
| head_rlcd_490 | 0.2590 | 8,462,659 | 1e-05* | 1.0259 → 1.0848 | 1.000/.188/.100/.032 |
| head_rlcd_735 | 0.4899 | 8,462,659 | 1e-05* | 1.0259 → 0.5351 | .625/.531/.400/.323 |
| head_soft_ce_490 | 0.4238 | 8,462,659 | 1e-05* | 0.6355 → 0.6583 | .281/.719/.100/.613 |
| head_soft_ce_735 | 0.3098 | 8,462,659 | 1e-05* | 0.6355 → 1.0202 | .281/.812/.100/.161 |
| lora_r8_soft_ce_490 | 0.7037 | 10,533,187 | (lr_lora 0.001) | 0.7618 → 0.0022 | .500/.906/.700/.677 |
| lora_r8_soft_ce_735 | 0.6362 | 10,533,187 | (lr_lora 0.001) | 0.7618 → 0.0040 | .469/.844/.500/.613 |
| lora_r32_soft_ce_490 | 0.1168 | 16,744,771 | (lr_lora 0.001) | 0.7618 → 1.0362 | 1.000/.000/.000/.000 |
| lora_r32_soft_ce_735 | 0.2244 | 16,744,771 | (lr_lora 0.001) | 0.7618 → 1.0700 | .750/.125/.100/.097 |
| seedcheck_full_soft_ce_735_seed20261123 | 0.7320 | 114,728,323 | 1e-05 | 1.4221 → 0.0015 | .656/.938/.800/.548 |

\* head receipts record the configured lr_encoder value although the encoder is frozen in that arm; trainable count (8,462,659, constant ×4) is the operative field.
**Not yet written at audit time:** `data_245` and `data_122` (directories exist, no result.json) — the tier stood at 13/15 receipts; a completeness state, not an inconsistency.

## 3. winner.json — independently recomputed
- My argmax over the 12 grid receipts: **full_soft_ce_735, tune_macro_f1 = 0.7389308060360692**.
- winner.json contents: `{"arm": "full", "loss": "soft_ce", "steps": 735, "tune_macro_f1": 0.7389308060360692, "out_dir": "runs/full_soft_ce_735", "lora_available": true}`.
- **MATCH — exact, to full float precision.** Runner-up lora_soft_ce_735 = 0.7187 (margin 0.0202).

## 4. Seed check
`seedcheck_full_soft_ce_735_seed20261123`: seed **20261123**, tune F1 **0.731970782691318**, trainable 114,728,323, 735 losses, 0 bad, recalls .656/.938/.800/.548.
**Delta vs winner = −0.00696** (0.7320 vs 0.7389). Its loss_first (1.4221) differs from the winner's (0.6355), as expected under a different seed (different batch order/soft-target draw); loss_last 0.0015 is sane.

## 5. Observations (named, with values — none is an integrity defect)
1. **Signed zero:** full_lr2e-5_soft_ce_735 records loss_last = **−0.0** (also the last element of its losses array). Finite, not NaN/Inf; a floating-point signed zero at a fully-converged endpoint. Cosmetic only.
2. **LoRA field naming:** all 10 LoRA receipts (6 grid + r8 ×2 + r32 ×2) record **lr_encoder = null** and instead carry `lr_lora` (= 0.001) plus `lora_r`/`lora_alpha`/`lora_dropout`/`lora_targets` keys, which full/head receipts lack. The learning rate is present under its correct name; the null is a schema difference, consistent across the whole LoRA family — but any consumer reading `lr_encoder` uniformly will see a null and should be pointed at `lr_lora`.
3. **Loss-increase traces are confined to the known non-learning configs** and agree with their F1s: full_rlcd_245 (1.026→1.451), lora_rlcd_245 (1.106→1.209), lora_rlcd_735 (1.106→1.135), head_rlcd_490 (1.026→1.085), head_soft_ce_490 (0.635→0.658), head_soft_ce_735 (0.635→1.020), lora_r32_490 (0.762→1.036), lora_r32_735 (0.762→1.070). Conversely the strong soft_ce runs end at ≈0 (full_soft_ce_490 → 0.0004, full_rlcd_735 → exactly 0.0), the memorization-range endpoints already noted in the run's narrative. No receipt shows a loss pattern inconsistent with its score.
4. **Family fingerprints are exact:** full 114,728,323 in all 11 full-arm receipts (grid 6 + LR variants 4 + seed check 1); head 8,462,659 ×4; LoRA trainable monotone in rank (r8 10,533,187 < r16 12,603,715 < r32 16,744,771), constant within each rank.
