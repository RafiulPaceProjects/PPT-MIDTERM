# The LAYA Notebook — Presenter's Walkthrough

**For:** Rafiul Haider, CS 668 Team 3 — Pace University Analytics Capstone, Fall 2026 (CRN 72369)
**What this is:** a study guide for showing the Colab notebook "Research" at the final. It explains every part of the notebook in plain language: what it does, why it is there, what its output means, and one sentence you can say out loud while that part is on screen.
**How to use it:** read §1 until you can say it without looking. Skim §2 once. Study §3 and §5 the night before. Keep §6 open on your phone during the demo.
**A note on results:** the main run executes through this notebook, and its outputs land in the cells themselves. The 12-run grid is **complete** — its scores are folded into this guide as verified fact, read from the run receipts. Everything after selection (the NewsCLIPpings arm, the supplementary tier, the test-once scoring, transfer, calibration, the verdicts, publish, and the cost ledger) is marked **[PENDING]** where it appears and fills in at run completion. The executed notebook is the source of truth, and every number in it traces to a file (see the notebook's closing section, "How to check this work").

---

## 1 · The 60-second story

Say this, or something very close to it, to open:

> "Our team studies multimodal misinformation detection — deciding whether an image-and-caption pair is genuine or fake, and if fake, in what way. We work with LAYA-Vision, a model that answers questions as *typed decisions*: instead of free text, it returns a probability for each defined answer, which means we can score it exactly. Before training anything, we audited the pretrained model — and the audit is the real starting point of this project. On MMFakeBench its paired score was 0.2037 macro-F1, and the per-class recalls showed why: out of 300 genuinely original items it recognised **one**. It had collapsed onto answering 'mismatch' for almost everything — 289 of 300 mismatch items right, nearly nothing else. A simple TF-IDF text baseline beat it, and we also found that the dataset's source metadata alone can score 0.9150 — which is label leakage, so we banned it as an input. So the research question became: can careful adaptation on a small, honestly split training set — 490 records — fix this, and can we prove it without fooling ourselves? We froze the rules before running anything: the winner is chosen on a 105-row tune split only, the test split is scored exactly once behind a guard, calibration gets its own reserved split, and success was defined in advance as at least +0.03 macro-F1 with a bootstrap confidence interval that excludes zero. This notebook is that experiment, end to end — gates, baselines, a 12-run training grid comparing full fine-tuning against LoRA, a second training arm that gives NewsCLIPpings its own trained weights, fifteen supplementary ablations around the winner, the single test scoring, calibration, and the published model and demo. The grid's verdict is already in: full fine-tuning with the plain soft_ce loss at the longest budget won, at 0.7389 tune macro-F1 — nearly triple the base model's 0.259 on the same split. Every number in it traces to a saved file."

That paragraph contains the whole arc: **problem → audit found a collapse → pre-registered fix → notebook as proof.** Everything else in the notebook is machinery that makes one clause of that paragraph true.

---

## 2 · Cell-by-cell guide

The notebook has 57 cells in 18 numbered sections (§0–§17), plus four post-selection patch sections (§7a–§7d, inserted after the winner froze — the notebook flags them with its own FREEZE PATCH banner at cell 22), front matter, and a closing audit guide. Sections are the anchor — use them when you talk ("in section six…"), because the audience sees the section headers as you scroll. Cell numbers below are the final notebook's.

### Front matter — title and review guide (cells 0–1)

- **What it does:** States what the notebook is: the notebook *is* the run. Run All on the pod executes the whole experiment, visibly, top to bottom. The review guide points a reader to the five places that matter (CONFIG, gates, grid, eval, publish) and lists the standing rules baked in.
- **Why it exists:** So that nobody — examiner, teammate, or you in three months — has to wonder whether the real experiment happened somewhere else, off-stage. It didn't; it's all here.
- **What "good" looks like:** A reader can find any decision in under a minute from this page.
- **SAY THIS:** *"This notebook is not a report about the experiment — it is the experiment. Everything you will see ran from these cells, in this order."*

### Front matter — Research design (cell 2)

- **What it does:** The academic core. Three research questions (RQ1: can small-data adaptation move the model from near-chance to defensible? RQ2: full fine-tuning vs LoRA at this scale? RQ3: does calibration on a reserved split fix the probabilities?), a decisions table giving the rationale and citation for every design choice, and five **pre-registered predictions, H1–H5**, each with the observation that would falsify it.
- **Why it exists:** Pre-registration. The predictions and the success rule were written down on 2026-11-22, before any cell executed. That is what stops a result from being a story invented after the fact — the hypotheses can *lose*, in public, against criteria fixed in advance.
- **What "good" looks like:** Every prediction is a range or a threshold, not a vibe. H1 predicts full-arm tune macro-F1 of 0.30–0.42; H4 predicts the worst class recall recovers to at least 0.25. If the run lands outside a band, the prediction is recorded as missed — that is the system working, not failing. One registered prediction carries a disclosed amendment: H2's text stands exactly as registered, but amendment (c) — recorded in the notebook's own FREEZE PATCH banner (cell 22) — re-aims its judgement from the base model's transfer score to a NewsCLIPpings arm trained on NewsCLIPpings' own data (§7a–§7c), with the base transfer number still reported beside it. The prediction was not edited; its target was amended, in the open.
- **SAY THIS:** *"These predictions were registered before the run. The notebook is not allowed to move them — and it doesn't."*

### Front matter — The whole study on one page (cell 3)

- **What it does:** Three diagrams — input, process, model. Input: three benchmarks; each item is one record (image + caption) asked as two typed questions (the native choice question and the binary *noul* Fake question — see the glossary). Process: gates → baselines → 12-run grid → tune-only winner → test once → calibration → publish. Model: LAYA-Vision with a frozen image tower and a trained language side.
- **Why it exists:** A five-minute reader should understand the study without reading code. It is also your safety net in the demo: if you lose your place, come back to this cell.
- **What "good" looks like:** A visitor can retell the study after this cell alone.
- **SAY THIS:** *"If you read only one cell, read this one — the rest of the notebook is the machinery that makes these three pictures true."*

### §0 · CONFIG (cells 4–5)

- **What it does:** Every variable that controls the run, in one place: the seed (20261122), the base model pinned to an exact revision (`thaitea/laya-vision` @ f2fe3c1), the step grid [245, 490, 735], the two losses, the learning rates, the LoRA settings, the three datasets with their *native* metrics (never one metric forced on all three), the success thresholds (+0.03, recall drop ≤ 5 pp), the Hugging Face repo names, the VisualNews tar URL, the `PUBLISH` switch, and the per-dataset **pack registry** — each dataset's own choice and noul questions, label set, native metric, and checkpoint pointer (the registry §7a materializes after selection).
- **Why it exists:** Repeatability. If a number is wrong here, it is wrong everywhere — which is exactly why it all lives in one cell that can be checked hardest. Nothing is allowed to change mid-run.
- **What "good" looks like:** You can point at any number in the results and trace it back to a line in this cell.
- **SAY THIS:** *"Every decision in the experiment lives in this one cell — pinned model revision, pinned seed, frozen thresholds. Nothing is tuned quietly later."*

### §1 · Setup (cells 6–7)

- **What it does:** Prepares the pod: installs the pinned package versions (the exact environment proven in the rehearsal), places the two run modules (`laya_trainer.py`, `visualnews_stream.py`) into the workspace, makes sure the pinned base checkpoint exists as a local snapshot, and checks the GPU.
- **Why it exists:** Environment drift is a silent result-killer — a different library version can change numbers without changing code. The rehearsal proved the stock pod image's library stack actually breaks, so the versions are pinned to the ones that were verified.
- **What "good" looks like:** The cell prints the environment it built and asserts a GPU is present; if the GPU is missing, it stops rather than crawling on CPU.
- **SAY THIS:** *"Setup pins the exact software versions we rehearsed with — the same environment that produced the rehearsal evidence, not whatever happens to be current."*

### §2 · Data (cells 8–9)

- **What it does:** Inventories what the sync put on the pod and *counts* it: the fine-tune records (490 train / 105 tune / 105 calib), the MMFakeBench and VERITE trees, the annotations. It asserts every tree the run depends on — if something is missing, it fails here, loudly, before any compute is spent. NewsCLIPpings *images* are deliberately absent (they are streamed later, never saved); only its annotations live on disk.
- **Why it exists:** "The file wasn't there" is the most common way experiments quietly change shape. Counting is cheap; discovering a missing split after training is not.
- **What "good" looks like:** Printed counts match the design: 490 / 105 / 105 records, full annotation files.
- **SAY THIS:** *"Before anything trains, the notebook counts what it actually has — the experiment runs on the data it claims to run on."*

### §3 · Pre-training verifications — the gates (cells 10–11)

- **What it does:** Two checks that must pass before training, and the notebook stops if either fails ("fail closed"). **Gate 1 — tokenization audit:** LAYA *skips* items that are too long instead of truncating them, so this cell measures every one of the 1,400 records and counts how many would be skipped at the token budget. **Gate 2 — checkpoint round-trip:** save the model, reload it, and compare every tensor.
- **Why it exists:** A silent skip is a silent change to the training data; a checkpoint that can't reload is not a result. Both failure modes are invisible unless you measure them first.
- **What "good" looks like:** The rehearsal measured the real values: **0.00% of 1,400 records over the token limit** (the gate fails the run at 2%), and the round-trip came back **416 tensors, bit-identical**. In the executed notebook, the gate prints its own measurements — a passed gate is visible in the output, not asserted in prose.
- **SAY THIS:** *"Nothing trains until these two gates pass. They measure the two ways this model family can silently change your data or lose your result."*

### §4 · Baseline eval (cells 12–13)

- **What it does:** Scores the *pretrained* model — no training yet — on MMFakeBench validation and VERITE, through the project's own baseline code, saving every prediction to a file. NewsCLIPpings is not here: its baseline is the stream pass in §5, scored by the same study code.
- **Why it exists:** You cannot claim an improvement without a "before" measured by the same code on the same rows. These saved predictions are the "before" for every comparison in the notebook — including the paired bootstrap, which needs both models' answers on identical rows.
- **What "good" looks like:** Prediction files exist for both datasets, and the metrics match the October audit (paired MMFakeBench macro-F1 ≈ 0.20; VERITE paired ≈ 0.3566).
- **SAY THIS:** *"Baselines first, measured with the same code we will use after training — so 'better' means better on the same rows, not better on an easier test."*

### §5 · NewsCLIPpings — the VisualNews stream leg (cells 14–17)

- **What it does:** NewsCLIPpings' images live in VisualNews, which ships as a single 91 GB archive — too big for the pod's disk. So this leg *streams* it: one pass over the archive, over the network. Each referenced image is verified in memory (full decode; a stub image under 8 pixels on a side counts as degenerate), handed to the model, and discarded. Nothing is saved except predictions and accounting. The cell defines the streaming function once (cell 15); **PASS 1** (cell 17) runs it with the base checkpoint — that is the NewsCLIPpings baseline. PASS 2 runs later in §11 (cell 41) — and note whose weights it carries: not the MMFakeBench winner, but NewsCLIPpings' **own** trained checkpoint from §7c. Each dataset is served by its own pack's weights; that separation is the design, not a detail.
- **Why it exists:** The dataset is a full third of the study (and H2 lives here), and "we couldn't store it" is not a reason to drop it. Streaming with a verifier is how you evaluate on data you never hold.
- **What "good" looks like:** The pass prints full accounting, per source (bbc / guardian / usa_today / washington_post): how many images were referenced, scored, and skipped — and accuracy is computed over the *scored* rows and labelled that way. Skips are integrity-only: a broken file is skipped and ledgered; the model is never protected from a hard-but-valid image.
- **[PENDING]** PASS 1's final per-source accounting (referenced / scored / skipped, with reasons) and its headline accuracy fill in when the pass completes; they are read side-by-side with PASS 2's in §11.
- **SAY THIS:** *"We never download this dataset. The images stream past once, each one is verified before the model sees it, and only the predictions stay."*

### §6 · Training — the 12-run grid (cells 18–19)

- **What it does:** Trains all 12 configurations: 2 arms (full, LoRA) × 2 losses (rlcd, soft_ce) × 3 step budgets (245, 490, 735), in ascending step order so the cheapest run proves the machinery first. Training uses every record in the train file (both question forms); the selection score — tune macro-F1 — is computed on the 4-class form only. Every run writes a receipt file: its full config, loss curve, tune score, and per-class recalls. A run with an existing receipt is read back, not re-trained.
- **Why it exists:** This is the experiment's engine — and §3 of this guide is devoted to it, because *how* these 12 runs differ is the RQ2 story.
- **What "good" looks like:** Twelve receipts, twelve tune scores, and a visible spread — and the completed grid delivered exactly that: from **0.7389** at the top to a collapsed **0.1946** at the bottom (the full table is §3.8 of this guide). If all twelve had scored identically, the grid would have taught nothing.
- **SAY THIS:** *"Twelve runs, one factor changed at a time — so afterwards we can say what actually caused the differences, not just which run won."*

### §7 · Selection (cells 20–21)

- **What it does:** Picks the winner: the single highest tune macro-F1 across **both** arms, written to `runs/winner.json`. Nothing else is consulted — not test, not vibes.
- **Why it exists:** Selection and verdict are kept separate on purpose. This cell chooses; §13 judges. If selection peeked at the test split, the test score would stop meaning anything.
- **What "good" looks like:** Exactly 12 receipts are required — the cell asserts the count before choosing, so a half-finished grid cannot produce a "winner." It produced one: **full · soft_ce · 735 steps, tune macro-F1 0.7389**, with LoRA · soft_ce · 735 the runner-up at 0.7187. The margin is 0.020 on 105 tune items — a real selection under the frozen rule, and (§3.7) a gap you present as *within noise*, not as proof the arms differ.
- **SAY THIS:** *"The winner is chosen by one number, on the tune split only. Whether that win is real is a different question — and a different section judges it."*

### FREEZE PATCH banner (cell 22)

- **What it does:** A markdown cell the notebook wears openly: everything from here through §7c was inserted *after* selection froze, on 2026-11-22. It is the amendment record — amendments (c) and (d) — sitting inside the notebook itself rather than in a side document.
- **Why it exists:** Post-registration changes are legitimate only when they are impossible to miss. The banner makes the notebook confess, in place, exactly where the design grew and why.
- **SAY THIS:** *"Everything after this banner was added after the winner froze — it's labelled, dated, and it never reaches back into selection."*

### §7a · Dataset packs (cells 23–24)

- **What it does:** Materializes the pack registry from CONFIG into `runs/packs.json`. For each dataset the pack carries: its own native choice question, its own noul question, its label set, its native metric, its splits, its calibration settings, and a checkpoint pointer. From here on, every evaluation loads the pack for the dataset being served, evaluates, unloads, and prints which weights are serving ("now serving: <dataset> / weights: <checkpoint>").
- **Why it exists:** MMFakeBench's winner must never silently score another dataset. The pack is the mechanism that keeps each dataset's questions, weights, and calibration separate — and makes the switch visible in the output.
- **SAY THIS:** *"Each dataset travels as a pack — its own questions, its own weights, its own calibration. The notebook switches packs; it never mixes them."*

### §7b · NewsCLIPpings training data (cells 25–26)

- **What it does:** Carves NewsCLIPpings' own training protocol — roughly 2,000 train / 250 tune / 250 calib items, each in both question forms — from the official **train split only**. The val split stays the reported evaluation (streamed, §5/§11); the test split is untouched. The carve's images are the one deliberate, labelled exception to the stream-only rule: this bounded training subset is saved on the pod, because training needs repeated passes that a one-pass stream cannot give.
- **Why it exists:** Amendment (c). NewsCLIPpings had everything a training arm needs — an official train split, probe evidence the signal is learnable (+6.24 pp), and headroom (0.5083 zero-shot) — and the original design gave it none. §5 Q8 of this guide is the full answer to "why this dataset and not VERITE."
- **SAY THIS:** *"NewsCLIPpings trains only on its own train split. Its validation set is still only ever streamed and scored — never trained on."*

### §7c · NewsCLIPpings training arm (cells 27–28)

- **What it does:** Trains the MMFakeBench winner's recipe — its arm and its loss — at two step budgets on the §7b carve. Deliberately *not* a second 12-run grid. The NCP winner is picked on the NCP tune split only, and the NewsCLIPpings pack's checkpoint pointer then aims at those weights.
- **Why it exists:** This is where H2 is earned. The trained arm is judged in §11's PASS 2 against its band (0.55–0.65) **and** against the base model's own number on the same stream (PASS 1: 0.5083 zero-shot val accuracy) — the bar includes clearing the probe's implied gain, at least +6.24 points over 0.5083.
- **[PENDING]** The arm's two training scores, its winner, and its NCP tune result fill in when §7c executes.
- **SAY THIS:** *"NewsCLIPpings doesn't borrow MMFakeBench's winner — it earns its own, with the winning recipe, on its own data."*

### §7d · Supplementary ablation tier (post-selection patch — follows §7c in the executed notebook)

- **What it does:** Fifteen more trainings around the frozen core, receipts quarantined in `runs/supplementary/` so they can never enter the 12-receipt selection: **head-only** arm × both losses × {490, 735} steps (4); **LoRA rank 8 and rank 32** at the winner's loss × {490, 735} (4); **full-arm encoder learning-rate variants** (5e-6 and 2e-5) at the winner's loss × {490, 735} (4); the **winner retrained under a second seed** (1); and a **data-size axis** — the winner's recipe at 490 steps trained on the first 245 and first 122 items of the frozen train set (2).
- **Why it exists:** Amendment (d). Each line answers a question an examiner can fairly ask — is the head alone enough? does adapter size matter? was the learning rate the real story? was the winner just lucky? would more data beat more steps? §3.9 of this guide teaches how to read the tier.
- **[PENDING]** The tier's results table fills in as its receipts land.
- **SAY THIS:** *"The core grid was registered and frozen. This tier is the systematic ablation around it — every other knob an examiner can name, turned one at a time, after selection, where it can't contaminate anything."*

### §8 · Method comparison (cells 29–33)

- **What it does:** Reads the 12 receipts and takes the grid apart factor by factor: arm effect (full vs LoRA, holding loss and steps fixed), loss effect (rlcd vs soft_ce, holding arm and steps fixed), step curves (245 → 490 → 735, holding arm and loss fixed), per-class recall profiles by method, and a generated verdict on which method the evidence supports — including, when the margin is small, saying the methods are **not separated by this evidence**. Its markdown panels (cells 29 and 32) explain each arm and each loss in plain words.
- **Why it exists:** A winning number alone teaches nothing. This section is what turns "run #7 won" into "LoRA at 490 steps won *because*…" — or into the honest statement that the data can't tell the methods apart.
- **What "good" looks like:** Clean pairwise gaps (see §3 of this guide for how to read them) and a method verdict whose confidence matches the margin. On the completed grid it found: soft_ce beat rlcd in all six matched pairs; the full-vs-LoRA gap at the top was +0.020 — inside the n=105 noise this section itself flags; and one configuration (LoRA · rlcd · 735) collapsed outright, which the per-class views expose rather than average away.
- **SAY THIS:** *"Winning isn't explaining. This section holds two factors still and moves one, so each gap in the table is one factor's effect."*

### §9 · Trained eval (cells 34–35)

- **What it does:** Re-runs the §4 evaluation — same CLI, same split, same code — with only the checkpoint changed to the winner, and prints baseline and winner side by side.
- **Why it exists:** The controlled comparison. One variable changed (the checkpoint), so the difference is attributable to training.
- **What "good" looks like:** The winner's val numbers improve on the baseline's *and* the per-class profile changes shape — especially the 'original' class recall climbing off zero (that is H4's signature).
- **SAY THIS:** *"Same test, same code, new checkpoint. Anything that changed here was caused by the training — there is nothing else it could be."*

### §10 · Test — scored once (cells 36–38)

- **What it does:** Scores the MMFakeBench **test** split — here, and nowhere else in the notebook: once, with the frozen winner, after selection. A marker file (`runs/.test_scored`) makes the guard mechanical: if the marker exists, the cell *refuses to run* and prints that the recorded result stands. The second cell (cell 38) pairs the winner's test predictions with the baseline's saved test predictions, row by row, and computes the paired bootstrap confidence interval that H1 is judged on (2,000 resamples, seed pinned).
- **Why it exists:** A test set you score repeatedly becomes a tuning set — you start choosing what it likes, and its verdict stops being independent. The marker turns "we only ran it once" from a promise into a mechanism.
- **What "good" looks like:** One test result file (`runs/test_once.json`), one delta with a confidence interval, and a guard that visibly refuses a second scoring.
- **[PENDING]** The single test score and the bootstrap interval fill in when §10 executes — this is the number H1 is formally judged on.
- **SAY THIS:** *"The test split is scored exactly once, and the notebook itself enforces that — if I ran this cell again right now, it would refuse."*

### §11 · Transfer + specialist eval (cells 39–41)

- **What it does:** Two different questions share this section, and keeping them apart matters. **Cell 40 — VERITE transfer:** the MMFakeBench winner, through the same CLI, on a dataset that contributed no training signal of any kind. **Cell 41 — stream PASS 2:** NewsCLIPpings val streamed a second time, but now served by the NewsCLIPpings pack's **own trained weights** (§7c) — printed against PASS 1's base-model figure from §5. Nothing here feeds back into selection.
- **Why it exists:** VERITE is the honest transfer test (H3): nothing about it was trained on, tuned on, or selected on — its score is the difference between "fitted" and "learned." NewsCLIPpings is no longer a transfer question at all: amendment (c) made it a *specialist* question — does a dataset with its own training arm beat its own base-model number? H2 is judged on the trained arm here, with the base transfer figure (0.5083) reported beside it, never hidden.
- **What "good" looks like:** VERITE lands in the H3 band (0.38–0.48, from a 0.3566 baseline). The trained NCP arm lands in the H2 band (0.55–0.65) **and** clears PASS 1 by at least the probe's margin (+6.24 pp over 0.5083). Landing below band is reported as-is — this section is where honest projects find their limits.
- **[PENDING]** PASS 2's per-source accounting (referenced / scored / skipped) and both scores fill in when §11 executes, next to PASS 1's accounting for the side-by-side.
- **SAY THIS:** *"VERITE never trained anything — its score is what travelled. NewsCLIPpings answers a different question now: it has its own trained weights, and this pass holds them against the base model's number on the same stream."*

### §12 · Calibration (cells 42–43)

- **What it does:** Fits temperature scaling — one temperature per question type — on the **reserved 105 calib records only** (never tune, never test), saves the calibrated winner as a separate checkpoint, and measures H5: ECE (expected calibration error — how far the model's stated confidence is from its real accuracy) before and after, on tune, with accuracy required to be unchanged.
- **Why it exists:** A probability you can't trust is a number, not a decision tool. The baseline's raw ECE is ≈ 0.466 — when this model says "80% sure," it is nowhere near right 80% of the time. Calibration is the fix, and the reserved split is what keeps the fix honest: temperatures fitted on selection data would just be more overfitting.
- **What "good" looks like:** ECE drops below 0.15 (H5's target) with accuracy identical before and after — calibration moves confidence, never the answers.
- **[PENDING]** The fitted per-pack temperatures and the before/after ECE pair fill in when §12 executes — that pair of numbers is H5.
- **SAY THIS:** *"Calibration doesn't change what the model answers — it makes the model's confidence mean what it says. And it's fitted on its own reserved data, so it can't cheat."*

### §13 · Verdict (cells 44–45)

- **What it does:** Judges H1–H5 against the frozen rule and prints the verdict in full: H1 on test (delta + CI from §10) and on tune; H2 on the **trained NewsCLIPpings arm** (its 0.55–0.65 band, and its margin over the base model's 0.5083 from PASS 1); H3 against its transfer band; H4's minimum recall against 0.25; H5's ECE against 0.15. It also assembles `midterm_results.json` — the comparison table the plots and the paper read.
- **Why it exists:** This is where the pre-registration pays off. The criteria were frozen in October and the predictions in November; this cell just applies them. Met or not met, as they fall.
- **What "good" looks like:** A printed verdict block where every hypothesis has a number, a criterion, and a verdict — no hypothesis quietly dropped.
- **[PENDING]** The block completes at run end: H1's formal test verdict, H2, and H5 are still open. H1's tune side and H4 already read as passed from the receipts — §3.8 of this guide has both.
- **SAY THIS:** *"Nothing in this cell was decided after seeing the results. The rule was frozen first; this is just the rule, applied."*

### §14 · Results — the three pictures (cells 46–49)

- **What it does:** Three charts, drawn only from saved receipts and prediction files (these cells never train and never score): **(a)** the grid — tune macro-F1 for all 12 configs; **(b)** per-class recall, baseline vs winner; **(c)** calibration — the reliability curve plus ECE before/after. If an input file isn't there yet, a cell prints a note instead of crashing, so the notebook always runs end-to-end.
- **Why it exists:** Every claim in the study reduces to one of these three pictures: *what the grid did, what changed per class, whether the probabilities can be trusted.*
- **What "good" looks like:** Chart (b) is the money chart — the baseline's collapsed profile (one tall 'mismatch' bar, 'original' at zero) against the winner's spread-out profile.
- **SAY THIS:** *"Three pictures: the grid, the per-class change, and the calibration. If a claim I make isn't in one of these, it isn't a result."*

### §15 · Publish (cells 50–51)

- **What it does:** Pushes the **calibrated** winner to Hugging Face with a model card written from the real results, and creates/updates the live demo Space. It is guarded twice: the CONFIG `PUBLISH` switch must be on, and a marker file makes a re-run announce itself instead of silently republishing. The access token is read from the environment or a file — never printed.
- **Why it exists:** A result nobody can run is a claim. The published checkpoint and the before/after demo are how an examiner checks the work with their own image and caption.
- **What "good" looks like:** The model page and Space are live; the Space's "after" model is the published checkpoint; the marker records exactly what was pushed.
- **SAY THIS:** *"The model and the demo are public — anyone in this room can test the before and after with their own example."*

### §16 · PaperOrchestra bundle (cells 52–53)

- **What it does:** Exports the idea summary and experiment log for the paper-writing pass, assembled from the real saved results.
- **Why it exists:** The paper must be written from the same files the notebook produced — every number in the paper traces to these exports, not to anyone's memory of the run.
- **What "good" looks like:** The bundle's numbers match the notebook's outputs exactly, because they are generated from them.
- **SAY THIS:** *"Even the paper is generated from the result files — the numbers can't drift between the experiment and the write-up."*

### §17 · Complete record (cells 54–55)

- **What it does:** Assembles `final_results_bundle.json` — one machine-readable record of the entire run: config, gates, data inventory, baselines, all 12 receipts, the selection, the test-once result with its bootstrap detail, both transfer legs with their stream accounting, calibration, the H1–H5 verdicts, and a deviations list. Anything missing is recorded as `null` and named in a printed missing list — gaps are visible, never papered over. The bundle also carries the run's **cost and operations ledger**: per-training wall time, peak GPU memory, host RAM, and dollars for all 29 trainings, plus per-stage durations and stream byte counts — checked against the pod's starting and ending balance.
- **[PENDING]** The final ledger figures fill in at run completion, before the pod is terminated.
- **Why it exists:** This bundle, together with the executed notebook, is the exact input the final paper is written from — and the single place an auditor starts.
- **What "good" looks like:** An empty missing list, or a short one that is honestly named.
- **SAY THIS:** *"One file contains the whole run — including a list of anything that's missing. The gaps are printed, not hidden."*

### Closing — How to check this work (cell 56)

- **What it does:** The audit guide: where every number comes from (which file, which cell), the rules that were frozen before anything ran, and links to the artifacts (model, Space, base checkpoint).
- **Why it exists:** It is the notebook grading itself — the standard the whole project holds itself to: *if a number is not in a cell output or one of the named files, it is not a result.*
- **SAY THIS:** *"If you doubt any number I've shown you, this cell tells you exactly which file to open to check it."*

---

## 3 · The training methods, and how training choices cause differences

This is the section to study hardest. The grid in §6 changes **three things** — arm, loss, and step budget — and the examiners' natural question is: *"What did each choice actually do?"* This section gives you each method on its own, what difference to expect from it, and how to read the notebook's charts as cause and effect. The notebook's own §8 makes the same points from the receipts; this section teaches you to say them.

### 3.1 · The FULL arm — retrain the reading-and-deciding parts

- **What actually changes inside the model:** the language encoder's own weights and the decision head are updated — 114.7M of the model's 201M parameters. The vision tower (the part that turns pixels into features) does not move at all; it is frozen in both arms (design amendment (b), §5 Q1 below).
- **How it learns:** with *differential learning rates* — two speeds on purpose. The encoder moves slowly (LR 1e-5): its pretrained features are valuable, so they are nudged, not shoved. The head moves fast (LR 1e-3): it starts with nothing task-specific, so it has the most to learn.
- **What to expect:** the highest ceiling of the two arms — the encoder can genuinely reshape itself around the task — and the highest risk: with only 490 training items, a fully trainable encoder can bend toward the small sample and *drift* away from what it knew, which is exactly the failure the literature on fine-tuning contrastive vision–language models warns about (the design section cites it as [5]).
- **SAY THIS:** *"Full fine-tuning retrains the model's reading-and-deciding parts, gently, and leaves its eyes untouched — most power, most room to drift."*

### 3.2 · The LoRA arm — teach through small plug-in corrections

- **What actually changes inside the model:** almost nothing of the original model. Small adapter matrices (rank 16, scaling α32, dropout 0.05) are inserted into the encoder's attention and MLP projections (the q/k/v/o and gate/up/down matrices), and only those adapters — plus the decision head — train. Every base weight, vision tower *and* encoder, stays exactly as pretrained. Each adapted weight effectively becomes *base + a small learned correction*, and the corrections train hot (LR 1e-3) because they start at zero and there are few of them.
- **Why this is the standard small-data move:** with 490 examples, you do not have enough evidence to rewrite a 201M-parameter model — but you have plenty to fit a small correction to it. The adapters are a built-in leash: the model can only move as far as the corrections let it, so it cannot forget as much. That is why the multi-agent audit flagged LoRA as the normal choice at this scale, and why the arm was added.
- **The rehearsal hint — labelled honestly:** in the rehearsal's tiny 20-step plumbing runs, LoRA's training loss fell further than the full arm's (3.57 → 0.24 vs 3.55 → 0.95), and on a 30-row tune slice its macro-F1 read higher (0.66 vs 0.42). Say this only with its label attached: **that was a plumbing test on 30 rows — it proves the machinery works, it is not evidence about the methods.** The grid is the evidence.
- **SAY THIS:** *"LoRA leaves the model untouched and teaches it through small plug-in corrections — cheaper, and with 490 examples, the leash is the point."*

### 3.3 · The rlcd loss — the model's home recipe

A *loss* is the score training tries to minimise — the definition of "wrong" the model learns from. **rlcd** is the objective LAYA was built around: a policy-gradient term with a proper scoring rule, computed over slightly noised versions of the model's own answers (noise σ = 0.3, groups of 4, weight 0.75), *plus* soft cross-entropy (weight 1.0). In plain terms: the model tries answers near its current answer, and is rewarded not just for being right but for putting its probability mass honestly — confident when it should be, hedged when it shouldn't. **What to expect:** because rlcd optimises the same kind of typed, probabilistic decision the model is *scored* on, it is aligned with the evaluation — if any loss teaches the model to be a better *decision-maker* rather than just a better guesser, it should be this one.

- **SAY THIS:** *"rlcd is the model's home recipe — it learns from noisy tries at each answer, scored by a rule that rewards honest confidence."*

### 3.4 · The soft_ce loss — the plain recipe, run as a control

**soft_ce** is soft cross-entropy alone: match the target distribution, nothing else. No exploration, no scoring-rule term — the cleanest, simplest training signal there is. One technical point worth knowing: soft_ce cannot be produced by the library's training loop (the policy-gradient term can't be switched off there), so the trainer implements it from the library's own pieces with identical grouping, schedule, clipping, and precision — meaning the two losses in the grid differ **only** in the objective, nothing else. **What to expect:** a cleaner, more direct signal that may train more stably — and if rlcd beats it, the gap *is* the policy-gradient term's contribution, measured. soft_ce exists so that contribution is a number, not an assumption.

- **SAY THIS:** *"soft_ce is the plain recipe — just be right. It exists so we can measure what the fancy recipe actually adds."*

### 3.5 · Step budget — how long to train on very little data

The grid trains each configuration for **245, 490, or 735 steps**. At batch size 8 over the 490 training items, that is roughly **4, 8, and 12 passes** over the training set (epochs). On tiny data this choice is a genuine dilemma, and it cuts both ways: too few steps and the model hasn't learned the task; too many and it starts *memorising* the 490 items — training loss keeps falling while real performance quietly gets worse (overfitting). The risk curve is not symmetric or known in advance, which is exactly why the budget is *searched* on the tune split instead of assumed: the tune scores at 245 → 490 → 735 trace the curve — and a downturn, a dip, or an outright collapse along that row is a finding, not a bug. **The completed grid produced all three shapes** (§3.8 has the table): under soft_ce the full arm was *still rising* at 735 (0.5954 → 0.6598 → 0.7389), no overfitting downturn inside the searched range; LoRA · soft_ce *dipped* at 490 (0.6282 → 0.5726) and then recovered to 0.7187 at 735 — a mid-training valley, **not** an early peak, and anyone who had stopped the search at 490 would have published the wrong shape; and LoRA · rlcd didn't overfit in the usual sense at all — it collapsed onto a single class.

- **SAY THIS:** *"With 490 examples, training longer helps until it hurts. We didn't guess where that point is — the grid measures it."*

### 3.6 · How to read cause — the factor-isolation rule

The grid varies three factors at once, which sounds like a confound — until you compare correctly. The rule (it is printed in §8 of the notebook): **hold two factors constant, vary one — the gap IS that factor's effect.**

- **Arm effect:** compare full vs LoRA at the *same* loss and steps (e.g., full·rlcd·490 vs lora·rlcd·490). Six such pairs exist; if LoRA wins most of them, that is a real arm effect, not one lucky run.
- **Loss effect:** compare rlcd vs soft_ce at the same arm and steps. Six pairs again.
- **Steps effect:** read along one arm·loss row (245 → 490 → 735). Rising then falling = the overfitting curve from §3.5, made visible.

§8's first code cell computes exactly these contrasts from the receipts, and §14's plot (a) draws all 12 tune scores so the pattern is visible at a glance. **The completed grid, read by this rule:** the *loss effect* is the loud one — soft_ce beat rlcd in all six matched pairs, by +0.03 to +0.27. The *arm effect* at the top is small: at soft_ce · 735, full 0.7389 vs LoRA 0.7187 — a +0.020 gap that §3.7's caveat applies to in full. The *steps effect* splits by loss: both soft_ce rows end at their highest point (LoRA's via a dip and recovery), the full · rlcd row crawls upward (0.5667 → 0.5880 → 0.6061), and the LoRA · rlcd row falls off a cliff at 735 (0.1946). **Any comparison that changes two things at once is confounded and is not evidence** — if an examiner proposes one ("but the best LoRA run beat the worst full run…"), the answer is: that comparison changes arm *and* steps; the paired comparisons are the evidence.

The second code cell of §8 adds the deeper view: **per-class recall by method.** Averages hide mechanism; recalls reveal it. The baseline's disease was specific — it collapsed onto 'mismatch' and abandoned 'original' (recall 1/300). So the question to ask of any method is not only "did the average rise?" but "**which class did it rescue?**" A method that lifts 'original' recall is *fixing the collapse*; a method that only piles more onto 'mismatch' is raising the average while leaving the disease in place. When you present a winner, name the class movement, not just the score.

- **SAY THIS:** *"Hold two factors still, move one — the gap is that factor's effect. And don't just read the average: read which class each method rescued."*

### 3.7 · "Best for LAYA" — how the study decides, and the honest caveat

The decision procedure is fixed: the winner is the highest **tune macro-F1 across both arms** (§7), and §8 then explains the choice with the factor contrasts, the winner's **recall profile** (did it fix the collapse, or just the average?), and later its **calibration** (§12 — a winner whose probabilities are meaningless is a weaker winner). What pattern would make each arm the answer:

- **LoRA is the answer if** it matches or beats full on tune F1 *and* shows the healthier recall profile — equal performance with a fraction of the trainable parameters and less drift risk is the better method at this data scale, full stop.
- **Full is the answer if** it separates clearly — a tune margin beyond noise *and* a recall profile LoRA can't match — because then the encoder genuinely needed to move, and the extra capacity earned its risk.

**What actually happened:** the full arm won the selection — full · soft_ce · 735 at **0.7389**, against LoRA's best of 0.7187 — but by 0.020 on 105 tune items, which is inside the noise band the caveat below describes. So the honest presentation is double, and you should give both halves: *the protocol selected the full arm*, and *the evidence does not separate the two soft_ce arms* — LoRA matched the winner within noise at a fraction of the trainable parameters, which is itself the RQ2 answer. What separated cleanly was not the arm but the loss, and the winner's recall profile (§3.8) is what confirms the win is a repair of the collapse, not an average trick.

**The caveat, said out loud before anyone asks:** the tune split has **105 items**. A gap of a point or two between methods is within the noise of 105 items, and §8's method verdict is written to say so — when the margin is small, it states the methods are *not separated by this evidence* rather than crowning a winner the data can't support. The §7 selection still stands (the protocol needs a winner to evaluate), but you present it as "selected under the frozen protocol," not as "proven better," unless the margin earns the stronger sentence.

- **SAY THIS:** *"The protocol picks the winner; the evidence decides how strongly I'm allowed to talk about it. On 105 tune items, small gaps are noise — and the notebook says so itself."*

### 3.8 · The completed grid — facts you can state as fact

The grid is done. These numbers come from the run receipts, not from expectations — this is the one part of the guide you no longer have to phrase in the future tense.

**Tune macro-F1, all 12 configurations (selection split, n=105):**

| arm · loss | 245 steps | 490 steps | 735 steps |
|---|---|---|---|
| full · rlcd | 0.5667 | 0.5880 | 0.6061 |
| full · soft_ce | 0.5954 | 0.6598 | **0.7389** |
| lora · rlcd | 0.4597 | 0.4505 | 0.1946 |
| lora · soft_ce | 0.6282 | 0.5726 | 0.7187 |

- **The winner:** full · soft_ce · 735 — **0.7389**, against the base model's **0.259** tune macro-F1 on the same 105 items. H1's registered band for the full arm was 0.30–0.42; the winner cleared the top of the band by more than 0.30. H1's tune-side bar is passed by an order of magnitude — the *formal* H1 verdict still waits on the single test scoring. **[PENDING: test-once score + paired bootstrap.]**
- **The winner's per-class recalls:** original **0.66** · textual **0.97** · visual **0.70** · mismatch **0.61**. The weakest class is 0.61, against H4's threshold of 0.25 — **H4 is passed on the winner's own profile.** Set that beside the baseline's test recalls (1/300 · 8/300 · 22/100 · 289/300): every class is repaired, and 'mismatch' — the baseline's crutch — is now the winner's *hardest* class, not its favourite answer.
- **The collapse inside the grid:** lora · rlcd · 735 scored **0.1946 — below the base model** — with recalls original 1.00 · textual 0.06 · visual 0.10 · mismatch 0.00. It collapsed onto 'original': the mirror image of the base model's collapse onto 'mismatch'. Say it plainly if asked: one configuration failed completely, the receipts show exactly how, and the selection rule never went near it. A grid that reports its failures is more believable than one that hides them.
- **The LoRA dip, correctly told:** lora · soft_ce went 0.6282 → 0.5726 → 0.7187. If anyone calls 245 steps its "peak," correct them: the curve dipped mid-training and recovered; the arm's best score is at 735, within 0.020 of the winner.
- **SAY THIS:** *"The winner nearly tripled the baseline on the selection split and repaired every class — its weakest class clears the recovery threshold two times over. And the one configuration that collapsed is in the table too, because the grid reports everything it ran."*

### 3.9 · The supplementary tier — amendment (d), and why it doesn't break the registration

- **What it is:** fifteen further trainings (notebook §7d), run *after* selection, with receipts quarantined in `runs/supplementary/`: **head-only** ×4 (is the head alone — the October probe's in-model cousin — enough?), **LoRA ranks 8 and 32** ×4 (does adapter capacity matter?), **encoder learning rates 5e-6 and 2e-5** ×4 (was the winner's rate the real story?), the **winner under a second seed** ×1 (was the winner just lucky?), and the **data-size axis** ×2 (the winner's recipe at 490 steps on the first 245 and first 122 training items — the grid's own 490-step sibling is the 490-item point of that curve).
- **Why it is legitimate:** the registered comparison — the 12-config grid and its selection — *closed* before the tier existed. The tier interrogates the winner; it cannot replace it. Its receipts live outside the selection's receipt glob, so if a supplementary run outscored the winner tomorrow, the winner would still be the winner and the test would still be scored by it. That quarantine is the whole difference between an ablation tier and quietly extending the search until something wins.
- **The descope rule, if anyone asks about budget:** if the run's money had tightened, this tier descopes *first* — before the NewsCLIPpings arm, and never at the expense of the registered core, the test-once scoring, or publishing.
- **[PENDING]** The tier's results table fills in as its receipts land; the final paper reports it as supplementary ablations around the pre-registered core, under exactly that name.
- **SAY THIS:** *"Everything an examiner could ask 'did you try…' about is in this tier — tried after selection, in the open, where the answers can inform the paper but never rewrite the result."*

---

## 4 · Five numbers to know cold

If an examiner asks for a number and you hesitate, it should never be one of these five.

1. **0.2037 — the baseline's paired macro-F1 (MMFakeBench test ablation).** The pretrained model's score on the full test population (9,999 usable rows), computed from saved predictions in the audit. Its validation-split sibling is 0.1985. *What it means:* near the floor for a 4-class problem — this is the "before" that H1 must beat by +0.03 with a confidence interval excluding zero.
2. **1/300 · 8/300 · 22/100 · 289/300 — the collapse, in per-class recalls.** Of 300 original items the baseline recognised 1; of 300 textual-distortion items, 8; of 100 visual, 22; of 300 mismatch items, 289. *What it means:* the model didn't fail evenly — it gave up and answered "mismatch" for nearly everything. This is the disease the whole experiment treats, and H4 (worst class recall ≥ 0.25 after training) is its recovery test.
3. **+6.24 pp [4.76, 7.70] — the transfer probe.** A logistic probe on the model's *frozen* features scored 57.4% on NewsCLIPpings test vs 51.1% zero-shot. *What it means:* the signal is already inside the frozen features — the strongest single piece of evidence that adaptation can work, and the justification for freezing the vision tower (amendment (b)). Its VERITE sibling, +4.37 pp [−1.36, 9.95], crosses zero: inconclusive, and always quoted as such.
4. **+0.03 macro-F1, CI lower bound > 0, recall drop ≤ 5 pp — the frozen success rule.** Fixed in the October 19 protocol, before any of these runs. *What it means:* three hurdles, all required — a real gain (not noise), statistical separation (the paired bootstrap interval must exclude zero), and no class sacrificed to buy the average.
5. **490 / 105 / 105, ×2 = 1,400 — the split sizes.** 490 training items, 105 tune (selection only), 105 calibration (reserved, post-selection), each item asked in 2 question forms = 1,400 records — the same 1,400 the tokenization gate audited at 0.00% over-length. *What it means:* small data, deliberately — every design choice (LoRA arm, reserved calib split, tune-only selection) is a response to these three numbers.

*Two supporting numbers worth having if the conversation goes there:* the metadata leakage ceiling **0.9150** (why source metadata is banned), and the baseline's raw calibration error **ECE ≈ 0.466** (why §12 exists; the binary accuracy floor of 0.695 — scoring "all Fake" without looking — is why accuracy alone was never trusted here). And the grid's headline pair: **0.7389 vs 0.259** — winner vs base, tune macro-F1 on the same 105 items (§3.8 of this guide).

---

## 5 · Hard questions, ready answers

Each answer names where the evidence lives in the notebook. Keep answers to two or three sentences; offer the cell, don't re-derive the study.

**Q1. Your "full" arm freezes the vision tower. Isn't that just… not full fine-tuning?**
*Evidence: Research design cell (decisions table, amendment dated 2026-11-22); §0 CONFIG comment; §3 of this guide.*
"The name is honest about what trains: encoder plus head — 114.7M of 201M parameters. We originally specified nothing frozen; the rehearsal proved the library's training loop cannot unfreeze the vision tower, so we amended the design the same day, in writing, with the reason recorded — and the frozen-feature probe transferring at +6.24 points says the frozen features already carry the signal. Disclosing the amendment makes the work *more* credible, not less: the alternative was quietly redefining 'full' and hoping nobody asked. You just asked — and the answer is in the notebook, dated."

**Q2. Why should anyone trust the test score?**
*Evidence: §7 (selection, cells 20–21), §10 (test-once + marker guard + bootstrap, cells 36–38), closing cell (56).*
"Because the test split could not influence anything. The winner was selected on the 105-row tune split alone; the test was then scored exactly once, by the frozen winner — and that's mechanical, not a promise: a marker file makes the scoring cell refuse to run a second time. The verdict is a paired bootstrap against the baseline's saved predictions on the same rows, so the confidence interval accounts for row difficulty."

**Q3. How did you prevent leakage?**
*Evidence: Research design cell (metadata row); closing cell (frozen rules); §5 (verifier rules); reconciliation record (exposure audit).*
"Three layers. First, the dataset's source metadata is never fed to the model — our audit showed a metadata-only rule scores 0.9150, which is the label leaking, not evidence. Second, we audited the split overlap itself: 9 validation rows connected to test by 14 hash edges, and those 14 test rows were excluded. Third, even the stream verifier's skips are integrity-only — a broken image is skipped, a hard image never is — so evaluation can't quietly drop the rows the model would miss."

**Q4. Why run both full fine-tuning and LoRA? Isn't LoRA the obvious choice at this size?**
*Evidence: Research design cell (RQ2, decisions table [4] [5]); §6 (cells 18–19); §8 (cells 29–33); §3.8 of this guide.*
"'Obvious' is an assumption, and RQ2 exists to measure it instead. The audit evidence says small-data adaptation is usually parameter-efficient and that full fine-tuning of a contrastive VLM can drift and degrade transfer — so we ran both, on identical data, losses, and step budgets, and let the tune split arbitrate. The grid has now answered: the full arm won the selection (0.7389), but LoRA's best was 0.7187 — a 0.020 gap on 105 items, inside noise. So the measured RQ2 answer is that at this scale the arms are barely separated, LoRA delivers winner-level performance at a fraction of the trainable parameters, and the choice that actually moved the score was the loss, not the arm."

**Q5. Why is VERITE only a transfer check? Why not train on it too?**
*Evidence: Research design cell (H3); §11 (cell 40); CONFIG (VERITE: eval-only, no train split).*
"Because a benchmark the model trained on stops measuring generalisation. VERITE contributes no training signal, so its score answers a question MMFakeBench can't: does the adaptation *travel*? H3's band is 0.38–0.48 against the 0.3566 baseline, deliberately wide — and we stay honest about the prior evidence: the frozen-probe transfer to VERITE was +4.37 points with an interval crossing zero, so transfer here was never a sure thing. The natural follow-up — why NewsCLIPpings *does* get a training arm — is Q8."

**Q6. What if training doesn't beat the baseline?**
*Evidence: Research design cell (H1 falsifier); §13 verdict.*
"Then H1 is rejected, the notebook prints that, and the study still stands — because the contribution was never only the training. The diagnostic audit (the collapse, the leakage ceiling, the calibration failure) is a complete finding on its own, and a pre-registered negative result is worth more than an unregistered positive one: it tells the next team exactly where the floor is. The framing was chosen in advance so that the paper is honest either way — that's what the falsifier column in the design cell is for. As it happened, the question is moot on the selection split — training beat the baseline 0.7389 to 0.259 — and the formal verdict waits on the single test scoring. [PENDING: test-once.]"

**Q7. The NewsCLIPpings images weren't even stored. Why believe those numbers?**
*Evidence: §5 (stream leg + verifier rules, cells 14–17); §11 PASS 2 (cell 41); §17 (stream accounting in the record bundle, cell 55).*
"Because not storing them is the documented method, not a gap in it. VisualNews ships as one 91 GB archive; the leg streams it in a single pass — every referenced image is verified by full decode before the model sees it, predictions are scored by the same study code as the disk-based legs, and the pass prints complete accounting per source: referenced, scored, skipped-with-reasons. Accuracy is computed over the scored rows and labelled as such. And before the notebook run, the streaming path was gated against the file-based path on identical items: maximum probability delta, 0.0."

**Q8. Why does NewsCLIPpings get its own training arm but VERITE doesn't?**
*Evidence: FREEZE PATCH banner (cell 22); §7a–§7c (cells 23–28); §11 (cells 40–41); Research design cell (H2 as amended by (c); H3).*
"Three reasons, all structural. First, *material*: NewsCLIPpings ships an official train split, so we could carve a clean protocol from it — train, tune, and calib that never touch its validation set. VERITE has no train split in this design at all; there is nothing legitimate to train it on. Second, *evidence*: NewsCLIPpings is where the prior evidence pointed — the frozen-feature probe gained +6.24 points there, and its zero-shot accuracy of 0.5083 left real headroom to win. Third, *protection*: VERITE is the study's one untouched witness. The moment it trains the model, H3 stops measuring whether the adaptation *travels* — and a transfer test you can train on isn't one. So NewsCLIPpings became a specialist, with its own weights in its own pack, judged against its own base-model number — and VERITE stayed the honest outsider."

---

## 6 · Showing it live — the five-minute demo

**Scroll order (the story in five stops):**
1. **Research design (cell 2)** — open on the predictions. "These were registered before the run." *(30 seconds)*
2. **One-page summary (cell 3)** — the three diagrams. Walk input → process → output with your finger. *(60 seconds)*
3. **Gates output (§3, cell 11)** — point at the two printed measurements: 0.00% skipped, round-trip identical. "Nothing trained until these passed." *(30 seconds)*
4. **The verdict (§13, cell 45)** — the H1–H5 block. Read the verdicts as they stand, met or not. *(60 seconds)*
   - **Optional stop — the pack switch (§7c, cell 28 → §11, cell 41):** if the audience is technical, show the NewsCLIPpings arm and PASS 2 side by side: MMFakeBench's winner never scores NewsCLIPpings; its own trained weights do, against the base model's PASS 1 number. *(30 seconds)* [PENDING until §11 executes]
5. **The three pictures (§14, cells 47–49)** — grid chart, then the recall chart (linger here: baseline's collapsed profile vs the winner's — this is the visual the audience will remember), then calibration. *(90 seconds)*
6. **Close on the Space** (browser tab) — run one before/after example live. *(30 seconds)*

**Safe to re-run live, if asked:** the §14 plot cells and §8's factor-isolation cells (they only *read* receipts and redraw — they cannot change any result); §17's record assembly (reads files, writes the bundle). The §3 gates can be re-run — they re-measure and print — but they reload the model, so give them a few seconds rather than narrating over a spinner.

**Safe *because* it refuses:** §10's test cell. If an examiner challenges "run it again, then," you can — the marker guard makes it print that the test was already scored and the recorded result stands. That refusal is one of the strongest credibility moments in the demo. Use it if the moment comes; don't burn time on it otherwise.

**Do NOT re-run live:** §6 (the grid — that *is* the training run; its receipts are the output, point at `runs/` instead), §5/§11 stream passes (a full pass over a 91 GB stream is not a demo action — point at the printed accounting), §12 calibration and §15 publish (both are marker-guarded one-way doors; re-running changes published state, and publish will announce itself via its marker).

**Have open in other tabs before you start:** the Hugging Face model page (`RafiulHaiderbro/laya-vision-fullft-mmfakebench`), the Space (`RafiulHaiderbro/laya-misinfo-demo`) with one example ready to submit, and the GitHub `finals/` folder (PPT-MIDTERM repo) — the status log, the verified baseline draft, and this notebook's staged copy live there if anyone wants the paper trail.

**If a number is challenged and you don't know:** say "that traces to a file — the closing cell names it," scroll to cell 56, and find it together. That move is on-brand for this project; guessing is not.

---

## 7 · Glossary — every term in one plain sentence

- **Typed decision** — the model answers a defined question by returning a probability for each allowed answer, instead of generating free text — which is what makes its answers exactly scoreable.
- **Choice question / noul question** — the two question forms asked of every record: *choice* asks "which of the dataset's classes is this?"; *noul* asks the binary question "would this be labelled Fake?" and returns one Fake probability.
- **Macro-F1** — the headline score for the 4-class task: each class's F1 (the balance of its precision and recall) computed separately, then averaged with equal weight — so a big class can't carry the score and a collapsed class can't hide.
- **Per-class recall** — for one class, the fraction of its true items the model actually found (e.g., original recall 1/300 = it found one of 300).
- **Paired bootstrap CI** — a confidence interval built by resampling the *same rows* both models answered, thousands of times, and re-scoring the difference each time; pairing removes row difficulty from the comparison, and the interval's lower bound must exclude zero for a gain to count as real.
- **Pre-registration** — writing the hypotheses, splits, and success rule down before running anything, so the criteria can't be edited to fit the outcome.
- **Fail-closed gate** — a check that stops the whole run when it fails (rather than warning and continuing), so a bad measurement can never flow silently into training.
- **LoRA** — Low-Rank Adaptation: training small plug-in correction matrices inside a frozen model instead of the model's own weights — far fewer trainable parameters, and the base model can't drift far.
- **Full fine-tuning (this study's FULL arm)** — training the model's own encoder and head weights directly (vision tower frozen, per amendment (b)) — the most capacity to change, and the most room to overfit small data.
- **rlcd vs soft_ce** — the two training losses: rlcd is LAYA's native objective (a proper-scoring-rule policy gradient over noised answers, plus soft cross-entropy); soft_ce is soft cross-entropy alone — the plain signal, run as the control so rlcd's extra term has a measured effect.
- **Step budget / epoch** — a step is one batch update (batch = 8 records here); an epoch is one full pass over the training set, so 245/490/735 steps ≈ 4/8/12 epochs over 490 items.
- **Temperature scaling** — post-hoc calibration: dividing the model's confidence scores by one fitted number (per question type) so its stated probabilities match its real accuracy — answers unchanged, confidence made honest.
- **ECE (expected calibration error)** — how far the model's confidence is from reality, on average: ECE 0.466 means its probabilities were badly miscalibrated; below 0.15 is this study's H5 target.
- **Leakage** — any path by which the answer reaches the model (or the evaluation) through a side channel instead of the evidence — here, source metadata that alone scores 0.9150.
- **Transfer** — scoring a trained model on a benchmark it never trained on, to test whether what it learned travels. In the final design VERITE is the pure transfer test; NewsCLIPpings' base-model stream score (PASS 1) is the transfer figure its own trained arm is reported against.
- **Dataset pack** — everything one dataset needs, kept separate from the others: its own choice and noul questions, label set, native metric, splits, calibration settings, and checkpoint pointer. The notebook loads a pack, evaluates, unloads — so one dataset's weights are never served for another by accident.
- **Head-only arm** — a supplementary configuration in which only the decision head trains and the entire encoder stays frozen — the in-model cousin of the October frozen-feature probe.
- **Supplementary ablation tier** — the 15 post-selection trainings (§7d) that vary one secondary factor at a time (head-only, adapter rank, learning rate, seed, data size) around the frozen winner; their receipts are quarantined in their own folder, so they can inform the paper but never re-open selection.
- **Tune / calib splits** — the two small held-out sets with separate jobs: *tune* (105) is the only data allowed to choose the winner; *calib* (105) is reserved until after selection and used only to fit calibration.

---

*Prepared 2026-11-22 from the staged notebook, and refreshed the same day against the final notebook (57 cells, §§0–17 plus the §7a–§7d post-selection patch sections), with the completed grid folded in from the run receipts. The [PENDING] slots — test-once, the NewsCLIPpings arm, both stream passes' accounting, calibration/H5, the supplementary table, and the cost ledger — fill in at run completion. Where the executed run's outputs differ from any expectation described here, the notebook is right and this guide is the thing to update.*
