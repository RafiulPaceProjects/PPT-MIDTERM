// Headless screenshots of every slide, plus each slide's speaker notes.
// Build-time tooling only.
//
//   node tools/capture_slides.mjs                 export mode, 1920x1080 -> export/slides/
//   node tools/capture_slides.mjs --live --size 1280x720 --out /tmp/x --slides 0,7
//
// Every request that leaves localhost is blocked and reported: the deck must
// run with the network off (INV-6). Console errors are reported too.
import { chromium } from "playwright";
import { mkdirSync, writeFileSync } from "node:fs";
import { join, resolve } from "node:path";
import { serve, DECK_ROOT } from "./lib/serve.mjs";

const args = process.argv.slice(2);
const opt = (name, dflt) => { const i = args.indexOf(name); return i >= 0 ? args[i + 1] : dflt; };
const live = args.includes("--live");
const [W, H] = opt("--size", "1920x1080").split("x").map(Number);
const out = resolve(opt("--out", join(DECK_ROOT, "export/slides")));
const only = opt("--slides", null)?.split(",").map(Number);
const scale = Number(opt("--scale", "1"));
const wait = Number(opt("--wait", live ? "2600" : "150"));
const query = opt("--query", live ? "" : "?export=1");

mkdirSync(out, { recursive: true });
const server = await serve();
const browser = await chromium.launch();
const context = await browser.newContext({ viewport: { width: W, height: H }, deviceScaleFactor: scale,
  reducedMotion: args.includes("--reduced") ? "reduce" : "no-preference" });
const page = await context.newPage();
const external = [], failed = [], errors = [];
await page.route("**/*", (route) => {
  const url = route.request().url();
  if (url.startsWith(server.url) || url.startsWith("data:") || url.startsWith("blob:")) return route.continue();
  external.push(url);
  return route.abort();
});
page.on("requestfailed", (r) => { if (r.url().startsWith(server.url)) failed.push(r.url()); });
page.on("response", (r) => { if (r.status() >= 400) failed.push(`${r.status()} ${r.url()}`); });
page.on("console", (m) => { if (m.type() === "error") errors.push(m.text()); });
page.on("pageerror", (e) => errors.push(e.stack || String(e)));

await page.goto(`${server.url}/index.html${query}#/0`);
await page.waitForFunction(() => window.__deckReady === true, null, { timeout: 30000 });
const total = await page.evaluate(() => Reveal.getTotalSlides());
const notes = [];
for (let i = 0; i < total; i++) {
  if (only && !only.includes(i)) continue;
  // live: land before the fragments; export: every fragment shown (the final state)
  await page.evaluate(([n, f]) => Reveal.slide(n, 0, f), [i, live ? -1 : 99]);
  await page.waitForTimeout(wait);
  await page.evaluate(() => document.fonts.ready);
  const file = join(out, `slide-${String(i + 1).padStart(2, "0")}.png`);
  await page.screenshot({ path: file });
  notes.push(await page.evaluate(() => {
    const s = Reveal.getCurrentSlide();
    const n = s.querySelector("aside.notes");
    return { index: Reveal.getIndices().h, id: s.id, title: (s.querySelector("h1, h2")?.innerText || "").trim(),
             notes: n ? n.innerText.trim() : "" };
  }));
}
writeFileSync(join(out, "notes.json"), JSON.stringify(notes, null, 1));
console.log(`captured ${notes.length} of ${total} slides -> ${out}`);
if (external.length) console.log("blocked external requests:\n  " + [...new Set(external)].join("\n  "));
if (failed.length) console.log("failed local requests:\n  " + [...new Set(failed)].join("\n  "));
if (errors.length) console.log("console errors:\n  " + [...new Set(errors)].join("\n  "));
await browser.close();
server.close();
process.exitCode = external.length || failed.length || errors.length ? 2 : 0;
