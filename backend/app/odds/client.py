"""The Odds API client — public REST API only (no scraping, no sportsbook login)."""

from __future__ import annotations

from datetime import datetime, timezone

import httpx

from app.config import Settings
from app.odds.ranking import enrich_event
from app.schemas import Bookmaker, EventOdds, Market, Outcome


def _parse_event(raw: dict) -> EventOdds:
    books: list[Bookmaker] = []
    for book in raw.get("bookmakers", []):
        markets: list[Market] = []
        for market in book.get("markets", []):
            last = market.get("last_update")
            last_dt = None
            if last:
                last_dt = datetime.fromisoformat(last.replace("Z", "+00:00"))
            outcomes = [
                Outcome(
                    name=o["name"],
                    price=float(o["price"]),
                    point=o.get("point"),
                )
                for o in market.get("outcomes", [])
            ]
            markets.append(
                Market(key=market["key"], last_update=last_dt, outcomes=outcomes)
            )
        books.append(
            Bookmaker(key=book["key"], title=book["title"], markets=markets)
        )

    commence = datetime.fromisoformat(raw["commence_time"].replace("Z", "+00:00"))
    event = EventOdds(
        id=raw["id"],
        sport_key=raw["sport_key"],
        sport_title=raw.get("sport_title") or raw["sport_key"],
        commence_time=commence,
        home_team=raw["home_team"],
        away_team=raw["away_team"],
        bookmakers=books,
    )
    return enrich_event(event)


async def fetch_live_odds(settings: Settings) -> list[EventOdds]:
    if not settings.odds_api_key.strip():
        raise RuntimeError("ODDS_API_KEY is not configured")

    events: list[EventOdds] = []
    params = {
        "apiKey": settings.odds_api_key,
        "regions": "us",
        "markets": "h2h,spreads,totals",
        "oddsFormat": "decimal",
        "dateFormat": "iso",
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        for sport in settings.sport_keys:
            url = f"{settings.odds_api_base}/sports/{sport}/odds"
            resp = await client.get(url, params=params)
            if resp.status_code == 404:
                continue
            resp.raise_for_status()
            payload = resp.json()
            for item in payload:
                events.append(_parse_event(item))

    events.sort(key=lambda e: e.commence_time or datetime.now(timezone.utc))
    return events
