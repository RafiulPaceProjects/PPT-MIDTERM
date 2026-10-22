/* Renders the native charts from window.DECK_DATA (data/deck-data.js, the
   same content as data/*.json). No chart library: plain SVG and HTML.
   Each chart's numbers come from the exports; each keeps its text in the
   DOM (value labels, hidden tables) so the data is readable as text. */
(function () {
  "use strict";
  const { get, fmt, rampColor, gradeOf } = window.DeckFormat;
  const NS = "http://www.w3.org/2000/svg";
  const GRADE = { A: "var(--grade-a)", B: "var(--grade-b)", C: "var(--grade-c)" };

  function el(tag, attrs = {}, parent) {
    const node = document.createElementNS(NS, tag);
    for (const [k, v] of Object.entries(attrs)) if (v != null) node.setAttribute(k, v);
    if (parent) parent.appendChild(node);
    return node;
  }
  // fill and font settings go inline: the theme's `.chart svg text` rule
  // would otherwise beat SVG presentation attributes
  const STYLE = { fill: "fill", "font-size": "font-size", "font-weight": "font-weight" };
  function text(parent, x, y, str, attrs = {}) {
    const style = [];
    const rest = {};
    for (const [k, v] of Object.entries(attrs)) {
      if (k in STYLE && v != null) style.push(`${STYLE[k]}:${typeof v === "number" && k === "font-size" ? v + "px" : v}`);
      else rest[k] = v;
    }
    if (style.length) rest.style = (rest.style ? rest.style + ";" : "") + style.join(";");
    const t = el("text", { x, y, ...rest }, parent);
    t.textContent = str;
    return t;
  }
  function html(tag, attrs = {}, parent, content) {
    const node = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs)) if (v != null) node.setAttribute(k, v);
    if (content != null) node.textContent = content;
    if (parent) parent.appendChild(node);
    return node;
  }
  function svgIn(plot, label) {
    plot.querySelectorAll(":scope > svg").forEach((s) => s.remove());
    const w = plot.clientWidth, h = plot.clientHeight;
    const svg = el("svg", { viewBox: `0 0 ${w} ${h}`, role: "img", "aria-label": label }, plot);
    return { svg, w, h };
  }
  function srTable(parent, caption, headers, rows) {
    parent.querySelectorAll(":scope > table.sr-only").forEach((t) => t.remove());
    const t = html("table", { class: "sr-only" }, parent);
    html("caption", {}, t, caption);
    const hr = html("tr", {}, html("thead", {}, t));
    headers.forEach((h) => html("th", {}, hr, h));
    const tb = html("tbody", {}, t);
    rows.forEach((r) => { const tr = html("tr", {}, tb); r.forEach((c) => html("td", {}, tr, c)); });
  }
  const tip = (node, str) => { node.setAttribute("data-tip", str); node.setAttribute("data-interactive", ""); };

  const charts = {};

  /* slide 3: funnel widths, proportional to the count */
  charts.funnel = function () {
    const total = get("key_metrics.dataset.raw_rows");
    document.querySelectorAll("[data-share-of]").forEach((bar) => {
      // share of the row, leaving room for the unit label beside the bar
      bar.style.width = `calc((100% - 210px) * ${get(bar.dataset.shareOf) / total})`;
    });
  };

  /* slide 4: the fence band on the notebook's histogram, placed by value */
  charts.histogram = function (fig) {
    const d = fig.dataset, frame = fig.querySelector(".hist-frame");
    const x0 = +d.calX0, ppp = +d.calPxPerPoint, W = +d.calWidth, H = +d.calHeight;
    const fence = get("key_metrics.score.upper_fence"), max = get("key_metrics.score.max");
    const left = x0 + fence * ppp, right = x0 + max * ppp;
    frame.style.setProperty("--band-left", (100 * left) / W + "%");
    frame.style.setProperty("--band-width", (100 * (right - left)) / W + "%");
    frame.style.setProperty("--band-top", (100 * +d.calPlotTop) / H + "%");
    frame.style.setProperty("--band-bottom", (100 * (H - +d.calPlotBottom)) / H + "%");
    const label = frame.querySelector(".tail-label");
    label.textContent = `Past the fence (${fmt(fence, "num1")} pts): ${fmt(get("key_metrics.score.n_above_fence"), "int")} inspections`;
    label.style.left = (100 * left) / W + 1.2 + "%";
    label.style.top = "26%";
  };

  /* slide 5: missingness bars */
  charts.missingness = function (fig) {
    const fields = [["grade_date", "Grade date"], ["grade", "Grade"], ["score", "Score"], ["cuisine_description", "Cuisine"]];
    const plot = fig.querySelector(".plot");
    const { svg, w, h } = svgIn(plot, "Share of inspections missing each field");
    const labelW = 200, valueW = 120, rowH = Math.min(96, h / fields.length);
    const scale = (v) => ((w - labelW - valueW) * v) / 50;   // axis 0..50%
    fields.forEach(([key, name], i) => {
      const v = get(`key_metrics.missing.${key}`);
      const y = i * rowH + 10;
      text(svg, 0, y + rowH * 0.42, name, { "font-size": 28, "font-weight": 700, fill: "var(--ink)" });
      const bar = el("rect", { x: labelW, y, width: scale(v), height: rowH * 0.62, rx: 8,
        class: `bar grow-x bar-${i}`, fill: key === "grade" ? "var(--accent)" : "var(--ink-3)",
        style: `--d:${i + 2}` }, svg);
      tip(bar, `<b>${name}</b>: missing on ${fmt(v, "pct1")} of inspections`);
      text(svg, labelW + scale(v) + 14, y + rowH * 0.42, fmt(v, "pct1"), { class: "val", "font-size": 30 });
    });
    srTable(fig, "Share of inspections missing each field", ["Field", "Missing"],
      fields.map(([k, n]) => [n, fmt(get(`key_metrics.missing.${k}`), "pct1")]));
  };

  /* slide 6, left: borough medians */
  charts.borough = function (fig) {
    const rows = get("tables.borough").filter((b) => b.boro !== "0");
    const plot = fig.querySelector(".plot");
    const { svg, w, h } = svgIn(plot, "Median inspection score by borough, lower is better");
    const top = 40, bottom = 70, left = 40, maxV = 15;
    const ph = h - top - bottom, bw = (w - left) / rows.length;
    const y = (v) => top + ph - (ph * v) / maxV;
    [0, 5, 10, 15].forEach((g) => {
      el("line", { x1: left, x2: w, y1: y(g), y2: y(g), class: "grid" }, svg);
      text(svg, left - 8, y(g) + 7, g, { "text-anchor": "end", "font-size": 18 });
    });
    rows.forEach((b, i) => {
      const x = left + i * bw + bw * 0.18, bwid = bw * 0.64;
      const r = el("rect", { x, y: y(b.median), width: bwid, height: ph - (y(b.median) - top), rx: 6,
        fill: GRADE[gradeOf(b.median)], class: "bar grow-y", style: `--d:${i + 2}` }, svg);
      tip(r, `<b>${b.boro}</b>: median ${fmt(b.median, "num0")} points over ${fmt(b.count, "int")} scored inspections (lower is better)`);
      text(svg, x + bwid / 2, y(b.median) - 10, fmt(b.median, "num0"), { class: "val", "text-anchor": "middle", "font-size": 28 });
      const short = b.boro === "Staten Island" ? "Staten Is." : b.boro;
      text(svg, x + bwid / 2, h - bottom + 30, short, { "text-anchor": "middle", "font-size": 20 });
    });
    el("line", { x1: left, x2: w, y1: top + ph, y2: top + ph, class: "axis" }, svg);
    srTable(fig, "Median score by borough", ["Borough", "Median score", "Scored inspections"],
      rows.map((b) => [b.boro, fmt(b.median, "num0"), fmt(b.count, "int")]));
  };

  /* slide 6, right: cuisine medians, one row per cuisine; the label is the explorer chip */
  charts.cuisine = function (fig) {
    const rows = [...get("tables.cuisine")].sort((a, b) => a.median_score - b.median_score || b.inspections - a.inspections);
    const plot = fig.querySelector(".plot");
    plot.innerHTML = "";
    plot.classList.add("cuisine-rows", "hover-dim");
    const maxV = 20;
    rows.forEach((c, i) => {
      const row = html("div", { class: "crow hl" + (i === rows.length - 1 ? " bar-last" : ""), "data-cuisine-row": c.cuisine }, plot);
      const chip = html("button", { class: "chip", type: "button", "data-interactive": "", "data-cuisine": c.cuisine,
        "data-mascot-letter": c.typical_grade, "aria-pressed": "false" }, row, c.cuisine);
      chip.setAttribute("data-tip", `<b>${c.cuisine}</b>: median ${fmt(c.median_score, "num0")} points (${c.typical_grade}), ${fmt(c.inspections, "int")} inspections`);
      const track = html("div", { class: "ctrack" }, row);
      html("div", { class: "cbar grow-x", style: `width:${(100 * c.median_score) / maxV}%; background:${GRADE[c.typical_grade]}; --d:${2 + i * 0.5}` }, track);
      html("span", { class: "cval" }, row, fmt(c.median_score, "num0"));
    });
    srTable(fig, "Median score by cuisine", ["Cuisine", "Median score", "Inspections", "Modeled B or C share"],
      rows.map((c) => [c.cuisine, fmt(c.median_score, "num0"), fmt(c.inspections, "int"),
        c.modeled_bc_pct == null ? "" : fmt(c.modeled_bc_pct, "pct1")]));
  };

  /* slide 7: correlation matrix with the two traps ringed */
  charts.correlation = function (fig) {
    const { columns, matrix } = get("tables.correlation");
    const names = { score: "score", n_violations: "violations", n_critical: "critical", latitude: "latitude", longitude: "longitude" };
    const plot = fig.querySelector(".plot");
    const { svg, w, h } = svgIn(plot, "Correlation matrix of score, violations, critical violations, latitude and longitude");
    const lab = 170, n = columns.length, cell = Math.min((w - lab) / n, (h - lab + 40) / n);
    const ox = lab, oy = 10;
    matrix.forEach((row, i) => {
      text(svg, ox - 12, oy + i * cell + cell / 2 + 8, names[columns[i]], { "text-anchor": "end", "font-size": 21 });
      row.forEach((r, j) => {
        const a = Math.abs(r);
        const g = el("g", { class: "cell-in rv", style: `--d:${(i + j) * 0.6}` }, svg);
        const rect = el("rect", { x: ox + j * cell + 3, y: oy + i * cell + 3, width: cell - 6, height: cell - 6, rx: 8,
          fill: r < 0 ? "#5B6B8C" : "#1D1E22", "fill-opacity": 0.08 + 0.82 * a }, g);
        tip(rect, `<b>${names[columns[i]]} × ${names[columns[j]]}</b>: r = ${fmt(r, "dec2")}`);
        text(g, ox + j * cell + cell / 2, oy + i * cell + cell / 2 + 9, fmt(r, "dec2"),
          { "text-anchor": "middle", "font-size": 24, "font-weight": 700, fill: a > 0.5 ? "#FFFFFF" : "var(--ink)" });
      });
    });
    columns.forEach((c, j) => text(svg, ox + j * cell + cell / 2, oy + n * cell + 30, names[c], { "text-anchor": "middle", "font-size": 18 }));
    [[0, 2], [3, 4]].forEach(([i, j], k) => {
      el("rect", { x: ox + j * cell - 2, y: oy + i * cell - 2, width: cell + 4, height: cell + 4, rx: 12,
        fill: "none", stroke: "var(--accent)", "stroke-width": 7, class: "trap-ring", "data-trap": k }, svg);
    });
    srTable(fig, "Correlation matrix", ["", ...columns.map((c) => names[c])],
      matrix.map((row, i) => [names[columns[i]], ...row.map((r) => fmt(r, "dec2"))]));
  };

  /* ZIP polygons (map_risk_zip.html's boundary file) projected into a box */
  function zipProjection(shapes, x0, y0, w, h, pad = 12) {
    const kx = Math.cos((40.7 * Math.PI) / 180);
    let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
    for (const polys of Object.values(shapes)) for (const poly of polys) for (const [lon, lat] of poly[0]) {
      minX = Math.min(minX, lon * kx); maxX = Math.max(maxX, lon * kx); minY = Math.min(minY, lat); maxY = Math.max(maxY, lat);
    }
    const s = Math.min((w - 2 * pad) / (maxX - minX), (h - 2 * pad) / (maxY - minY));
    const ox = x0 + (w - s * (maxX - minX)) / 2, oy = y0 + h - (h - s * (maxY - minY)) / 2;
    const pt = ([lon, lat]) => `${(ox + s * (lon * kx - minX)).toFixed(1)} ${(oy - s * (lat - minY)).toFixed(1)}`;
    return (polys) => polys.map((poly) => poly.map((ring) => "M" + ring.map(pt).join("L") + "Z").join("")).join("");
  }

  /* slide 8: flat ZIP risk map. Filled ZIPs when the boundary file is exported;
     ZIP centroids as dots otherwise. */
  charts.zipmap = function (fig) {
    const zips = get("maps.zips"), clip = get("maps.color_scale.clip_pct");
    const plot = fig.querySelector(".plot");
    const shapes = get("maps.zcta_shapes"), risk = get("maps.risk_zip");
    if (shapes && risk) return zipChoropleth(fig, plot, zips, shapes, risk, clip);
    const { svg, w, h } = svgIn(plot, "Map of ZIP codes: dot size is inspections, color is the share ending B or C");
    const lat0 = 40.7, kx = Math.cos((lat0 * Math.PI) / 180);
    const xs = zips.map((z) => z.lon * kx), ys = zips.map((z) => z.lat);
    const [minX, maxX, minY, maxY] = [Math.min(...xs), Math.max(...xs), Math.min(...ys), Math.max(...ys)];
    const pad = 22, s = Math.min((w - 2 * pad) / (maxX - minX), (h - 2 * pad) / (maxY - minY));
    const offX = (w - s * (maxX - minX)) / 2, offY = (h - s * (maxY - minY)) / 2;
    const px = (z) => offX + s * (z.lon * kx - minX), py = (z) => h - offY - s * (z.lat - minY);
    const maxInsp = Math.max(...zips.map((z) => z.inspections));
    const r = (z) => 2.5 + 9.5 * Math.sqrt(z.inspections / maxInsp);
    const g = el("g", { class: "hover-dim" }, svg);
    const worst = get("key_metrics.zip.worst.zip");
    [...zips].sort((a, b) => b.inspections - a.inspections).forEach((z) => {
      const c = el("circle", { cx: px(z), cy: py(z), r: r(z), class: "hl dot",
        fill: z.reliable ? rampColor(z.pct_bc, clip) : "var(--unreliable)",
        stroke: "#FFFFFF", "stroke-width": 1.2, "data-zip": z.zip }, g);
      tip(c, z.reliable
        ? `<b>ZIP ${z.zip}</b><br>${fmt(z.pct_bc, "pct1")} ended B or C<br>${fmt(z.graded, "int")} graded of ${fmt(z.inspections, "int")} inspections`
        : `<b>ZIP ${z.zip}</b><br>not enough inspections to judge<br>${fmt(z.graded, "int")} graded of ${fmt(z.inspections, "int")} inspections`);
    });
    const wz = zips.find((z) => z.zip === worst);
    el("circle", { cx: px(wz), cy: py(wz), r: r(wz) + 6, fill: "none", stroke: "var(--ink)", "stroke-width": 3 }, svg);
    text(svg, px(wz) + r(wz) + 10, py(wz) - 10, `${worst}: ${fmt(wz.pct_bc, "pct1")}`, { class: "val", "font-size": 22 });
    srTable(fig, "B or C share by ZIP code", ["ZIP", "Inspections", "Graded", "B or C share"],
      zips.map((z) => [z.zip, fmt(z.inspections, "int"), fmt(z.graded, "int"),
        z.reliable ? fmt(z.pct_bc, "pct1") : "not enough inspections to judge"]));
  };

  function zipChoropleth(fig, plot, zips, shapes, risk, clip) {
    const { svg, w, h } = svgIn(plot, "Map of ZIP codes coloured by the share of graded inspections ending B or C");
    const path = zipProjection(shapes, 0, 0, w, h, 8);
    const hero = Object.fromEntries(zips.map((z) => [z.zip, z]));
    const byZip = Object.fromEntries(risk.map((r) => [r.zip, r]));
    const worst = get("key_metrics.zip.worst.zip");
    const g = el("g", { class: "hover-dim" }, svg);
    for (const [zip, polys] of Object.entries(shapes)) {
      const r = byZip[zip], z = hero[zip];
      const fill = !r ? "#EEF0F2" : r.reliable ? rampColor(r.pct_bc, clip) : "var(--unreliable)";
      const shape = el("path", { d: path(polys), class: "hl zip", fill, stroke: "#FFFFFF", "stroke-width": 0.8, "data-zip": zip }, g);
      tip(shape, !r ? `<b>ZIP ${zip}</b><br>no inspections matched to this ZIP`
        : r.reliable
          ? `<b>ZIP ${zip}</b><br>${fmt(z.pct_bc, "pct1")} ended B or C<br>${fmt(r.graded, "int")} graded of ${fmt(z.inspections, "int")} inspections`
          : `<b>ZIP ${zip}</b><br>not enough inspections to judge<br>${fmt(r.graded, "int")} graded of ${fmt(z.inspections, "int")} inspections`);
    }
    el("path", { d: path(shapes[worst]), fill: "none", stroke: "var(--ink)", "stroke-width": 3 }, svg);
    const wb = svg.querySelector(`path[data-zip="${worst}"]`).getBBox();
    text(svg, wb.x + wb.width + 8, wb.y + 6, `${worst}: ${fmt(hero[worst].pct_bc, "pct1")}`, { class: "val", "font-size": 22 });
    srTable(fig, "B or C share by ZIP code", ["ZIP", "Inspections", "Graded", "B or C share"],
      risk.map((r) => [r.zip, fmt(hero[r.zip].inspections, "int"), fmt(r.graded, "int"),
        r.reliable ? fmt(hero[r.zip].pct_bc, "pct1") : "not enough inspections to judge"]));
  }

  /* slide 9 toggle, "Scored 14+": the notebook's paired ZIP maps (cell 13.5),
     one colour scale for both, grey under the 20-scored floor */
  function visitMaps(svg, w, h) {
    const vp = get("maps.visit_kind_panels"), shapes = get("maps.zcta_shapes");
    const zmax = vp.shared_zmax, gap = 16, mw = (w - gap) / 2;
    [["initial", "First visits"], ["reinspection", "Re-inspections"]].forEach(([kind, name], i) => {
      const x0 = i * (mw + gap);
      const path = zipProjection(shapes, x0, 16, mw * 0.62, h - 16, 2);
      const byZip = Object.fromEntries(vp.panels[kind].map((p) => [p.zip, p]));
      const g = el("g", {}, svg);
      for (const [zip, polys] of Object.entries(shapes)) {
        const p = byZip[zip];
        const shape = el("path", { d: path(polys), stroke: "#FFFFFF", "stroke-width": 0.3,
          fill: !p ? "#EEF0F2" : p.reliable ? rampColor(p.pct_high, zmax) : "var(--unreliable)" }, g);
        if (p) tip(shape, p.reliable
          ? `<b>ZIP ${zip}</b>, ${name.toLowerCase()}<br>${fmt(p.pct_high, "pct1")} scored 14 or more<br>${fmt(p.scored, "int")} scored inspections`
          : `<b>ZIP ${zip}</b>, ${name.toLowerCase()}<br>too few to judge (${fmt(p.scored, "int")} scored)`);
      }
      const overall = get(`key_metrics.visit_kind.${kind}_pct_scored_14_plus`);
      text(svg, x0, 12, overall == null ? name : `${name}: ${fmt(overall, "pct1")} scored 14+`,
        { "font-size": 15, "font-weight": 700, fill: "var(--ink)" });
      const lx = x0 + mw * 0.66;
      if (kind === "initial") {
        text(svg, lx, h * 0.42, "no B or C is ever", { "font-size": 13, class: "initial-note" });
        text(svg, lx, h * 0.42 + 16, "issued on a first visit", { "font-size": 13, class: "initial-note" });
      } else {
        text(svg, lx, h * 0.42, "scored 14+:", { "font-size": 13 });
        text(svg, lx, h * 0.42 + 16, `0 to ${fmt(zmax, "pct0")}, one scale`, { "font-size": 13 });
        text(svg, lx, h * 0.42 + 32, `grey: < ${vp.floor_scored} scored`, { "font-size": 13 });
      }
    });
  }

  /* slide 9: B-or-C share by visit kind, with the pre-reveal ghost */
  function visitBars(svg, w, h, opts) {
    const vk = get("key_metrics.visit_kind"), clip = get("maps.color_scale.clip_pct");
    const measure = opts.measure || "grade";
    const vals = measure === "grade"
      ? [vk.initial_bc_pct, vk.reinspection_bc_pct]
      : [vk.initial_pct_scored_14_plus, vk.reinspection_pct_scored_14_plus];
    const names = ["First visits", "Re-inspections"];
    const top = opts.small ? 26 : 50, bottom = opts.small ? 26 : 60, maxV = 40;
    const ph = h - top - bottom, bw = Math.min(w / 4.2, opts.small ? 90 : 190);
    const y = (v) => top + ph - (ph * v) / maxV;
    if (!opts.small) [0, 10, 20, 30, 40].forEach((g) => {
      el("line", { x1: 60, x2: w, y1: y(g), y2: y(g), class: "grid" }, svg);
      text(svg, 50, y(g) + 7, g + "%", { "text-anchor": "end", "font-size": 18 });
    });
    names.forEach((name, i) => {
      const cx = (w * (i + 1)) / 3 + (opts.small ? 0 : 20), x = cx - bw / 2, v = vals[i];
      text(svg, cx, h - bottom + (opts.small ? 20 : 34), name, { "text-anchor": "middle", "font-size": opts.small ? 16 : 22, "font-weight": 700 });
      if (v == null) {
        text(svg, cx, top + ph / 2, "awaiting export", { "text-anchor": "middle", "font-size": opts.small ? 14 : 20, fill: "#8A1C10", "font-weight": 700, "data-pending": "" });
        return;
      }
      const isInitial = i === 0;
      if (isInitial && opts.ghost) {
        const gh = vals[1] ?? 0;
        const ghost = el("rect", { x, y: y(gh), width: bw, height: ph - (y(gh) - top), rx: 8, class: "ghost-bar",
          fill: "url(#hatch)", stroke: "var(--ink-3)", "stroke-width": 2, "stroke-dasharray": "8 6" }, svg);
        text(svg, cx, y(gh) - 12, "?", { class: "val ghost-label", "text-anchor": "middle", "font-size": opts.small ? 22 : 40 });
        if (opts.small) return;
        ghost.classList.add("collapses");
      }
      if (isInitial && opts.ghost && opts.small) return;
      const bar = el("rect", { x, y: y(v), width: bw, height: Math.max(0, ph - (y(v) - top)), rx: 8,
        fill: measure === "grade" ? rampColor(v, clip) : "var(--ink-3)", class: "bar grow-y" + (isInitial ? " real-initial" : "") }, svg);
      tip(bar, measure === "grade"
        ? `<b>${name}</b>: ${fmt(v, "pct1")} of ${fmt(isInitial ? vk.initial_graded : vk.reinspection_graded, "int")} graded ended B or C`
        : `<b>${name}</b>: ${fmt(v, "pct1")} of scored inspections at 14 points or more`);
      text(svg, cx, y(v) - 12, fmt(v, "pct1"), { class: "val" + (isInitial ? " real-initial-label" : ""), "text-anchor": "middle", "font-size": opts.small ? 18 : 34 });
      if (measure === "grade" && !opts.small) {
        const n = isInitial ? vk.initial_graded : vk.reinspection_graded;
        text(svg, cx, h - bottom + 58, `${fmt(n, "int")} graded`, { class: isInitial ? "real-initial-label" : "", "text-anchor": "middle", "font-size": 18 });
      }
    });
    if (measure === "score" && opts.small) {   // only on the first-visit side
      text(svg, w / 3, top - 8, "no B or C is ever issued on a first visit", { "text-anchor": "middle", "font-size": 13, class: "initial-note" });
    }
    el("line", { x1: opts.small ? 0 : 60, x2: w, y1: top + ph, y2: top + ph, class: "axis" }, svg);
  }
  function hatchDefs(svg) {
    const defs = el("defs", {}, svg);
    const p = el("pattern", { id: "hatch", width: 10, height: 10, patternUnits: "userSpaceOnUse", patternTransform: "rotate(45)" }, defs);
    el("rect", { width: 10, height: 10, fill: "#F5F6F7" }, p);
    el("line", { x1: 0, y1: 0, x2: 0, y2: 10, stroke: "#C9CBD0", "stroke-width": 4 }, p);
  }
  charts.visitbars = function (fig) {
    const plot = fig.querySelector(".plot");
    const { svg, w, h } = svgIn(plot, "Share of graded inspections ending B or C: first visits versus re-inspections");
    hatchDefs(svg);
    visitBars(svg, w, h, { ghost: true });
    const vk = get("key_metrics.visit_kind");
    srTable(fig, "B or C share by visit kind", ["Visit", "Graded", "B or C share"],
      [["First visits", fmt(vk.initial_graded, "int"), fmt(vk.initial_bc_pct, "pct1")],
       ["Re-inspections", fmt(vk.reinspection_graded, "int"), fmt(vk.reinspection_bc_pct, "pct1")]]);
  };
  charts.visitMinis = function (measure = "grade") {
    document.querySelectorAll("[data-chart-mini]").forEach((plot) => {
      const before = plot.dataset.chartMini === "before";
      const { svg, w, h } = svgIn(plot, before ? "What we expected before looking: unknown" : "What the file says");
      hatchDefs(svg);
      if (!before && measure === "score" && get("maps.visit_kind_panels") && get("maps.zcta_shapes")) visitMaps(svg, w, h);
      else visitBars(svg, w, h, { small: true, ghost: before, measure: before ? "grade" : measure });
    });
  };

  /* slide 10: one restaurant's inspections */
  charts.timeline = function (fig) {
    const ex = get("tables.history_example.rows");
    const plot = fig.querySelector(".plot");
    const { svg, w, h } = svgIn(plot, "One restaurant's six inspections in 2024 and the history each one could see");
    // visits are evenly spaced (several fall within days of each other); dates are labelled
    const t = ex.map((_, i) => i);
    const left = 110, right = 110, x = (v) => left + ((w - left - right) * v) / (ex.length - 1);
    const axisY = h - 70;
    el("line", { x1: left - 30, x2: w - right + 30, y1: axisY, y2: axisY, class: "axis" }, svg);
    const short = (s) => s.split("/ ")[1].replace(" Inspection", "");
    ex.forEach((r, i) => {
      const cx = x(t[i]);
      const g = el("g", { class: "rv", style: `--d:${i * 1.5}` }, svg);
      const dot = el("circle", { cx, cy: axisY, r: 13, fill: "var(--ink)" }, g);
      tip(dot, `<b>${r.inspection_date}</b> · ${short(r.inspection_type)}<br>score ${fmt(r.score, "num0")} (lower is better)<br>seen beforehand: ${r.prior_count} prior` +
        (r.prior_mean_score == null ? "" : `, mean ${fmt(r.prior_mean_score, "num1")}, last ${fmt(r.last_score, "num0")}`));
      text(g, cx, axisY - 34, `${fmt(r.score, "num0")} pts`, { class: "val", "text-anchor": "middle", "font-size": 24 });
      text(g, cx, axisY + 34, r.inspection_date, { "text-anchor": "middle", "font-size": 17 });
      text(g, cx, axisY + 56, short(r.inspection_type), { "text-anchor": "middle", "font-size": 17 });
      const seen = r.prior_count === 0 ? "no history yet" : `${r.prior_count} prior · mean ${fmt(r.prior_mean_score, "num0")} · last ${fmt(r.last_score, "num0")}`;
      text(g, cx, axisY - 82, seen, { "text-anchor": "middle", "font-size": 17, fill: "var(--grade-a)", "font-weight": 700 });
    });
    text(svg, left - 30, 22, "Green: what the model can see before each visit", { "font-size": 18 });
    const tr = get("key_metrics.split.train_rows"), te = get("key_metrics.split.test_rows");
    const strip = document.querySelector("[data-split-strip]");
    if (strip) strip.style.gridTemplateColumns = `${tr}fr ${te}fr`;
  };

  /* slide 11: PCA variance per component + cumulative */
  charts.pca = function (fig) {
    const comps = get("pca.components");
    const plot = fig.querySelector(".plot");
    const { svg, w, h } = svgIn(plot, "Variance explained by each principal component, with the cumulative share");
    const left = 70, bottom = 46, top = 20, ph = h - top - bottom, bw = (w - left) / comps.length;
    const y = (v) => top + ph - (ph * v) / 100;
    [0, 25, 50, 75, 100].forEach((g) => {
      el("line", { x1: left, x2: w, y1: y(g), y2: y(g), class: "grid" }, svg);
      text(svg, left - 10, y(g) + 7, g + "%", { "text-anchor": "end", "font-size": 18 });
    });
    el("line", { x1: left, x2: w, y1: y(90), y2: y(90), stroke: "var(--ink-3)", "stroke-width": 2, "stroke-dasharray": "8 6" }, svg);
    text(svg, w - 4, y(90) - 8, "90%", { "text-anchor": "end", "font-size": 18, "font-weight": 700 });
    let path = "";
    comps.forEach((c, i) => {
      const x = left + i * bw;
      const bar = el("rect", { x: x + bw * 0.15, y: y(c.variance_pct), width: bw * 0.7, height: ph - (y(c.variance_pct) - top), rx: 4,
        fill: i < 2 ? "var(--ink)" : "var(--ink-3)", class: "bar grow-y", style: `--d:${i * 0.6}` }, svg);
      tip(bar, `<b>${c.component}</b>: ${fmt(c.variance_pct, "pct1")} of the variance; ${fmt(c.cumulative_pct, "pct1")} cumulative`);
      if (i < 2) text(svg, x + bw / 2, y(c.variance_pct) - 8, fmt(c.variance_pct, "pct1"), { class: "val", "text-anchor": "middle", "font-size": 20 });
      text(svg, x + bw / 2, h - bottom + 26, c.component, { "text-anchor": "middle", "font-size": 16 });
      path += `${i ? "L" : "M"}${x + bw / 2} ${y(c.cumulative_pct)} `;
    });
    el("path", { d: path, fill: "none", stroke: "var(--accent)", "stroke-width": 4, class: "draw", pathLength: 1 }, svg);
    comps.forEach((c, i) => el("circle", { cx: left + i * bw + bw / 2, cy: y(c.cumulative_pct), r: 5, fill: "var(--accent)" }, svg));
    srTable(fig, "PCA explained variance", ["Component", "Variance", "Cumulative"],
      comps.map((c) => [c.component, fmt(c.variance_pct, "pct1"), fmt(c.cumulative_pct, "pct1")]));
  };

  /* slide 12: test ROC-AUC bars with train rings */
  charts.auc = function (fig) {
    const order = ["Logistic regression", "Random forest", "Gradient boosting", "Dummy (always A)"];
    const rows = order.map((m) => get(`tables.models[${m}]`));
    const plot = fig.querySelector(".plot");
    const { svg, w, h } = svgIn(plot, "Test and train ROC-AUC for four models");
    const left = 70, bottom = 56, top = 34, ph = h - top - bottom, bw = (w - left) / rows.length;
    const y = (v) => top + ph - ph * v;
    [0, 0.25, 0.5, 0.75, 1].forEach((g) => {
      el("line", { x1: left, x2: w, y1: y(g), y2: y(g), class: "grid" }, svg);
      text(svg, left - 10, y(g) + 7, g.toFixed(2), { "text-anchor": "end", "font-size": 18 });
    });
    el("line", { x1: left, x2: w, y1: y(0.5), y2: y(0.5), stroke: "var(--ink-3)", "stroke-width": 2, "stroke-dasharray": "8 6" }, svg);
    const g = el("g", { class: "hover-dim" }, svg);
    rows.forEach((r, i) => {
      const cx = left + i * bw + bw / 2, x = cx - bw * 0.26;
      const grp = el("g", { class: "hl" }, g);
      const bar = el("rect", { x, y: y(r.test_roc_auc), width: bw * 0.52, height: ph - (y(r.test_roc_auc) - top), rx: 6,
        fill: i === 0 ? "var(--ink)" : i === 3 ? "#C9CBD0" : "var(--ink-3)", class: "bar grow-y", style: `--d:${i + 2}` }, grp);
      tip(bar, `<b>${r.model}</b><br>test ROC-AUC ${fmt(r.test_roc_auc, "dec3")} (2025 on)<br>train ROC-AUC ${fmt(r.train_roc_auc, "dec3")}<br>gap ${fmt(r.train_roc_auc - r.test_roc_auc, "dec3")}`);
      text(grp, cx, y(r.test_roc_auc) + 34, fmt(r.test_roc_auc, "dec3"), { "text-anchor": "middle", "font-size": 26, "font-weight": 700, fill: i === 3 ? "var(--ink)" : "#FFFFFF" });
      const ring = el("circle", { cx, cy: y(r.train_roc_auc), r: 14, fill: "var(--paper)", stroke: "var(--accent)", "stroke-width": 5, class: "rv", style: `--d:${i + 6}` }, grp);
      tip(ring, `<b>${r.model}</b>: train ROC-AUC ${fmt(r.train_roc_auc, "dec3")}`);
      const gap = r.train_roc_auc - r.test_roc_auc;
      text(grp, cx + 22, y(r.train_roc_auc) + 7, Math.abs(gap) < 0.02 ? "train ≈ test" : `train ${fmt(r.train_roc_auc, "dec3")}`,
        { "font-size": 20, "font-weight": 700, fill: "var(--accent-ink)", class: "rv", style: `--d:${i + 6}`, transform: Math.abs(gap) < 0.02 ? `translate(0 -26)` : null });
      if (gap > 0.05)
        el("line", { x1: cx, x2: cx, y1: y(r.train_roc_auc) + 14, y2: y(r.test_roc_auc) - 4, stroke: "var(--accent)", "stroke-width": 3, "stroke-dasharray": "6 5", class: "rv", style: `--d:${i + 7}` }, grp);
      text(grp, cx, h - bottom + 30, r.model.replace(" (always A)", ""), { "text-anchor": "middle", "font-size": 20, "font-weight": 700 });
    });
    srTable(fig, "Model comparison", ["Model", "Train ROC-AUC", "Test ROC-AUC"],
      rows.map((r) => [r.model, fmt(r.train_roc_auc, "dec3"), fmt(r.test_roc_auc, "dec3")]));
  };

  /* slide 13: ROC and PR curves for the winning model, with the threshold marker */
  charts.curves = function (fig) {
    const model = get("thresholds.model"), curves = get(`curves.models.${model}`);
    const plot = fig.querySelector(".plot");
    const { svg, w, h } = svgIn(plot, `ROC and precision-recall curves for the ${model}, test years`);
    const gap = 40, pw = (w - gap) / 2, ph = h - 50;
    const panels = [
      { key: "roc", title: "ROC", xl: "false positive rate", yl: "recall", pts: curves.roc, ox: 0 },
      { key: "pr", title: "Precision–recall", xl: "recall", yl: "precision", pts: curves.pr, ox: pw + gap },
    ];
    panels.forEach((p) => {
      const g = el("g", { transform: `translate(${p.ox} 6)` }, svg);
      const L = 44, sx = (v) => L + (pw - L - 6) * v, sy = (v) => ph - 26 - (ph - 40) * v;
      el("rect", { x: L, y: sy(1), width: sx(1) - L, height: sy(0) - sy(1), fill: "var(--mist)" }, g);
      if (p.key === "roc") el("line", { x1: sx(0), y1: sy(0), x2: sx(1), y2: sy(1), stroke: "var(--ink-3)", "stroke-dasharray": "5 5" }, g);
      el("path", { d: p.pts.map((q, i) => `${i ? "L" : "M"}${sx(q[0]).toFixed(1)} ${sy(q[1]).toFixed(1)}`).join(" "),
        fill: "none", stroke: "var(--ink)", "stroke-width": 3, class: "draw", pathLength: 1 }, g);
      text(g, L, sy(1) - 8, p.title, { "font-size": 18, "font-weight": 700, fill: "var(--ink)" });
      text(g, sx(0.5), sy(0) + 22, p.xl, { "text-anchor": "middle", "font-size": 15 });
      text(g, 12, sy(0.5), p.yl, { "text-anchor": "middle", "font-size": 15, transform: `rotate(-90 12 ${sy(0.5)})` });
      el("circle", { r: 9, fill: "var(--accent)", stroke: "#FFFFFF", "stroke-width": 3, class: "thr-marker", "data-panel": p.key,
        "data-sx": `${L}|${pw - L - 6}`, "data-sy": `${ph - 26}|${ph - 40}` }, g);
    });
    const box = document.querySelector("[data-threshold] input[type=range]");
    const stops = get("thresholds.stops");
    charts.curveMarker(box ? stops[Number(box.value)].threshold : get("thresholds.default"));
  };
  charts.curveMarker = function (threshold) {
    const pt = get(`curves.threshold_points[${threshold}]`);
    if (!pt) return;
    document.querySelectorAll(".thr-marker").forEach((m) => {
      const [L, W] = m.dataset.sx.split("|").map(Number), [B, H] = m.dataset.sy.split("|").map(Number);
      const [vx, vy] = m.dataset.panel === "roc" ? [pt.fpr, pt.tpr] : [pt.tpr, pt.precision];
      m.setAttribute("cx", L + W * vx);
      m.setAttribute("cy", B - H * vy);
    });
  };

  /* backup B3: cuisine coefficients, diverging */
  charts.cuisinecoef = function (fig) {
    const rows = get("importance.cuisine_coefficients");
    const plot = fig.querySelector(".plot");
    const { svg, w, h } = svgIn(plot, "Logistic regression coefficient for each grouped cuisine");
    const lab = 330, rowH = h / rows.length, maxA = Math.max(...rows.map((r) => Math.abs(r.coefficient)));
    const mid = lab + (w - lab) / 2, sc = ((w - lab) / 2 - 80) / maxA;
    el("line", { x1: mid, x2: mid, y1: 0, y2: h, class: "axis" }, svg);
    const g = el("g", { class: "hover-dim" }, svg);
    rows.forEach((r, i) => {
      const y = i * rowH, v = r.coefficient, grp = el("g", { class: "hl" }, g);
      text(grp, lab - 14, y + rowH * 0.72, r.cuisine, { "text-anchor": "end", "font-size": Math.min(19, rowH * 0.75) });
      const bar = el("rect", { x: v >= 0 ? mid : mid + v * sc, y: y + rowH * 0.14, width: Math.abs(v) * sc, height: rowH * 0.72, rx: 3,
        fill: v >= 0 ? "var(--grade-c)" : "var(--grade-a)", class: "bar grow-x", style: `--d:${i * 0.3}` }, grp);
      tip(bar, `<b>${r.cuisine}</b>: coefficient ${fmt(v, "dec3")} (${v >= 0 ? "toward B or C" : "toward A"})`);
      text(grp, v >= 0 ? mid + v * sc + 8 : mid + v * sc - 8, y + rowH * 0.72, fmt(v, "dec3"),
        { "text-anchor": v >= 0 ? "start" : "end", "font-size": Math.min(17, rowH * 0.7), class: "val" });
    });
    srTable(fig, "Cuisine coefficients", ["Cuisine", "Coefficient"], rows.map((r) => [r.cuisine, fmt(r.coefficient, "dec3")]));
  };

  /* Charts are drawn when their slide is shown (hidden slides measure 0 px),
     and redrawn only if the slide's layout size changed. */
  function renderSlide(slide) {
    if (slide.querySelector("[data-share-of]")) charts.funnel();
    slide.querySelectorAll("[data-chart]").forEach((fig) => {
      const fn = charts[fig.dataset.chart];
      const plot = fig.querySelector(".plot");
      if (!fn || !plot) return;
      const size = plot.clientWidth + "x" + plot.clientHeight;
      if (!plot.clientWidth || fig.dataset.renderedAt === size) return;
      try { fn(fig); fig.classList.add("rendered"); fig.dataset.renderedAt = size; }
      catch (err) { console.error("chart failed:", fig.dataset.chart, err); }
    });
    if (slide.querySelector("[data-chart-mini]")) {
      const btn = slide.querySelector('[data-toggle="visit-type"][aria-pressed="true"]');
      charts.visitMinis(btn ? btn.dataset.measure : "grade");
    }
  }

  window.DeckCharts = { renderSlide, charts };
})();
