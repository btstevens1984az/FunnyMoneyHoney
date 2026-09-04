# Media regeneration

README screenshots and GIFs live in `media/` and `media/readme/`.

## Placeholder assets

SVG stills ship by default so the README renders immediately. Replace them with real captures when you can.

## Capture live GIFs (Playwright + ffmpeg)

Requires the API on `:8000` and the UI on `:5173`.

```bash
# terminal 1
cd backend && source .venv/bin/activate
uvicorn app.main:app --reload --port 8000

# terminal 2
cd frontend && npm run dev

# terminal 3
cd scripts
npm install
npx playwright install chromium
node capture-readme.mjs
```

Outputs (≈8–12s loops):

- `media/readme/01-odds-table.gif`
- `media/readme/02-probability.gif`
- `media/readme/03-bankroll.gif`
- `media/readme/04-dashboard.gif`

Optional MP4s are written alongside if `ffmpeg` is on `PATH`.

## Topics for GitHub

Suggested repository topics:

`sports-odds` `fastapi` `react` `typescript` `tailwind` `docker` `odds-api` `educational` `self-hosted` `recharts`
