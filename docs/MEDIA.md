# Media regeneration

README screenshots and GIFs live in `media/` and `media/readme/`.

## Assets

| Path | Purpose |
|------|---------|
| `media/*.png` | Still screenshots for the README table |
| `media/readme/*.gif` | ~9s looping demos of the live UI |

Do **not** commit solid-color placeholder GIFs. Always capture from a running app.

## Capture live PNG + GIF (Playwright + ffmpeg)

Requires the API on `:8000` and the UI on `:5173` (or set `FMH_URL`).

```bash
# terminal 1 — API
cd backend && source .venv/bin/activate
uvicorn app.main:app --reload --port 8000

# terminal 2 — UI
cd frontend && npm run dev

# terminal 3 — capture
cd scripts
npm install
npx playwright install chromium
FMH_URL=http://127.0.0.1:5173 node capture-readme.mjs
```

Outputs:

- `media/01-odds-table.png` … `media/04-dashboard.png`
- `media/readme/01-odds-table.gif` … `media/readme/04-dashboard.gif`
- Optional MP4s beside the GIFs when `ffmpeg` is available

## Topics for GitHub

Suggested repository topics:

`sports-odds` `fastapi` `react` `typescript` `tailwind` `docker` `odds-api` `educational` `self-hosted` `recharts`
