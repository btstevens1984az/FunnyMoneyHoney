"""Educational risk alerts — caution / pull signals from market metrics."""

from __future__ import annotations

from datetime import datetime, timezone

from app.schemas import AlertItem, AlertsResponse, EventOdds

DISCLAIMER = (
    "Not financial or gambling advice. Alerts are educational heuristics based on "
    "overround and relative-value math. They do not predict winners or guarantee loss avoidance."
)


def build_alerts(events: list[EventOdds]) -> AlertsResponse:
    alerts: list[AlertItem] = []
    now = datetime.now(timezone.utc)

    for event in events:
        matchup = f"{event.away_team} @ {event.home_team}"
        for book in event.bookmakers:
            for market in book.markets:
                if market.overround >= 0.10:
                    alerts.append(
                        AlertItem(
                            severity="caution",
                            title=f"High overround on {market.key}",
                            detail=(
                                f"{book.title} {market.key} overround is {market.overround:.1%}. "
                                "Educational tip: wide margins reduce any notion of value."
                            ),
                            event_id=event.id,
                            matchup=matchup,
                        )
                    )
                for outcome in market.outcomes:
                    if outcome.risk_flag == "pull":
                        alerts.append(
                            AlertItem(
                                severity="pull",
                                title=f"Pull / study signal: {outcome.name}",
                                detail=outcome.risk_reason
                                or "Relative value deeply negative after vig removal.",
                                event_id=event.id,
                                matchup=matchup,
                            )
                        )
                    elif outcome.risk_flag == "caution":
                        alerts.append(
                            AlertItem(
                                severity="caution",
                                title=f"Caution: {outcome.name}",
                                detail=outcome.risk_reason
                                or "Muted relative value after vig removal.",
                                event_id=event.id,
                                matchup=matchup,
                            )
                        )

        hours = (event.commence_time - now).total_seconds() / 3600.0
        if hours < 2 and event.alert_level == "pull":
            alerts.append(
                AlertItem(
                    severity="pull",
                    title="Event starting soon with weak educational metrics",
                    detail=(
                        f"{matchup} tips in under 2 hours and carries pull-level signals. "
                        "Educational guidance: do not chase — review or skip."
                    ),
                    event_id=event.id,
                    matchup=matchup,
                )
            )

    seen: set[str] = set()
    unique: list[AlertItem] = []
    for a in alerts:
        key = f"{a.severity}:{a.title}:{a.event_id}"
        if key in seen:
            continue
        seen.add(key)
        unique.append(a)

    severity_order = {"pull": 0, "caution": 1, "info": 2}
    unique.sort(key=lambda a: severity_order.get(a.severity, 9))

    if not unique:
        unique.append(
            AlertItem(
                severity="info",
                title="No pull alerts right now",
                detail="Markets look within normal educational thresholds after vig removal.",
            )
        )

    return AlertsResponse(generated_at=now, alerts=unique[:40], disclaimer=DISCLAIMER)
