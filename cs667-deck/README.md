# cs667-deck

The technical presentation for the CS 667 midterm, *Predicting Restaurant Inspection
Grades in New York City* (Rafiul Haider and Shadman Rahman, Fall 2026). It comes in two forms:

- **LiveDeck:** `index.html`, the reveal.js deck you present from. It has the animations,
  the mascot, the threshold slider and the 3D map.
- **StaticRecord:** `export/CS667_Technical_Presentation.pptx`, the graded file. Each slide
  is a full-size screenshot of the live deck, and the speaker notes are copied in.
  `export/CS667_Technical_Presentation_handout.pdf` is a printed handout, not the graded file.

## Presenting

```sh
cd cs667-deck
python3 -m http.server 8000
# open http://localhost:8000 in Chrome, full screen (F)
```

Everything is stored in this folder, so you can present with Wi-Fi off. The only part that
needs the network is **Go live** on slide 8, which loads the PyDeck map. If it doesn't load
within 4 seconds, the poster stays up and a recorded 10-second rotation plays instead.
Opening `index.html` directly (`file://`) also works, but Go live always uses the recording.

| Key | Action |
|---|---|
| → / Space / PageDown | next (finishes an entrance animation that is still running) |
| ← / PageUp | previous |
| Home / End | first / last slide |
| S | speaker view: notes, per-slide target times, timer |
| Esc | overview; when the slider or a button has focus, Esc returns the keys to the slides |
| R | reduced motion on/off (the footer button does the same) |

Slide 7 has two steps (one for each trap). Slide 9's reveal is one step: press → when the
pause has done its work.

**Rehearsal rule.** If the talk runs long in practice, cut slide 5 to one sentence and
slide 11's PCA half to one line. Never cut the pause on slide 9 or the drag on slide 13:
those are the two moments the talk is remembered by.

The split: Rafiul presents slides 1–9; Shadman steps in partway through slide 9 and presents
10–15. Slides 16–19 (B1–B4) are backups for Q&A.

## Where the numbers come from (INV-1)

No number in `index.html` was typed by hand. The flow is:

```
source/  notebook (executed) + modeling_table.csv + nta_risk_table.csv
   │  tools/export_deck_data.py   parse the notebook's printed outputs; re-fit the models
   ▼
data/*.json + data/deck-data.js   (data/MANIFEST.md: sources and checksums)
   │  tools/stamp_numbers.py      write every data-bind="…" value into index.html
   ▼
index.html                        charts are drawn in the browser from data/deck-data.js
```

- **The re-fit.** The notebook prints precision and recall for each threshold, but not the
  confusion counts or the curve points. The exporter re-fits the notebook's exact pipeline
  on `modeling_table.csv` and **stops if the result differs from any model number the
  notebook printed** (cells 58, 60, 62). It currently matches all of them: 4 models,
  6 threshold stops, and the coefficients.
- **The hero map's ZIP data** comes from the HTML the notebook embedded in cell 44.
- `data/FIXTURES.md` checks the exports against the numbers quoted in the build spec.

To re-export, which is a deliberate step that should show up in the git diff:

```sh
python3 tools/extract_notebook_assets.py   # figures + HTML maps out of the notebook
python3 tools/export_deck_data.py          # data/*.json, MANIFEST.md, FIXTURES.md
python3 tools/stamp_numbers.py             # numbers into index.html
python3 tools/inline_mascot.py             # only if src/assets-src/mascot.svg changed
```

### Still open

| What | Why | Where it shows |
|---|---|---|
| 8,456 same-day restaurant pairs | only stated in a markdown cell; no cell prints it | slide 3 notes |
| 41.8% / 37.1% scored 14+ (first visits / re-inspections) | cell 13.5's output was saved as "Output hidden" | slide 9 toggle, notes |
| 99.6% ZIP boundary match | cell 13.4's output was saved as "Output hidden" | slide 8 notes, B4 |
| RF 0.640 / GB 0.637 / 3,281 in the spec | the notebook says **0.641 / 0.636 / 3,284**; the deck shows the notebook's values | slides 12, 13 |

Until the first three are exported, the deck shows a red "awaiting export" label in their
place, and `qa_check.py` fails. To fill them in, run `tools/notebook_export_cell.py` as the
last cell of the notebook in Colab. The cell refuses to run unless the file it downloads is
still the October 21, 2026 file. Upload the `deck_exports.json` it writes to `source/`, then
run the re-export commands above.

## Building the StaticRecord

```sh
cd cs667-deck/tools && npm install && cd ..   # build-time only: Playwright and deck.gl
node tools/capture_slides.mjs --pdf           # 1920x1080 screenshots of ?export=1 + notes + PDF
python3 tools/build_pptx.py                   # .pptx; asserts screenshots == slides == notes
python3 tools/qa_check.py                     # the Part 10 gates
```

Export mode (`?export=1`) turns animation off and shows every interactive slide after its
interaction. The trap card is flipped, slide 9 is revealed with both states printed beneath,
and both traps on slide 7 are ringed. Grady holds idle with an A.
`node tools/capture_hero.mjs` re-renders the hero posters and the rotation video from
`data/maps.json` with a local deck.gl, so it works offline.

## Layout

```
index.html              the deck: 19 <section>s with speaker notes
src/css/                theme (palette, type, furniture) · deck (layout) · animations · mascot
src/js/                 deck (reveal setup) · data-loader (charts) · animations · interactions
                        · mascot · format (number formats and data lookups)
src/assets-src/         mascot.svg, the layered source of Grady
data/                   DataExports, generated; do not edit
assets/                 fonts (Inter 400/700), notebook figures, posters, rotation video,
                        the hero map's HTML (the live extra)
source/                 the executed notebook and its saved tables (the source of truth)
tools/                  export, stamp, capture, pptx, QA
vendor/reveal.js/       reveal.js 5.2.1 and its notes plugin
export/                 the StaticRecord and the handout
```

## Decisions to know about

- **Hero poster and rotation video.** These are rendered from the notebook's own ColumnLayer
  data and settings (heights, colours, radius) with a local deck.gl. The original HTML
  loads its basemap and deck.gl from CDNs that this build environment can't reach, so the
  poster has no street map underneath. The camera is closer than the notebook's zoom 10,
  where the columns stand only a few pixels tall.
- **Slide 8's flat panel.** It is a dot map of ZIP centroids, not a filled-polygon map: the
  ZIP polygons were never saved, and the uploaded copy of `map_risk_zip.html` stops at 1 MB.
  When `deck_exports.json` supplies the polygons, the data is ready for a filled map.
- **The 3D score scatter is not used.** It encodes the score as height, which breaks INV-4.
  The 10 MB hexagon map is not linked from the deck at all.
- **Cuisine B-or-C shares (slide 6 explorer)** are computed over the modeled inspections
  (graded, first visits excluded). That's the population the notebook saved, and the label
  on the slide says so.
- **Slide 9's reveal** happens when the presenter advances, never on a timer, so the
  scripted pause stays in the presenter's hands.
