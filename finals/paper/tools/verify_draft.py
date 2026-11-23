#!/usr/bin/env python3
"""CI gate for the LAYA study living draft.

Checks finals/paper/draft/paper.tex (+ bibliography.bib) before any
version may be cut. Run locally or from .github/workflows/paper.yml:

    python3 finals/paper/tools/verify_draft.py

Exit codes: 0 = gate passes (warnings allowed), 1 = gate fails,
2 = the gate itself could not run (missing/unreadable input).

Checks
------
(a) Citations: every \\cite... key in paper.tex resolves to an entry in
    bibliography.bib.
(b) Number tracing: every numeric literal in the body of paper.tex must
    appear in tools/verified_numbers.json, where each entry carries the
    source that authorises it. An unmatched number FAILS the gate and is
    listed with its line number. Allowlist entries with no source also
    fail -- an unsourced allowlist entry is how numbers sneak in.
(c) Placeholder scan: template leftovers fail the gate.
(d) Section 4.6 warning (NOT a failure): the baseline draft's known
    regime mix-up prints GPT-4V Standard validation macro-F1 (51.0)
    beside the LLaVA MMD-Agent figure (49.9) with no protocol labels.
    The pattern is detected and warned about so the v0.1 rewrite fixes
    it deliberately instead of the gate silently blessing it.
"""

import argparse
import json
import re
import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
DRAFT_DIR = TOOLS_DIR.parent / "draft"

# Commands whose brace arguments are metadata, not prose: numbers inside
# them (citation years, file names like iclr2025_conference) are not
# claims and are excluded from number tracing.
STRIP_COMMANDS = (
    "cite", "citep", "citet", "citealp", "citeauthor", "citeyear",
    "ref", "eqref", "autoref", "label", "usepackage", "documentclass",
    "bibliographystyle", "bibliography", "input", "include",
    "includegraphics", "url", "href", "hypersetup",
)

PLACEHOLDERS = (
    "[PENDING]",
    "TODO",
    "TBD",
    "lorem",
    "Author Placeholder",
    # The baseline draft's actual template author block (v0.0). Catching
    # the real strings, not just the generic token, is the point.
    "Ambitious AI Researcher",
    "AI Research Institute",
    "researcher@institute.ai",
)

NUMBER_RE = re.compile(r"\d[\d,]*(?:\.\d+)?")
CITE_RE = re.compile(r"\\cite\w*\*?(?:\[[^\]]*\])?\{([^}]*)\}")
BIB_KEY_RE = re.compile(r"@\w+\s*\{\s*([^,\s]+)\s*,")


def strip_comment(line: str) -> str:
    """Remove a LaTeX comment (unescaped %) from one line."""
    out = []
    i = 0
    while i < len(line):
        ch = line[i]
        if ch == "%" and (i == 0 or line[i - 1] != "\\"):
            break
        out.append(ch)
        i += 1
    return "".join(out)


def strip_command_args(line: str) -> str:
    """Blank out the brace arguments of STRIP_COMMANDS on one line."""
    for cmd in STRIP_COMMANDS:
        pattern = re.compile(r"\\" + cmd + r"\*?\s*(?:\[[^\]]*\])?\s*\{")
        start = 0
        while True:
            m = pattern.search(line, start)
            if not m:
                break
            depth = 1
            j = m.end()
            while j < len(line) and depth:
                if line[j] == "{":
                    depth += 1
                elif line[j] == "}":
                    depth -= 1
                j += 1
            line = line[: m.start()] + " " + line[j:]
            start = m.start() + 1
    return line


def load_allowlist(path: Path):
    """Return (set of floats, list of problems)."""
    data = json.loads(path.read_text(encoding="utf-8"))
    allowed = set()
    problems = []
    for idx, entry in enumerate(data.get("numbers", [])):
        raw = entry.get("value")
        source = (entry.get("source") or "").strip()
        if raw is None:
            problems.append(f"allowlist entry #{idx} has no value")
            continue
        if not source:
            problems.append(f"allowlist entry {raw!r} has NO SOURCE -- not allowed")
            continue
        try:
            allowed.add(float(str(raw).replace(",", "")))
        except ValueError:
            problems.append(f"allowlist entry {raw!r} is not numeric")
    return allowed, problems


def main() -> int:
    ap = argparse.ArgumentParser(description="Verify the LAYA living draft.")
    ap.add_argument("--tex", default=str(DRAFT_DIR / "paper.tex"))
    ap.add_argument("--bib", default=str(DRAFT_DIR / "bibliography.bib"))
    ap.add_argument("--allowlist", default=str(TOOLS_DIR / "verified_numbers.json"))
    args = ap.parse_args()

    tex_path, bib_path, allow_path = Path(args.tex), Path(args.bib), Path(args.allowlist)
    for p in (tex_path, bib_path, allow_path):
        if not p.is_file():
            print(f"GATE ERROR: required file not found: {p}")
            return 2

    tex_lines = tex_path.read_text(encoding="utf-8").splitlines()
    bib_text = bib_path.read_text(encoding="utf-8")

    failures: list[str] = []
    warnings: list[str] = []

    # ---- (a) citations -------------------------------------------------
    bib_keys = set(BIB_KEY_RE.findall(bib_text))
    cited: dict[str, int] = {}
    for lineno, raw in enumerate(tex_lines, 1):
        for m in CITE_RE.finditer(raw):
            for key in m.group(1).split(","):
                cited.setdefault(key.strip(), lineno)
    unresolved = {k: ln for k, ln in cited.items() if k not in bib_keys}
    if unresolved:
        for key, ln in sorted(unresolved.items()):
            failures.append(f"citation: \\cite key '{key}' (line {ln}) has no entry in bibliography.bib")
    print(f"[citations] {len(cited)} cited key(s), {len(bib_keys)} bib entr(ies) "
          f"-> {'OK' if not unresolved else 'FAIL'}")

    # ---- allowlist integrity -------------------------------------------
    allowed, allow_problems = load_allowlist(allow_path)
    for prob in allow_problems:
        failures.append(f"allowlist: {prob}")
    print(f"[allowlist] {len(allowed)} verified number(s) loaded"
          f"{'' if not allow_problems else f', {len(allow_problems)} problem(s)'}")

    # ---- (b) number tracing + (c) placeholder scan ----------------------
    unmatched: dict[float, list[int]] = {}
    number_count = 0
    body_lines: list[str] = []
    for lineno, raw in enumerate(tex_lines, 1):
        body = strip_command_args(strip_comment(raw))
        body_lines.append(body)
        for token in PLACEHOLDERS:
            if token.lower() in body.lower():
                failures.append(f"placeholder: '{token}' found at line {lineno}")
        for m in NUMBER_RE.finditer(body):
            number_count += 1
            try:
                value = float(m.group(0).replace(",", ""))
            except ValueError:
                continue
            if not any(abs(value - a) < 1e-9 for a in allowed):
                unmatched.setdefault(value, []).append(lineno)
    if unmatched:
        for value, lines in sorted(unmatched.items()):
            shown = ", ".join(str(x) for x in lines[:5])
            failures.append(
                f"number tracing: {value:g} (lines {shown}) is not in verified_numbers.json "
                "-- add it WITH its source, or fix the draft"
            )
    print(f"[numbers] {number_count} numeric literal(s) traced "
          f"-> {'OK' if not unmatched else f'FAIL ({len(unmatched)} unverified)'}")

    # ---- (d) section 4.6 regime-mix warning ------------------------------
    # The known baseline error: "51.0 and 49.9" printed as a pair with no
    # regime labels. Warning only -- v0.0 legitimately contains it and the
    # fix belongs to the v0.1 rewrite, not to a silent gate failure.
    body_text = "\n".join(body_lines)
    for m in re.finditer(r"51\.0", body_text):
        window = body_text[max(0, m.start() - 500): m.end() + 500]
        if "49.9" in window and "Standard" not in window and "MMD-Agent" not in window:
            warnings.append(
                "section 4.6 pattern: GPT-4V 51.0 appears beside LLaVA 49.9 with no "
                "protocol/regime labels in the surrounding text -- this is the known "
                "baseline regime mix-up (51.0 is Standard; 49.9 is MMD-Agent; LLaVA "
                "Standard is 25.7). The v0.1 rewrite must label regimes."
            )
            break
    if warnings:
        print(f"[warnings] {len(warnings)}")
    else:
        print("[warnings] 0")

    # ---- report ----------------------------------------------------------
    print("=" * 70)
    for w in warnings:
        print(f"WARNING: {w}")
    if failures:
        for f in failures:
            print(f"FAIL: {f}")
        print(f"GATE: FAIL ({len(failures)} failure(s), {len(warnings)} warning(s))")
        return 1
    print(f"GATE: PASS ({len(warnings)} warning(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
