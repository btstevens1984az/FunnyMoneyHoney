"""Relative safety / value ranking across markets (educational only)."""

from __future__ import annotations

from app.odds.probability import risk_flag_for_value
from app.schemas import EventOdds, RankedOutcome


def enrich_event(event: EventOdds) -> EventOdds:
    """Mutate markets with implied/fair probs, relative value, and risk flags."""
    best_value = -999.0
    best_label: str | None = None
    worst_flag = "ok"

    for book in event.bookmakers:
        for market in book.markets:
            raw = [1.0 / o.price for o in market.outcomes if o.price > 1.0]
            if not raw or len(raw) != len(market.outcomes):
                continue
            total = sum(raw)
            overround = total - 1.0
            market.overround = round(overround, 4)
            fair = [p / total for p in raw]

            scored: list[tuple[int, float]] = []
            for idx, outcome in enumerate(market.outcomes):
                outcome.implied_probability = round(raw[idx], 4)
                outcome.fair_probability = round(fair[idx], 4)
                outcome.overround_share = round(raw[idx] - fair[idx], 4)
                outcome.relative_value = round(fair[idx] * outcome.price - 1.0, 4)
                flag, reason = risk_flag_for_value(outcome.relative_value, overround)
                outcome.risk_flag = flag  # type: ignore[assignment]
                outcome.risk_reason = reason
                scored.append((idx, outcome.relative_value))
                if flag == "pull":
                    worst_flag = "pull"
                elif flag == "caution" and worst_flag == "ok":
                    worst_flag = "caution"
                if outcome.relative_value > best_value:
                    best_value = outcome.relative_value
                    best_label = f"{outcome.name} @ {book.title} ({market.key})"

            # Higher relative value ⇒ safer educational rank (1 = best in market)
            scored.sort(key=lambda t: t[1], reverse=True)
            for rank, (idx, _) in enumerate(scored, start=1):
                market.outcomes[idx].safety_rank = rank

    event.best_value_outcome = best_label
    event.alert_level = worst_flag  # type: ignore[assignment]
    if worst_flag == "pull":
        event.analysis_summary = (
            "At least one priced outcome shows a strong educational pull/caution signal "
            "(negative relative value or high overround)."
        )
    elif worst_flag == "caution":
        event.analysis_summary = (
            "Some outcomes show muted educational value after vig removal — review carefully."
        )
    else:
        event.analysis_summary = (
            "Markets enriched with fair probabilities after overround removal. "
            "Relative value is an educational metric only."
        )
    return event


def flatten_rankings(events: list[EventOdds], limit: int = 40) -> list[RankedOutcome]:
    rows: list[RankedOutcome] = []
    for event in events:
        matchup = f"{event.away_team} @ {event.home_team}"
        for book in event.bookmakers:
            for market in book.markets:
                for outcome in market.outcomes:
                    analysis = (
                        f"Implied {outcome.implied_probability:.1%} → fair {outcome.fair_probability:.1%} "
                        f"after removing {market.overround:.1%} overround. "
                        f"Relative value {outcome.relative_value:+.2%}."
                    )
                    rows.append(
                        RankedOutcome(
                            event_id=event.id,
                            sport_title=event.sport_title,
                            matchup=matchup,
                            commence_time=event.commence_time,
                            bookmaker=book.title,
                            market=market.key,
                            outcome=outcome.name,
                            price=outcome.price,
                            implied_probability=outcome.implied_probability,
                            fair_probability=outcome.fair_probability,
                            relative_value=outcome.relative_value,
                            safety_rank=outcome.safety_rank,
                            risk_flag=outcome.risk_flag,
                            risk_reason=outcome.risk_reason,
                            analysis=analysis,
                        )
                    )
    rows.sort(key=lambda r: r.relative_value, reverse=True)
    # Re-number global safety rank
    for i, row in enumerate(rows, start=1):
        row.safety_rank = i
    return rows[:limit]
