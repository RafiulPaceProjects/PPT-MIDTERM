# Paper versioning protocol

The paper lives in git and improves in versions. A version is not a
save point — it is a gated, snapshotted, tagged release of the draft.
This file is the protocol; `CHANGELOG.md` is the record.

## Layout

```
finals/paper/
  draft/            the living draft (paper.tex, bibliography.bib,
                    figures/, plus the style files it builds with)
  versions/vX.Y/    immutable snapshot of one cut version
                    (paper.tex + built paper.pdf; v0.0 also keeps its
                    original references.bib)
  tools/            verify_draft.py (the gate) and
                    verified_numbers.json (the number allowlist)
  CHANGELOG.md      what changed in every version, and on whose evidence
  VERSIONING.md     this file
```

## Version scheme

| Version | Meaning |
|---|---|
| `v0.0` | The PaperOrchestra baseline draft, archived unchanged. Covers only the October diagnosis half of the study. |
| `v0.1` | Tonight's complete-record draft: the full study (diagnosis + main run) rewritten from the finalised results bundle. |
| patch (`v0.1.1`, `v0.1.2`, …) | **Wording-only** passes: phrasing, clarity, structure. No new numbers, no new claims. |
| minor (`v0.2`, `v0.3`, …) | **Added information, features, or sections**: new results, new analyses, new citations, new figures. |
| `v1.0` | Submission-ready: delivery gate green, all known flags closed, byline and bibliography final. |

## The rules

1. **A version exists only when the gate passes.** Run
   `python3 finals/paper/tools/verify_draft.py` — it must exit 0
   (warnings are allowed and must be read; failures are not). The gate
   checks: every citation key resolves in `bibliography.bib`; every
   numeric literal in the draft appears in
   `tools/verified_numbers.json`; no template placeholders survive.
2. **Every new number needs a source before it needs a sentence.** To
   print a number that the gate rejects, first add it to
   `verified_numbers.json` with the bundle, audit, or scout file that
   authorises it. An allowlist entry with no source fails the gate
   itself. Units convention lives in that file's header — LAYA metrics
   are proportions, competitor Protocol-A values are percentages as
   published; never mix them unlabelled.
3. **Cutting a version** (after the gate passes and the PDF builds):
   - copy `draft/paper.tex` and the built `draft/paper.pdf` into
     `versions/vX.Y/` — snapshots are immutable once committed;
   - add the `CHANGELOG.md` entry (below);
   - commit, then tag the commit `paper-vX.Y.Z` (full three-part tag:
     `v0.1` is tagged `paper-v0.1.0`) and push the tag. The
     `paper-v*` tag triggers the release workflow, which attaches the
     built PDF to a GitHub release.
4. **CHANGELOG discipline.** Every version gets an entry recording:
   what changed, classified as **wording** / **information** /
   **features**; and, for any new number, figure, or claim, the bundle
   or audit file that authorises it (e.g. `final_results_bundle.json`,
   `CALIBRATION_FINDING_2026-11-22.md`). "Improved the text" is not an
   entry; name the sections and the evidence.
5. **The living draft is the only file that changes.** Snapshots under
   `versions/` are never edited. If a snapshot is wrong, the fix is a
   new version and a CHANGELOG line saying so — the record of what was
   believed when is part of the study's evidence.

## The exact commands

```bash
# gate + build the living draft
python3 finals/paper/tools/verify_draft.py
cd finals/paper/draft && pdflatex paper.tex && bibtex paper \
  && pdflatex paper.tex && pdflatex paper.tex && cd ../../..

# snapshot, changelog, commit, tag, push (example: v0.2)
mkdir -p finals/paper/versions/v0.2
cp finals/paper/draft/paper.tex finals/paper/versions/v0.2/paper.tex
cp finals/paper/draft/paper.pdf finals/paper/versions/v0.2/paper.pdf
# ... write the CHANGELOG.md entry for v0.2 ...
git add finals/paper && git commit -m "Paper v0.2: <what changed>"
git tag paper-v0.2.0
git push origin main --tags
```
