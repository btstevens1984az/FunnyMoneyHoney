# Architecture

FunnyMoneyHoney is a self-hosted educational odds dashboard.

```
Browser (React + Tailwind + Recharts)
        │  /api/*
        ▼
FastAPI ──► demo_feed (bundled JSON + deterministic jitter)
        └─► The Odds API (optional, ODDS_API_KEY)
        └─► SQLAlchemy snapshots (SQLite / PostgreSQL)
```

## Modes

| Mode | When | Behavior |
|------|------|----------|
| **Demo** | `DEMO_MODE=true` or no API key | Bundled sample events; prices micro-move every ~15s |
| **Live** | `DEMO_MODE=false` + `ODDS_API_KEY` | Public The Odds API; falls back to demo on errors |

## Educational metrics

1. **Implied probability** = `1 / decimal_odds`
2. **Overround** = sum(implied) − 1
3. **Fair probability** = implied / sum(implied)
4. **Relative value** = fair × decimal_odds − 1
5. **Pull / caution** = heuristics on negative relative value or high overround

These are teaching tools. They are **not** predictions, tips, or a claimed win rate.

## Risk disclaimer

Not financial or gambling advice. Past or simulated results do not predict future outcomes. Gambling involves risk of loss.
