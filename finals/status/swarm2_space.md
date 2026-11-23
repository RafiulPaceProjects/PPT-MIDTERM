# Swarm-2 Audit — HF Space app v2 (VM copy + pod copy)
Date: 2026-11-22 · Read-only audit · Auditor: swarm agent
Scope: ~/workspace/misinfo_run/hf_space/ (VM), /workspace/Misinformation/hf_space/ (pod), pod runs/packs.json, SPACE_DESIGN_DECISION_2026-11-22.md

## VERDICT: READY — no findings. All five audit items pass; the only gaps are the two publish-stage products (results.json, examples/) that are correctly absent pre-publish.

## 1. VM app.py — compile, packs, questions, layout, logic
- `python3 -m py_compile app.py` → OK (18,182 bytes). The `__pycache__` the compile created was removed afterwards; the tree is back to exactly app.py / README.md / requirements.txt.
- Pack registry contains EXACTLY the two specified packs: `mmfakebench`, `newsclippings` (VERITE correctly not served — Results-only, per the decision note).
- Verbatim-question diff vs the pod's `runs/packs.json` (programmatic comparison of the executed PACKS dict against the pod JSON): **20/20 MATCH** —
  - mmfakebench native instructions + criteria: MATCH · fake instructions + criteria: MATCH
  - newsclippings native instructions + criteria: MATCH · fake instructions + criteria: MATCH
  - Also matching per pack: labels, display names, noul_threshold (0.5 both).
- AFTER repos exactly as specified:
  - mmfakebench → `RafiulHaiderbro/laya-vision-fullft-mmfakebench`
  - newsclippings → `RafiulHaiderbro/laya-vision-fullft-newsclippings`
  - BEFORE = `thaitea/laya-vision` @ revision `f2fe3c12cb6d04c59d8a190250bf3fb40fc828dc` (pinned), matching the decision note.
- Three-stage layout present: section headers "1 · Input", "2 · Processing", "3 · Output" (3 matches), with a per-dataset serving line and a processing panel rendering the pack's two questions + arbitration rule.
- Uncertain-badge logic present and correct in form: `if choice_fake != noul_fake:` (line 173) appends the "⚠ uncertain — the two questions disagree…" badge.
- Flip callout present: "### 🔀 Training changed the verdict: **{before} → {after}** on this pair." (line 214), with a same-verdict confidence-comparison line as the alternative branch.
- Temperature hook: AFTER choice probabilities are temperature-adjusted only when results.json supplies the pack's fitted temperature; fail-soft otherwise — as specified.

## 2. Pod copy — sync verified
- Pod path: `/workspace/Misinformation/hf_space/` containing exactly app.py, README.md, requirements.txt.
- **md5(app.py): pod `af9837546fbf36157253206a16860a78` == VM `af9837546fbf36157253206a16860a78`** — the run log's claim is TRUE. The v2 copy on the pod is byte-identical to the audited VM copy; no older copy can be published by accident from that directory.

## 3. README numbers vs verified baselines
BEFORE table in README.md:
| Dataset | In README | Verified | |
|---|---|---|---|
| MMFakeBench val (1,000) macro-F1 | 0.2079 | 0.2079 | ✓ |
| MMFakeBench test ablation macro-F1 | 0.2037 | 0.2037 | ✓ |
| NewsCLIPpings val accuracy | 0.5141 | 0.5141 | ✓ |
| VERITE accuracy | 0.3467 | 0.3467 | ✓ |
- No stale October numbers in README.md (0.5083 / 0.3566: zero occurrences).
- In app.py, the only occurrences of 0.5083 / 0.3566 are inside the explicitly-labelled footnote under the current RESULTS_MD table ("The October audit measured 0.5083 … under the earlier question wording — the small deltas are the wording, not the model."). That is intentional provenance context beneath the current numbers, NOT a stale BEFORE entry. The app's scoreboard fallback line also uses the current set (0.2037 / 0.5141 / 0.3467).

## 4. requirements.txt — sane for a CPU Space
- `torch --index-url https://download.pytorch.org/whl/cpu` — CPU wheel index, correct for a free CPU Space.
- `laya @ git+https://github.com/r33drichards/laya-vision@9e1e2419d855ad3e1a2af4d4bd1ef6be5418842c` — the dev VLM package pinned to the rehearsal-verified commit, with the comment explaining why PyPI laya cannot be used.
- gradio, transformers, peft, pillow, huggingface_hub present. Gradio's version is carried by the README frontmatter (`sdk_version: 5.0.0`) rather than a requirements pin — standard HF practice, noted for completeness, not a finding.

## 5. Pre-publish state — the absence is the only gap
- `results.json`: ABSENT on the VM copy and ABSENT on the pod copy — correct; it is a publish-stage product (scoreboard_md + after_md + per-pack temperatures from final_results_bundle.json), and the app degrades fail-soft without it.
- `examples/`: ABSENT on both copies — correct; publish-stage product (MMF 4 VAL items one per class; NCP from saved tune/carve files; never test). The app's per-pack examples loader is fail-soft and hides the blocks when the files don't exist.
- Nothing else in the decision note's publish duties is stale or contradicted: both winner-repo names in the app match the duties; the smoke-check duty (boot + one live predict per pack) remains a publish-time action, not a pre-publish artifact; no placeholder numbers are hard-coded anywhere in the AFTER path (AFTER panels report "not published yet" until the repos exist, via a live repo_exists check).

## Bottom line
The Space staging is exactly what the decision note specifies, the pod copy is provably the same bytes, the published numbers will be the run's own measured baselines, and the app cannot ship stale or invented AFTER content. Publish can proceed when the run reaches that stage; its remaining work is the two winner-repo pushes, results.json, examples/, and the per-pack smoke check.
