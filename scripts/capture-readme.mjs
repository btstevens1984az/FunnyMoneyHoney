/**
 * Capture real UI PNG stills + 8–12s looping GIFs for the README.
 * Prerequisites: API :8000, UI (default :5176 or FMH_URL), Playwright Chromium, ffmpeg.
 *
 *   FMH_URL=http://127.0.0.1:5176 node capture-readme.mjs
 */
import { chromium } from "playwright";
import { spawnSync } from "node:child_process";
import { mkdirSync, rmSync, existsSync, readdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const root = join(__dirname, "..");
const stillDir = join(root, "media");
const outDir = join(root, "media", "readme");
const tmp = join(__dirname, ".capture-tmp");

mkdirSync(stillDir, { recursive: true });
mkdirSync(outDir, { recursive: true });
rmSync(tmp, { recursive: true, force: true });
mkdirSync(tmp, { recursive: true });

const BASE = process.env.FMH_URL || "http://127.0.0.1:5173";
const SECONDS = 9;
const FPS = 6;

const shots = [
  {
    name: "01-odds-table",
    prep: async (page) => {
      await page.waitForSelector('[data-testid="odds-table"] tbody tr');
      await page.evaluate(() => window.scrollTo(0, 0));
      await page.waitForTimeout(400);
    },
  },
  {
    name: "02-probability",
    prep: async (page) => {
      await page.locator('[data-testid="odds-table"] tbody tr').first().click();
      await page.waitForSelector('[data-testid="probability-view"] .recharts-wrapper');
      await page.locator('[data-testid="probability-view"]').scrollIntoViewIfNeeded();
      await page.waitForTimeout(600);
    },
  },
  {
    name: "03-bankroll",
    prep: async (page) => {
      await page.locator('[data-testid="bankroll-sim"]').scrollIntoViewIfNeeded();
      await page.getByRole("button", { name: "Simulate" }).click();
      await page.waitForSelector('[data-testid="bankroll-sim"] .recharts-wrapper', {
        timeout: 15000,
      });
      await page.waitForSelector('[data-testid="thinking-panel"] .font-mono');
      await page.waitForTimeout(1000);
    },
  },
  {
    name: "04-dashboard",
    prep: async (page) => {
      await page.evaluate(() => window.scrollTo(0, 0));
      await page.waitForSelector('[data-testid="odds-table"] tbody tr');
      await page.waitForSelector('[data-testid="alerts-panel"]');
      await page.waitForTimeout(1200);
    },
  },
];

function hasFfmpeg() {
  return spawnSync("ffmpeg", ["-version"], { encoding: "utf8" }).status === 0;
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
    "scale=960:-1:flags=lanczos,split[s0][s1];[s0]palettegen=stats_mode=diff[p];[s1][p]paletteuse=dither=bayer",
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

console.log("Capturing from", BASE);
const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({
  viewport: { width: 1440, height: 900 },
  deviceScaleFactor: 1,
});

await page.goto(BASE, { waitUntil: "networkidle", timeout: 60000 });
await page.waitForSelector('[data-testid="odds-table"] tbody tr', { timeout: 30000 });
await page.waitForSelector('[data-testid="disclaimer"]');
await page.waitForFunction(
  () => document.querySelectorAll('[data-testid="odds-table"] tbody tr').length >= 3,
);
await page.waitForTimeout(1200);

for (const shot of shots) {
  console.log("Capturing", shot.name);
  await shot.prep(page);

  const stillPng = join(stillDir, `${shot.name}.png`);
  await page.screenshot({ path: stillPng, fullPage: false });
  console.log("  still", stillPng);

  const frameDir = join(tmp, shot.name);
  mkdirSync(frameDir, { recursive: true });
  const total = SECONDS * FPS;
  let written = 0;
  for (let i = 0; i < total; i++) {
    const file = join(frameDir, `frame-${String(i).padStart(3, "0")}.png`);
    try {
      await page.screenshot({ path: file, fullPage: false });
      written += 1;
    } catch (err) {
      console.warn("  frame skip", i, err instanceof Error ? err.message : err);
      break;
    }
    await page.waitForTimeout(1000 / FPS);
  }
  const gifPath = join(outDir, `${shot.name}.gif`);
  if (written >= 6) {
    framesToGif(frameDir, gifPath);
    console.log("  gif", gifPath, `(${written} frames)`);
  } else {
    console.warn("  gif skipped — not enough frames; keeping prior GIF if present");
  }
}

await browser.close();
rmSync(tmp, { recursive: true, force: true });

const gifs = readdirSync(outDir).filter((f) => f.endsWith(".gif"));
const pngs = readdirSync(stillDir).filter((f) => f.endsWith(".png"));
console.log("Done. PNG stills:", pngs.join(", "));
console.log("Done. GIFs:", gifs.join(", ") || "(none)");
