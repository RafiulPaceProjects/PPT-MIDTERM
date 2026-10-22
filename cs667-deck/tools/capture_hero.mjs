// Poster and rotation video of the 3D hero, rendered offline from
// data/maps.json (the hero layer data the notebook embedded in cell 44).
//
//   node tools/capture_hero.mjs          -> assets/img/hero_poster.png
//                                           assets/video/hero_rotate.mp4
import { chromium } from "playwright";
import { execFileSync } from "node:child_process";
import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { serve, DECK_ROOT } from "./lib/serve.mjs";

const server = await serve();
const browser = await chromium.launch({ args: ["--use-angle=swiftshader", "--enable-unsafe-swiftshader"] });

async function page(width, height, scale, query = "") {
  const p = await browser.newPage({ viewport: { width, height }, deviceScaleFactor: scale });
  await p.route("**/*", (route) =>
    route.request().url().startsWith(server.url) ? route.continue() : route.abort());
  await p.goto(`${server.url}/tools/hero/render.html${query}`);
  await p.waitForFunction(() => window.heroReady === true, null, { timeout: 30000 });
  return p;
}

// Poster: 1920x1080 at 2x, the notebook's own camera.
const poster = await page(1920, 1080, 2);
await poster.waitForTimeout(500);
await poster.screenshot({ path: join(DECK_ROOT, "assets/img/hero_poster.png") });
console.log("wrote assets/img/hero_poster.png");
await poster.close();

// The map slide's panel (about 930x620 on the slide): closer on the busy core.
const panel = await page(930, 624, 2, "?zoom=11.35&lat=40.715&lon=-73.93");
await panel.waitForTimeout(500);
await panel.screenshot({ path: join(DECK_ROOT, "assets/img/hero_poster_panel.png") });
console.log("wrote assets/img/hero_poster_panel.png");
await panel.close();
if (process.argv.includes("--posters-only")) { await browser.close(); server.close(); process.exit(0); }

// Video: one slow 10-second turn at 25 fps, 1280x720.
const frames = mkdtempSync(join(tmpdir(), "hero-"));
const video = await page(1280, 720, 1);
const start = -20;
for (let i = 0; i < 250; i++) {
  await video.evaluate((b) => window.setBearing(b), start + (360 * i) / 250);
  await video.waitForFunction(() => window.heroReady === true, null, { timeout: 5000 });
  await video.screenshot({ path: join(frames, `f${String(i).padStart(4, "0")}.png`) });
}
execFileSync("ffmpeg", ["-y", "-loglevel", "error", "-framerate", "25", "-i", join(frames, "f%04d.png"),
  "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "26", "-movflags", "+faststart",
  join(DECK_ROOT, "assets/video/hero_rotate.mp4")]);
// VP9 too, for browsers built without H.264
execFileSync("ffmpeg", ["-y", "-loglevel", "error", "-framerate", "25", "-i", join(frames, "f%04d.png"),
  "-c:v", "libvpx-vp9", "-b:v", "0", "-crf", "38", "-row-mt", "1", "-pix_fmt", "yuv420p",
  join(DECK_ROOT, "assets/video/hero_rotate.webm")]);
rmSync(frames, { recursive: true });
console.log("wrote assets/video/hero_rotate.mp4 and .webm");

await browser.close();
server.close();
