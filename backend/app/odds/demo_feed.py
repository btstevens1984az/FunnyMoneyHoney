"""Demo / offline odds feed with live-feeling updates (no API key required)."""

from __future__ import annotations

import json
import math
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path

from app.config import DATA_DIR
from app.odds.ranking import enrich_event
from app.schemas import Bookmaker, EventOdds, Market, Outcome

SAMPLE_PATH = DATA_DIR / "sample_odds.json"


def _load_templates() -> list[dict]:
    with SAMPLE_PATH.open(encoding="utf-8") as fh:
        return json.load(fh)


def _jitter(price: float, event_id: str, outcome_name: str, now: datetime) -> float:
    """Deterministic micro-moves so demo mode feels real-time without randomness chaos."""
    epoch = int(now.timestamp())
    # Update roughly every 15 seconds of wall clock
    tick = epoch // 15
    seed = sum(ord(c) for c in f"{event_id}:{outcome_name}") + tick
    wave = math.sin(seed / 7.0) * 0.025 + math.cos(seed / 11.0) * 0.01
    moved = price * (1.0 + wave)
    return round(max(1.05, min(moved, 25.0)), 2)


def build_demo_events(now: datetime | None = None) -> list[EventOdds]:
    now = now or datetime.now(timezone.utc)
    templates = _load_templates()
    events: list[EventOdds] = []

    for tmpl in templates:
        commence = now + timedelta(hours=float(tmpl["commence_offset_hours"]))
        books: list[Bookmaker] = []
        for book in tmpl["bookmakers"]:
            markets: list[Market] = []
            for market in book["markets"]:
                outcomes = [
                    Outcome(
                        name=o["name"],
                        price=_jitter(float(o["price"]), tmpl["id"], o["name"], now),
                        point=o.get("point"),
                    )
                    for o in market["outcomes"]
                ]
                markets.append(
                    Market(
                        key=market["key"],
                        last_update=now,
                        outcomes=outcomes,
                    )
                )
            books.append(
                Bookmaker(key=book["key"], title=book["title"], markets=markets)
            )

        event = EventOdds(
            id=tmpl["id"],
            sport_key=tmpl["sport_key"],
            sport_title=tmpl["sport_title"],
            commence_time=commence,
            home_team=tmpl["home_team"],
            away_team=tmpl["away_team"],
            bookmakers=books,
        )
        events.append(enrich_event(event))

    events.sort(key=lambda e: e.commence_time)
    return events


def demo_snapshot_payload(events: list[EventOdds]) -> list[dict]:
    return [deepcopy(e.model_dump(mode="json")) for e in events]


def sample_path() -> Path:
    return SAMPLE_PATH
