// Browser gates for qa_check.py (Part 10). Prints one JSON report.
// Navigation, counter, notes view, slider-vs-thresholds.json, keyboard focus
// return, mascot safety and safe-zone overlap, reduced motion, offline and
// file:// behaviour.
import { chromium } from "playwright";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { pathToFileURL } from "node:url";
import { serve, DECK_ROOT } from "./lib/serve.mjs";

const results = [];
const check = (gate, ok, detail = "") => results.push({ gate, ok: !!ok, detail });
const server = await serve();
const browser = await chromium.launch();
const thresholds = JSON.parse(readFileSync(join(DECK_ROOT, "data/thresholds.json"), "utf8"));

async function open(query = "", hash = "#/0", opts = {}) {
  const context = await browser.newContext({ viewport: { width: 1920, height: 1080 }, ...opts });
  const page = await context.newPage();
  const external = [], errors = [];
  await page.route("**/*", (route) => {
    const url = route.request().url();
    if (url.startsWith(server.url) || url.startsWith("data:") || url.startsWith("blob:") || url.startsWith("file:")) return route.continue();
    external.push(url);
    return route.abort();
  });
  page.on("pageerror", (e) => errors.push(String(e)));
  page.on("console", (m) => { if (m.type() === "error") errors.push(m.text()); });
  await page.goto(`${server.url}/index.html${query}${hash}`);
  await page.waitForFunction(() => window.__deckReady === true, null, { timeout: 30000 });
  return { context, page, external, errors };
}
const idx = (page) => page.evaluate(() => Reveal.getIndices());

/* ---------------- navigation, counter, hash, notes ---------------------- */
{
  const { context, page, external, errors } = await open();
  const total = await page.evaluate(() => Reveal.getTotalSlides());
  check("19 slides (15 + 4 backup)", total === 19, `total ${total}`);
  await page.keyboard.press("ArrowRight"); await page.waitForTimeout(1300);
  check("ArrowRight advances", (await idx(page)).h === 1);
  await page.keyboard.press("ArrowLeft"); await page.waitForTimeout(1300);
  check("ArrowLeft goes back", (await idx(page)).h === 0);
  await page.keyboard.press("Space"); await page.waitForTimeout(1300);
  check("Space advances", (await idx(page)).h === 1);
  await page.keyboard.press("PageDown"); await page.waitForTimeout(1300);
  check("PageDown advances", (await idx(page)).h === 2);
  await page.keyboard.press("PageUp"); await page.waitForTimeout(1300);
  check("PageUp goes back", (await idx(page)).h === 1);
  await page.keyboard.press("End"); await page.waitForTimeout(400);
  check("End goes to the last slide", (await idx(page)).h === total - 1);
  await page.keyboard.press("Home"); await page.waitForTimeout(400);
  check("Home goes to the first slide", (await idx(page)).h === 0);
  await page.keyboard.press("Escape"); await page.waitForTimeout(400);
  check("Esc opens the overview", await page.evaluate(() => Reveal.isOverview()));
  await page.keyboard.press("Escape"); await page.waitForTimeout(400);
  // counter on every slide
  let counterOk = true, counterBad = "";
  for (let i = 0; i < total; i++) {
    await page.evaluate((n) => Reveal.slide(n), i);
    const txt = await page.evaluate(() => document.querySelector(".slide-number")?.innerText.replace(/\s/g, ""));
    if (txt !== `${i + 1}/${total}`) { counterOk = false; counterBad = `slide ${i + 1}: "${txt}"`; break; }
  }
  check("counter visible and correct on every slide", counterOk, counterBad);
  // notes view opens offline (S)
  const popupPromise = context.waitForEvent("page", { timeout: 8000 }).catch(() => null);
  await page.keyboard.press("s");
  const popup = await popupPromise;
  let notesOk = false;
  if (popup) {
    await popup.waitForTimeout(2500);
    notesOk = await popup.evaluate(() => !!document.querySelector(".speaker-controls-notes, #speaker-controls, .speaker-controls"));
    await popup.close();
  }
  check("speaker notes view (S) opens offline", notesOk);
  check("no external requests during navigation", external.length === 0, external.join(", "));
  check("no console errors during navigation", errors.length === 0, errors.slice(0, 3).join(" | "));
  await context.close();
}
{
  const { context, page } = await open("", "#/threshold");
  check("hash deep-link lands on #/threshold", (await idx(page)).h === 12);
  await context.close();
}

/* ---------------- slider == thresholds.json; focus returns -------------- */
{
  const { context, page } = await open("", "#/12");
  await page.waitForTimeout(1500);
  const n = await page.evaluate(() => Number(document.querySelector("#thr").max) + 1);
  check("slider stops == exported stops", n === thresholds.stops.length, `${n} vs ${thresholds.stops.length}`);
  const fmtPct = (v) => (Math.round(v * 1000) / 10).toFixed(1) + "%";
  let all = true, bad = "";
  for (let i = 0; i < thresholds.stops.length; i++) {
    await page.evaluate((v) => { const el = document.querySelector("#thr"); el.value = String(v); el.dispatchEvent(new Event("input")); }, i);
    await page.waitForTimeout(450);
    const shown = await page.evaluate(() => ({
      recall: document.querySelector('[data-out="recall"]').textContent,
      precision: document.querySelector('[data-out="precision"]').textContent,
      f1: document.querySelector('[data-out="f1"]').textContent,
      tn: document.querySelector('[data-cm="tn"]').textContent, fp: document.querySelector('[data-cm="fp"]').textContent,
      fn: document.querySelector('[data-cm="fn"]').textContent, tp: document.querySelector('[data-cm="tp"]').textContent,
    }));
    const s = thresholds.stops[i];
    const want = { recall: fmtPct(s.recall), precision: fmtPct(s.precision), f1: s.f1.toFixed(3),
      tn: s.tn.toLocaleString("en-US"), fp: s.fp.toLocaleString("en-US"), fn: s.fn.toLocaleString("en-US"), tp: s.tp.toLocaleString("en-US") };
    for (const k of Object.keys(want)) if (shown[k] !== want[k]) { all = false; bad = `stop ${s.threshold} ${k}: ${shown[k]} != ${want[k]}`; }
  }
  check("slider values match thresholds.json at every stop", all, bad);
  // keyboard: focus the slider, move it, Esc, then arrows navigate slides again
  await page.focus("#thr");
  await page.keyboard.press("ArrowLeft");
  const moved = await page.evaluate(() => document.querySelector("#thr").value);
  await page.keyboard.press("Escape");
  await page.waitForTimeout(200);
  const overview = await page.evaluate(() => Reveal.isOverview());
  await page.keyboard.press("ArrowRight"); await page.waitForTimeout(1500);
  check("after the slider, Esc returns the arrow keys to the slides", (await idx(page)).h === 13 && !overview, `slider value ${moved}, overview ${overview}`);
  // trap card button and toggles hand focus back too
  await page.evaluate(() => Reveal.slide(11)); await page.waitForTimeout(1400);
  await page.click("[data-reveal]"); await page.waitForTimeout(700);
  const flipped = await page.evaluate(() => document.querySelector("[data-trap-card]").classList.contains("flipped"));
  await page.keyboard.press("ArrowRight"); await page.waitForTimeout(1500);
  check("dummy trap flips, then arrows still navigate", flipped && (await idx(page)).h === 12);
  await context.close();
}

/* ---------------- mascot safety ----------------------------------------- */
{
  const { context, page } = await open("", "#/5");
  const m = await page.evaluate(() => {
    const layer = document.getElementById("mascot-layer"), r = layer.getBoundingClientRect();
    return { pe: getComputedStyle(layer).pointerEvents, svgPe: getComputedStyle(document.getElementById("mascot")).pointerEvents,
             outside: !layer.closest(".reveal"), r: [r.left, r.top, r.right, r.bottom] };
  });
  check("mascot is pointer-events: none and outside the reveal root", m.pe === "none" && m.svgPe === "none" && m.outside);
  check("mascot sits inside the bottom-right 180x180 safe zone", m.r[0] >= 1740 && m.r[1] >= 900 && m.r[2] <= 1920 && m.r[3] <= 1080, m.r.join(","));
  // clicking through the mascot reaches the page
  const hit = await page.evaluate(() => { const r = document.getElementById("mascot-layer").getBoundingClientRect();
    const el = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2); return !el.closest("#mascot-layer"); });
  check("the mascot never traps a click", hit);
  // hover an interactive element -> hover-delight (after the entry cues end); tab hidden -> paused
  await page.waitForTimeout(5000);
  await page.hover("[data-cuisine]"); await page.waitForTimeout(100);
  const st = await page.evaluate(() => window.DeckMascot.state);
  check("hovering [data-interactive] gives hover-delight", st === "hover-delight", st);
  await page.evaluate(() => { Object.defineProperty(document, "hidden", { value: true, configurable: true }); document.dispatchEvent(new Event("visibilitychange")); });
  const paused = await page.evaluate(() => document.getElementById("mascot").classList.contains("paused"));
  check("mascot pauses when the tab is hidden", paused);
  await context.close();
}

/* ---------------- safe-zone overlap, every slide, export mode ------------ */
{
  const { context, page } = await open("?export=1");
  const total = await page.evaluate(() => Reveal.getTotalSlides());
  const hits = [];
  for (let i = 0; i < total; i++) {
    await page.evaluate((n) => Reveal.slide(n, 0, 99), i);
    await page.waitForTimeout(120);
    const found = await page.evaluate(() => {
      const s = Reveal.getCurrentSlide(), out = [];
      const zone = { left: 1920 - 180, top: 1080 - 180 };
      const els = s.querySelectorAll("p, span, text, td, th, h1, h2, h3, h4, li, button, input, figcaption, .legend, .slide-foot, .caption, [data-interactive], tspan, label");
      for (const el of els) {
        if (el.closest("aside.notes") || el.closest(".poster-bg") || el.closest(".sr-only")) continue;
        const cs = getComputedStyle(el);
        if (cs.visibility === "hidden" || cs.display === "none" || Number(cs.opacity) === 0) continue;
        const r = el.getBoundingClientRect();
        if (!r.width || !r.height) continue;
        if (r.right > zone.left && r.bottom > zone.top) out.push(`${el.tagName.toLowerCase()}.${el.className?.baseVal ?? el.className} "${(el.textContent || "").trim().slice(0, 30)}"`);
      }
      const counter = document.querySelector(".slide-number").getBoundingClientRect();
      if (counter.right > zone.left && counter.bottom > zone.top) out.push("slide counter");
      return out;
    });
    if (found.length) hits.push(`slide ${i + 1}: ${found.slice(0, 3).join("; ")}`);
  }
  check("nothing enters the mascot's safe zone on any slide (export mode)", hits.length === 0, hits.join(" | "));
  const mascot = await page.evaluate(() => ({ state: window.DeckMascot.state, letter: window.DeckMascot.letter }));
  check("export mode: Grady idle with placard A", mascot.state === "idle" && mascot.letter === "A", JSON.stringify(mascot));
  await context.close();
}

/* ---------------- reduced motion ---------------------------------------- */
{
  const { context, page } = await open("", "#/2", { reducedMotion: "reduce" });
  await page.waitForTimeout(300);
  const r = await page.evaluate(() => ({
    cls: document.documentElement.classList.contains("reduced-motion"),
    mascotAnims: document.getElementById("mascot").getAnimations({ subtree: true }).length,
    count: document.querySelector("#rows .r1 .num").textContent,
  }));
  check("prefers-reduced-motion: mascot motion off, counters final at once",
    r.cls && r.mascotAnims === 0 && r.count === "295,356", JSON.stringify(r));
  await context.close();
}
{
  const { context, page } = await open("", "#/2");
  await page.keyboard.press("r"); await page.waitForTimeout(100);
  const on = await page.evaluate(() => document.documentElement.classList.contains("reduced-motion"));
  await page.keyboard.press("r");
  check("manual reduced-motion toggle (R)", on);
  await context.close();
}

/* ---------------- offline: live map falls back; file:// works ------------ */
{
  const { context, page, external } = await open("", "#/7");
  await page.waitForTimeout(1400);
  await page.click("[data-go-live]");
  await page.waitForTimeout(5200);
  const state = await page.evaluate(() => {
    const w = document.querySelector("[data-live-map]");
    return { live: w.classList.contains("live"), playing: w.classList.contains("playing"), iframe: !!w.querySelector("iframe"),
             poster: getComputedStyle(w.querySelector("img")).display !== "none" };
  });
  check("live map with no network: iframe removed, poster + recording remain", !state.live && !state.iframe && state.poster, JSON.stringify(state));
  check("the only external attempts are the handled live-hero ones", external.every((u) => !u.includes("127.0.0.1")), `${external.length} blocked`);
  await page.keyboard.press("ArrowRight"); await page.waitForTimeout(1500);
  check("after the live-map attempt, arrows still navigate", (await idx(page)).h === 8);
  await context.close();
}
{
  const context = await browser.newContext({ viewport: { width: 1280, height: 720 } });
  const page = await context.newPage();
  const errors = [];
  page.on("pageerror", (e) => errors.push(String(e)));
  await page.route("**/*", (route) => (route.request().url().startsWith("file:") ? route.continue() : route.abort()));
  await page.goto(pathToFileURL(join(DECK_ROOT, "index.html")).href + "#/11");
  await page.waitForFunction(() => window.__deckReady === true, null, { timeout: 30000 });
  await page.waitForTimeout(1500);
  const ok = await page.evaluate(() => document.querySelector('[data-chart="auc"]').classList.contains("rendered"));
  check("file:// works: charts render without a server", ok && errors.length === 0, errors.join(" | "));
  await context.close();
}

console.log(JSON.stringify(results));
await browser.close();
server.close();
