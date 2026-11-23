# Swarm-2 Audit — Budget + Operations (2026-11-22 ~19:06 ET)

**VERDICT: WITHIN BUDGET** — current balance covers the full remaining-work projection with ~$2.1–2.5 to spare; projected total run spend $7.24–7.69 stays under the $8 hard stop (margin $0.31–0.76 if every stage runs long; the standing descope order — supplementary first, then the NCP arm — is the relief valve, and PASS 2 is the swing item).

## 1. Balance, spend, effective rate

| Point | Balance | Source |
|---|---|---|
| Deploy / run start (~15:33 ET) | $9.7725 | mainrun_log.md line 91 |
| ~16:26 ET | $9.0525 | log (parent record) |
| ~18:26 ET | $7.4071 | mainrun_log.md line 510 (log's own spend figure: $2.37) |
| **Now, ~19:06 ET** | **$6.5852** | **RunPod API `myself.clientBalance`, read live this audit** |

- **Spend so far: $9.7725 − $6.5852 = $3.1873.**
- Pod elapsed: rented 20:33:07 UTC = 15:33 ET (API `lastStatusChange`); API `uptimeInSeconds` 12,776 = **3.55 hr**, matching wall-clock to this audit (00:06 UTC).
- **Effective rate: $3.1873 / 3.549 hr = $0.898/hr** — matches the console total of **$0.90/hr** ($0.89 compute + $0.007 storage, user's own pod-details screenshot) within billing granularity. The API's `currentSpendPerHr` reads 0.897 (compute-side figure).
- Segment check (honesty note): 16:26→18:26 implies $0.82/hr and 18:26→19:06 implies $1.23/hr — the balance updates in discrete billing chunks, so single segments oscillate; the full-window fit ($0.898/hr over 3.55 hr) is the reliable figure and it agrees with the console rate.
- Log consistency: the log's 18:26 spend claim ($2.37) vs computed $9.7725 − $7.4071 = $2.3654 ✓.

## 2. Uptime + disk

- Pod uptime 3.55 hr from the 15:33 ET start (API runtime figure; the host OS `uptime` of 5 days is the physical host, not the pod).
- **Disk now: 50 GB container, 35 GB used (69%), 16 GB free** (`df` on the pod, live).
- User's telemetry screenshot (17:54 ET): 26 GB used (53%). **Growth of +9 GB in ~70 min** — accounted for by supplementary checkpoints landing (each full checkpoint ≈ 800 MB) plus the NCP carve images accumulating. 16 GB free is ample for what remains (PASS 2 writes predictions, not images; publish reads). No disk risk; the earlier ~25 GB peak projection in the risk sheet has been exceeded by the supplementary tier's checkpoints, without consequence at this headroom.

## 3. Remaining-work projection

| Remaining | Est. time | Cost @ $0.90/hr |
|---|---|---|
| Supplementary finish | ~0.3 hr | $0.27 |
| NCP carve finish + 2 trainings | ~1 hr | $0.90 |
| Trained eval + test-once + VERITE | ~1 hr | $0.90 |
| PASS 2 stream | ~1.5 hr | $1.35 |
| Calibration / verdict / publish / pull | ~1 hr | $0.90 |
| **Total remaining** | **~4.5–5 hr** | **$4.05–4.50** |

- Balance $6.5852 − $4.50 (worst case) = **$2.09 margin**; best case $2.54.
- Projected total spend $3.19 + $4.05–4.50 = **$7.24–7.69 vs the $8 hard stop** — inside, with $0.31–0.76 of headroom. PASS 2's stream rate is the one measured-unknown that could stretch this; the descope order protects the core if it does.

## 4. Ops facts — pod vs the user's screenshots

| Fact | Screenshot (console) | Pod (live) | Consistent? |
|---|---|---|---|
| GPU | RTX 4090, 24 GiB, driver 595.112.07 | NVIDIA GeForce RTX 4090, 24,564 MiB, driver 595.112.07 | ✓ exact |
| CPU model | AMD EPYC 7K62 | AMD EPYC 7K62 48-Core | ✓ exact |
| vCPU / RAM | 16 vCPU / 41 GB (allocation) | OS sees host: 96 threads / 251 GB | ✓ explained — the console figures are the container's allocated share (telemetry showed 38.18 GiB usable, consistent with a 41 GB allocation); the pod OS reports the physical host's totals. Not a contradiction. |
| Rate | $0.90/hr total ($0.89 + $0.007) | API spend/hr 0.897; measured effective $0.898/hr | ✓ |
| Disk | 50 GB container, 26 GB used @17:54 | 50 GB, 35 GB used @19:06 | ✓ (growth explained above) |
| Pod identity | u4eixy0wfqbgll "laya-mainrun", US secure | API status: RUNNING, same id, SSH 47.47.180.28:21588 | ✓ |

Actual resource use remains far inside the allocation (telemetry: host RAM 6.4 GB of 38.2 GiB usable during streaming; GPU 3–6.6 GB of 24 GB observed across stages).

*Read-only audit: nothing on the pod or in the run was modified; the pod was not stopped or terminated.*
