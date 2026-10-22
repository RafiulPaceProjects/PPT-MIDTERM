// Review gallery: Grady in each of the ten states, enlarged. Build-time only.
//   node tools/mascot_states.mjs <out.png>
import { chromium } from "playwright";
import { serve } from "./lib/serve.mjs";

const out = process.argv[2] || "mascot_states.png";
const server = await serve();
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 3 });
await page.goto(`${server.url}/index.html#/16`);
await page.waitForFunction(() => window.__deckReady === true);
await page.waitForTimeout(4000);
const states = [
  ["idle", (m) => m.setState("idle")],
  ["tracking", (m) => { m.setState("tracking"); m.lockPupils({ x: 200, y: 200 }); }],
  ["hover-delight", (m) => { m.lockPupils(null); m.setState("hover-delight"); }],
  ["click-pop", (m) => m.pop("B")],
  ["thinking", (m) => m.think(null)],
  ["warning", (m) => { m.releaseCue(); m.warn({ ms: null, letter: "C" }); }],
  ["celebrating", (m) => { m.releaseCue(); m.celebrate(); }],
  ["dizzy", (m) => { m.releaseCue(); m.setState("dizzy"); }],
  ["sleeping", (m) => { m.setState("sleeping"); }],
  ["pointing", (m) => { m.setState("idle"); m.point(".slide-foot"); }],
];
const shots = [];
for (const [name, fn] of states) {
  await page.evaluate(`(${fn.toString()})(window.DeckMascot)`);
  await page.waitForTimeout(name === "celebrating" ? 400 : name === "pointing" ? 300 : 250);
  const box = await page.locator("#mascot-layer").boundingBox();
  shots.push({ name, buf: await page.screenshot({ clip: { x: box.x - 24, y: box.y - 20, width: box.width + 40, height: box.height + 26 } }),
               state: await page.evaluate(() => window.DeckMascot.state) });
}
// tile them with labels in a plain page
const html = `<body style="margin:0;font:600 28px Inter, sans-serif;background:#fff;display:flex;flex-wrap:wrap;gap:24px;padding:24px;width:2200px">` +
  shots.map((s) => `<figure style="margin:0;text-align:center"><img style="width:400px" src="data:image/png;base64,${s.buf.toString("base64")}"><figcaption>${s.name} (${s.state})</figcaption></figure>`).join("") + "</body>";
const sheet = await browser.newPage({ viewport: { width: 2250, height: 1300 } });
await sheet.setContent(html);
await sheet.screenshot({ path: out, fullPage: true });
console.log("wrote", out);
await browser.close();
server.close();
