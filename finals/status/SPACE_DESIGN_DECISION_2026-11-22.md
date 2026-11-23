# HF Space — design decision (Rafiul, 2026-11-22 ~18:21–18:22 ET)

Rafiul's directives, in his words:
- "The app will run on changing the weights according to the datasets"
- "I want a visual way where users can see input processing and output results clearly"
- "Can also see the images" — "That is going in"

## Settled spec (app v2, built same evening in ~/workspace/misinfo_run/hf_space/)
- Per-dataset pack registry inside the Space, mirroring the notebook's runs/packs.json: each pack = native labels, two questions VERBATIM, fake threshold, AFTER checkpoint repo. Datasets served: MMFakeBench + NewsCLIPpings (VERITE stays eval-only, Results tab only).
- Selecting a dataset switches questions + labels + loaded weights together; a "Now serving" line states dataset, metric, both checkpoint repos, threshold.
- Three-stage visual layout: 1 · INPUT (image + caption; the image stays on screen with the result; per-dataset one-click examples with visible thumbnails) → 2 · PROCESSING (the pack's two questions shown verbatim + the arbitration rule) → 3 · OUTPUT (BEFORE | AFTER columns: class-probability bars, fake-screen readout, verdict, "uncertain" badge on choice/noul disagreement, flip callout when training changes the verdict).
- Weights are the study's own: BEFORE = thaitea/laya-vision @ f2fe3c1 (pinned); AFTER per dataset = RafiulHaiderbro/laya-vision-fullft-mmfakebench / -newsclippings. Lazy-load + cache per (pack, slot); AFTER probabilities temperature-adjusted when results.json carries the fitted choice temperature.
- Numbers as data: scoreboard + AFTER table render from results.json (publish writes it from final_results_bundle.json); fail-soft "pending" states, never invented numbers.
- This supersedes the earlier open widget questions (NCP-in-Space: YES by this directive; rebuild: DONE as v2).

## Publish-stage duties (updated)
- Push BOTH winner repos (MMF + NCP) before/with the Space.
- results.json: scoreboard_md + after_md + temperatures per pack.
- Examples per dataset under examples/<pack>/: MMF = 4 VAL items, one per gold class, true captions; NCP = items from its saved tune/carve files, labelled as such. VAL/tune only, never test.
- Smoke check: boot + one live predict per pack on an example.
