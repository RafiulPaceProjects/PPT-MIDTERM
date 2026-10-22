"""The Part 10 gates, automated where they can be.

  python3 tools/qa_check.py            static gates + browser gates
  python3 tools/qa_check.py --static   static gates only (fast)

Exit status 0 only when every gate passes. Pending values (numbers the
notebook never printed) fail the numbers gate on purpose: INV-1 keeps them
off the slides until they are exported.
"""
import html
import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path

from deckdata import MISSING, ROOT, fmt, load, resolve

INDEX = ROOT / "index.html"
results = []


def gate(name, ok, detail=""):
    results.append((name, bool(ok), detail))


def sections(text):
    return re.findall(r"(<section\b[^>]*>)(.*?)</section>", text, re.S)


def visible_text(body, drop_bound=True):
    body = re.sub(r'<aside class="notes">.*?</aside>', " ", body, flags=re.S)
    if drop_bound:   # stamped tables: checked by the re-stamp gate instead
        body = re.sub(r'<table[^>]*\sdata-table="[^"]+"[^>]*>.*?</table>', " ", body, flags=re.S)
    return plain(body, drop_bound)


def plain(fragment, drop_bound=True):
    if drop_bound:
        fragment = re.sub(r'<(\w+)[^<>]*\sdata-bind="[^"]+"[^<>]*>[^<]*</\1>', " ", fragment)
    fragment = re.sub(r"<[^>]+>", " ", fragment)
    return re.sub(r"\s+", " ", html.unescape(fragment)).strip()


def attr(tag, name):
    m = re.search(rf'\s{name}="([^"]*)"', tag)
    return m.group(1) if m else None


# numbers a slide may carry without a DataExport: calendar, course, labels, rules
ALLOWED = [
    r"\b20(?:07|24|25|26)\b", r"\b(?:Oct(?:ober)?\.?) \d{1,2}(?:\s*[–-]\s*\d{1,2})?(?:, )?",
    r"(?i)\bslides? \d{1,2}(?: to \d{1,2})?\b", r"\bMoment [1-3]\b", r"\bF1\b", r"\b0–", r"\b0%", r"\b5(?::00)? PM\b",
    r"\bCS 667\b", r"\bFall 2026\b", r"\bAct [IVX]+\b", r"\bB[1-4]\b", r"\bSprint [12]\b", r"\bTrap [12]\b",
    r"\bPC[12]\b", r"\b43nn-pn8j\b", r"\b14\+", r"\b0–\b", r"\b(?:80|90)%", r"\bof every 100\b", r"\bin 10\b",
    r"= [01]\b", r"\(\d\)", r"\b\d{1,2}:\d{2}\b", r"\b\d+ seconds?\b", r"\b10-second\b", r"\b3D\b", r"\b[1-3]\b(?=\s*[A-Z][a-z])",
    r"\bslides? \d{1,2}(?: to \d{1,2})?\b", r"\bslide \d+\b", r"\b1–9\b", r"\b10–15\b", r"\bpred_confusion\.png\b",
    r"\b5\s*PM\b", r"\bOct 13\b", r"\bOct 2[0-7]\b",
]


def untagged_numbers(text):
    for pat in ALLOWED:
        text = re.sub(pat, " ", text)
    return re.findall(r"\d[\d,.]*%?", text)


def main():
    static_only = "--static" in sys.argv
    text = INDEX.read_text()
    data = load()
    secs = sections(text)

    # ---- numbers & provenance --------------------------------------------
    r = subprocess.run([sys.executable, str(ROOT / "tools/export_deck_data.py"), "--check"],
                       capture_output=True, text=True)
    try:
        rep = json.loads(r.stdout.strip().splitlines()[-1])
    except Exception:
        rep = {"stale": ["?"], "bundle_ok": False, "fixture_failures": [r.stderr[-300:]], "pending": []}
    gate("exports are frozen: data/*.json equal a fresh build from the notebook", not rep["stale"], ", ".join(rep["stale"]))
    gate("deck-data.js carries exactly data/*.json", rep["bundle_ok"])
    gate("fixture values (Part 7) match the notebook", not rep["fixture_failures"],
         "; ".join(f"{f['path']}: spec {f['spec']}, notebook {f['export']}" for f in rep["fixture_failures"]))

    bound = re.findall(r'<(\w+)([^<>]*\sdata-bind="([^"]+)"[^<>]*)>([^<]*)</\1>', text)
    wrong, pending = [], []
    for _, attrs, path, body in bound:
        kind = attr(attrs, "data-fmt")
        value = resolve(data, path)
        if value is MISSING:
            wrong.append(f"{path}: not in the exports")
        elif value is None:
            pending.append(path)
        elif html.unescape(body) != fmt(value, kind):
            wrong.append(f"{path}: shows {body!r}, export says {fmt(value, kind)!r}")
    gate(f"every bound number equals its export ({len(bound)} bindings)", not wrong, "; ".join(wrong[:5]))
    gate("no value awaiting export (INV-1)", not pending, ", ".join(sorted(set(pending))))
    from stamp_numbers import stamp
    restamped, problems = stamp(text, data)
    gate("the stamp is current: re-stamping index.html changes nothing", restamped == text and not problems,
         "; ".join(problems[:3]) or "run tools/stamp_numbers.py")
    gate("every data-bind is stamped (none nested or skipped)", len(bound) == text.count("data-bind="),
         f"{len(bound)} of {text.count('data-bind=')}")

    stray = []
    for open_tag, body in secs:
        sid = attr(open_tag, "id")
        notes = re.search(r'<aside class="notes">(.*?)</aside>', body, re.S)
        for where, chunk in (("slide", visible_text(body)), ("notes", plain(notes.group(1)) if notes else "")):
            nums = untagged_numbers(chunk)
            if nums:
                stray.append(f"{sid} {where}: {', '.join(nums[:6])}")
    gate("no hand-typed numbers outside data-bind (slides and notes)", not stray, " | ".join(stray[:8]))

    asof = data["key_metrics"]["as_of_text"]
    missing_asof = [attr(t, "id") for t, b in secs
                    if attr(t, "data-slide-type") in ("chart", "map", "model-results", "discovery", "closing", "title")
                    and f"Data as of {asof}" not in visible_text(b, drop_bound=False)]
    gate("'Data as of October 21, 2026' on every data slide (INV-10)", not missing_asof, ", ".join(missing_asof))

    # ---- colour & labelling -----------------------------------------------
    grade_hex = re.compile(r"#(?:2E7D32|E69F00|C0392B)\b", re.I)
    offenders = []
    for f in list((ROOT / "src").rglob("*.*")) + [INDEX]:
        if f.suffix in (".css", ".js", ".html", ".svg"):
            for m in grade_hex.finditer(f.read_text()):
                if f.name != "theme.css":
                    offenders.append(f"{f.relative_to(ROOT)}: {m.group(0)}")
    theme = (ROOT / "src/css/theme.css").read_text()
    defs = all(re.search(rf"--grade-{g}:\s*{h};", theme) for g, h in (("a", "#2E7D32"), ("b", "#E69F00"), ("c", "#C0392B")))
    gate("grade colours defined once, as CSS variables in theme.css (INV-2)", defs and not offenders, ", ".join(offenders[:5]))
    lib = [attr(t, "id") for t, b in secs if "data-score-visual" in t and "lower is better" not in visible_text(b, False).lower()]
    gate("'lower is better' on every score visual (INV-3)", not lib, ", ".join(lib))
    gate("unreliable regions are greyed with the words 'not enough inspections to judge' (INV-5)",
         "not enough inspections to judge" in text and "--unreliable" in theme)

    # ---- offline -----------------------------------------------------------
    gate("the 10 MB hex map is not referenced by index.html (INV-6)", "nyc_hex_3d" not in text)
    ext = [u for u in re.findall(r'(?:src|href)="(https?://[^"]+)"', text)]
    src_ext = [f"{p.name}: {u}" for p in (ROOT / "src").rglob("*.*") if p.suffix in (".css", ".js")
               for m in re.findall(r"""url\(["']?(https?://[^)"']+)|["'](https?://[^"']+)["']""", p.read_text())
               for u in m if u and not u.startswith("http://www.w3.org/")]
    gate("no network URLs in the deck's HTML, CSS or JS", not ext and not src_ext, ", ".join(ext + [str(s) for s in src_ext])[:300])
    gate("fonts are vendored woff2, weights 400 and 700 only",
         all((ROOT / f"assets/fonts/inter-latin-{w}-normal.woff2").exists() for w in (400, 700))
         and "fonts.googleapis" not in text + theme)

    # ---- slides, notes, timing, speakers -----------------------------------
    no_notes = [attr(t, "id") for t, b in secs if not re.search(r'<aside class="notes">\s*<p>', b)]
    gate("speaker notes exist for every slide", not no_notes, ", ".join(no_notes))
    claims = [attr(t, "id") for t, b in secs if len(re.findall(r"<h[12]\b", b)) != 1]
    gate("exactly one claim (title) per slide (INV-9)", not claims, ", ".join(claims))
    main15 = [(t, b) for t, b in secs if "backup" not in (attr(t, "class") or "")]
    gate("15 content slides + 4 backups", len(main15) == 15 and len(secs) == 19, f"{len(main15)} + {len(secs) - len(main15)}")
    total = sum(int(attr(t, "data-timing") or 0) for t, _ in main15)
    gate("per-slide target times sum to 14:00", total == 840, f"{total // 60}:{total % 60:02d}")
    timed = [attr(t, "id") for t, b in main15 if not re.search(r"Target: \d+:\d\d", b)]
    gate("per-slide target times in the notes", not timed, ", ".join(timed))
    raf = sum(1 for t, _ in main15 if attr(t, "data-speaker").startswith("Rafiul"))
    sha = sum(1 for t, _ in main15 if attr(t, "data-speaker").startswith("Shadman"))
    gate("each presenter has at least 4 slides", raf >= 4 and sha >= 4, f"Rafiul {raf}, Shadman {sha}")
    interactive = [attr(t, "id") for t, b in secs if "data-interactive" in b
                   and not re.search(r"static record", re.search(r'<aside class="notes">(.*?)</aside>', b, re.S).group(1), re.I)]
    closing = next(b for t, b in secs if attr(t, "id") == "close")
    gate("static-record note on every interactive slide and on the closing slide (INV-11)",
         not interactive and "static record" in visible_text(closing, False), ", ".join(interactive))
    forced = [attr(t, "id") for t, b in secs if t.count('data-mascot-force="true"') > 1]
    gate("at most one forced mascot cue per slide", not forced)
    mascot_src = (ROOT / "src/assets-src/mascot.svg").read_text().strip()
    gate("the inline mascot equals src/assets-src/mascot.svg", mascot_src in text)
    gate("no business deck files, routes or stubs (Part 11)",
         not any(p for p in ROOT.rglob("*business*") if "node_modules" not in p.parts) and "business.html" not in text)

    # ---- export --------------------------------------------------------------
    pptx = ROOT / "export/CS667_Technical_Presentation.pptx"
    shots = sorted((ROOT / "export/slides").glob("slide-*.png"))
    if pptx.exists():
        with zipfile.ZipFile(pptx) as z:
            names = z.namelist()
            n_slides = len([n for n in names if re.fullmatch(r"ppt/slides/slide\d+\.xml", n)])
            n_notes = len([n for n in names if re.fullmatch(r"ppt/notesSlides/notesSlide\d+\.xml", n)])
            notes_text = " ".join(z.read(n).decode("utf8") for n in names if n.startswith("ppt/notesSlides/notesSlide"))
        gate("screenshots == slides == .pptx slides == notes", len(shots) == len(secs) == n_slides == n_notes,
             f"{len(shots)} shots, {len(secs)} slides, {n_slides} pptx slides, {n_notes} notes")
        gate("the .pptx notes carry the static-record disclaimer", "static record" in notes_text)
        gate("PDF backup generated", (ROOT / "export/CS667_Technical_Presentation_handout.pdf").exists())
    else:
        gate("StaticRecord .pptx built", False, "run tools/capture_slides.mjs then tools/build_pptx.py")

    # ---- browser gates ---------------------------------------------------------
    if not static_only:
        r = subprocess.run(["node", str(ROOT / "tools/qa_browser.mjs")], capture_output=True, text=True, cwd=ROOT)
        try:
            for g in json.loads(r.stdout.strip().splitlines()[-1]):
                gate("browser: " + g["gate"], g["ok"], g["detail"])
        except Exception:
            gate("browser gates ran", False, (r.stderr or r.stdout)[-400:])

    width = max(len(n) for n, _, _ in results)
    failed = 0
    for name, ok, detail in results:
        failed += not ok
        print(f"{'PASS' if ok else 'FAIL'}  {name.ljust(width)}  {'' if ok else detail}")
    print(f"\n{len(results) - failed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
