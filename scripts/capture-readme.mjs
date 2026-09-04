/**
 * Capture 8–12s looping GIFs for the README.
 * Prerequisites: API :8000, UI :5173, Playwright Chromium, ffmpeg on PATH (optional MP4).
 *
 *   node capture-readme.mjs
 */
import { chromium } from "playwright";
import { spawnSync } from "node:child_process";
import { mkdirSync, rmSync, existsSync, readdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const root = join(__dirname, "..");
const outDir = join(root, "media", "readme");
const tmp = join(__dirname, ".capture-tmp");

mkdirSync(outDir, { recursive: true });
rmSync(tmp, { recursive: true, force: true });
mkdirSync(tmp, { recursive: true });

const BASE = process.env.FMH_URL || "http://127.0.0.1:5173";
const SECONDS = 10;
const FPS = 8;

const shots = [
  {
    name: "01-odds-table",
    prep: async (page) => {
      await page.waitForSelector('[data-testid="odds-table"]');
    },
  },
  {
    name: "02-probability",
    prep: async (page) => {
      await page.waitForSelector('[data-testid="probability-view"]');
      await page.locator('[data-testid="odds-table"] tbody tr').first().click();
      await page.waitForTimeout(500);
    },
  },
  {
    name: "03-bankroll",
    prep: async (page) => {
      await page.waitForSelector('[data-testid="bankroll-sim"]');
      await page.getByRole("button", { name: "Simulate" }).click();
      await page.waitForTimeout(1200);
      await page.locator('[data-testid="bankroll-sim"]').scrollIntoViewIfNeeded();
    },
  },
  {
    name: "04-dashboard",
    prep: async (page) => {
      await page.waitForSelector('[data-testid="odds-table"]');
      await page.evaluate(() => window.scrollTo(0, 0));
    },
  },
];

function hasFfmpeg() {
  const r = spawnSync("ffmpeg", ["-version"], { encoding: "utf8" });
  return r.status === 0;
}

function framesToGif(frameDir, gifPath) {
  if (!hasFfmpeg()) {
    console.warn("ffmpeg not found — skipping GIF encode for", gifPath);
    return;
  }
  const args = [
    "-y",
    "-framerate",
    String(FPS),
    "-i",
    join(frameDir, "frame-%03d.png"),
    "-vf",
    "scale=960:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse",
    "-loop",
    "0",
    gifPath,
  ];
  const r = spawnSync("ffmpeg", args, { encoding: "utf8" });
  if (r.status !== 0) {
    console.error(r.stderr);
    throw new Error(`ffmpeg failed for ${gifPath}`);
  }
  const mp4 = gifPath.replace(/\.gif$/, ".mp4");
  spawnSync(
    "ffmpeg",
    [
      "-y",
      "-framerate",
      String(FPS),
      "-i",
      join(frameDir, "frame-%03d.png"),
      "-pix_fmt",
      "yuv420p",
      "-movflags",
      "+faststart",
      mp4,
    ],
    { encoding: "utf8" },
  );
}

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({
  viewport: { width: 1280, height: 800 },
  deviceScaleFactor: 1,
});

await page.goto(BASE, { waitUntil: "networkidle" });

for (const shot of shots) {
  console.log("Capturing", shot.name);
  await shot.prep(page);
  const frameDir = join(tmp, shot.name);
  mkdirSync(frameDir, { recursive: true });
  const total = SECONDS * FPS;
  for (let i = 0; i < total; i++) {
    const file = join(frameDir, `frame-${String(i).padStart(3, "0")}.png`);
    await page.screenshot({ path: file, fullPage: false });
    await page.waitForTimeout(1000 / FPS);
  }
  const gifPath = join(outDir, `${shot.name}.gif`);
  framesToGif(frameDir, gifPath);
  console.log("Wrote", existsSync(gifPath) ? gifPath : "(gif skipped)");
}

await browser.close();

// Keep a simple inventory note
const gifs = existsSync(outDir)
  ? readdirSync(outDir).filter((f) => f.endsWith(".gif"))
  : [];
console.log("Done. GIFs:", gifs.join(", ") || "(none — install ffmpeg)");
