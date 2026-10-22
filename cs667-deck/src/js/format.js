/* Data access and number formats, the same rules as tools/deckdata.py.
   Everything the deck shows live (charts, the slider) goes through these. */
(function () {
  "use strict";
  const ID_FIELDS = ["threshold", "model", "boro", "cuisine", "feature", "zip", "nta", "column", "grade", "component"];
  const WORDS = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"];

  function same(value, key) {
    if (typeof value === "number") return Number(key) === value;
    return String(value) === key;
  }

  /** Resolve "tables.models[Random forest].test_roc_auc" against DECK_DATA. */
  function get(path) {
    let cur = window.DECK_DATA;
    const steps = path.match(/[^.[\]]+|\[[^\]]+\]/g) || [];
    for (const step of steps) {
      if (cur == null) return undefined;
      if (step[0] !== "[") { cur = cur[step]; continue; }
      const key = step.slice(1, -1);
      if (Array.isArray(cur) && cur.length && typeof cur[0] === "object" && !Array.isArray(cur[0])) {
        const field = ID_FIELDS.find((f) => f in cur[0]);
        cur = cur.find((d) => same(d[field], key));
      } else {
        cur = cur[Number(key)];
      }
    }
    return cur;
  }

  /** Half-up rounding on the shortest decimal form, like Python's Decimal(repr(v)). */
  function round(v, n) {
    const r = Number(Math.round(Number(Math.abs(v) + "e" + n)) + "e-" + n);
    return (v < 0 ? -r : r).toFixed(n);
  }
  const signed = (s) => s.replace("-", "−");

  function fmt(value, kind) {
    switch (kind) {
      case "str": return String(value);
      case "int": return Number(round(value, 0)).toLocaleString("en-US");
      case "num0": return signed(round(value, 0));
      case "num1": return signed(round(value, 1));
      case "pct0": return round(value, 0) + "%";
      case "pct1": return round(value, 1) + "%";
      case "dec2": return signed(round(value, 2));
      case "dec3": return signed(round(value, 3));
      case "dec4": return signed(round(value, 4));
      case "frac_pct1": return round(100 * value, 1) + "%";
      case "per100": return round(100 * value, 0);
      case "inv_tenths": return round(10 * (1 - value), 0);
      case "inv_tenths_word": return WORDS[Number(round(10 * (1 - value), 0))];
      case "thr": return String(Number(Number(value).toFixed(2)));
      default: throw new Error("unknown format " + kind);
    }
  }

  /** The B-or-C ramp, pale at 0% to deep red at clip% (the notebook's cell 44
      ramp); its two ends are the theme's --scale-pale and --scale-deep. */
  let ends = null;
  const rgb = (hex) => [1, 3, 5].map((i) => parseInt(hex.trim().slice(i, i + 2), 16));
  function rampColor(pct, clip) {
    if (!ends) {
      const css = getComputedStyle(document.documentElement);
      ends = [rgb(css.getPropertyValue("--scale-pale")), rgb(css.getPropertyValue("--scale-deep"))];
    }
    const [pale, deep] = ends;
    const t = Math.max(0, Math.min(pct, clip)) / clip;
    const c = pale.map((p, i) => Math.round(p + t * (deep[i] - p)));
    return `rgb(${c[0]}, ${c[1]}, ${c[2]})`;
  }

  /** Grade a score would earn: A 0-13, B 14-27, C 28+. */
  const gradeOf = (score) => (score <= 13 ? "A" : score <= 27 ? "B" : "C");

  window.DeckFormat = { get, fmt, rampColor, gradeOf };
})();
