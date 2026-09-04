"""Odds feed orchestration with optional snapshot caching."""

from __future__ import annotations

import json
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.config import Settings
from app.models import OddsSnapshot
from app.odds import client, demo_feed
from app.schemas import EventOdds

DISCLAIMER = (
    "Not financial or gambling advice. Past or simulated results do not predict future outcomes. "
    "Gambling involves risk of loss. FunnyMoneyHoney is educational software only — "
    "it does not place bets or connect to sportsbook accounts."
)


async def load_events(settings: Settings, db: Session | None = None) -> tuple[list[EventOdds], str]:
    mode = "demo"
    if settings.live_api_enabled:
        try:
            events = await client.fetch_live_odds(settings)
            mode = "live"
        except Exception:
            events = demo_feed.build_demo_events()
            mode = "demo"
    else:
        events = demo_feed.build_demo_events()

    if db is not None and events:
        # Cache a compact snapshot for history / offline review
        for event in events[:20]:
            db.add(
                OddsSnapshot(
                    sport_key=event.sport_key,
                    event_id=event.id,
                    payload_json=json.dumps(event.model_dump(mode="json")),
                    captured_at=datetime.now(timezone.utc).replace(tzinfo=None),
                )
            )
        db.commit()

    return events, mode
