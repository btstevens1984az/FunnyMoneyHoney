"""Relative safety / value ranking across markets (educational only)."""

from __future__ import annotations

from collections import defaultdict

from app.odds.probability import risk_flag_for_value
from app.schemas import EventOdds, RankedOutcome


def _market_raw_probs(outcomes) -> list[float] | None:
    raw = [1.0 / o.price for o in outcomes if o.price > 1.0]
    if not raw or len(raw) != len(outcomes):
        return None
    return raw


def _consensus_and_counts(
    event: EventOdds,
) -> tuple[dict[tuple[str, str], float], dict[tuple[str, str], int]]:
    """Average de-vigged probs across books + how many books quoted each outcome."""
    buckets: dict[tuple[str, str], list[float]] = defaultdict(list)
    for book in event.bookmakers:
        for market in book.markets:
            raw = _market_raw_probs(market.outcomes)
            if not raw:
                continue
            total = sum(raw)
            for outcome, implied in zip(market.outcomes, raw, strict=True):
                buckets[(market.key, outcome.name)].append(implied / total)

    consensus = {key: sum(vals) / len(vals) for key, vals in buckets.items() if vals}
    counts = {key: len(vals) for key, vals in buckets.items()}
    return consensus, counts


def enrich_event(event: EventOdds) -> EventOdds:
    """Mutate markets with implied/fair probs, relative value, and risk flags."""
    consensus, counts = _consensus_and_counts(event)
    best_value = -999.0
    best_label: str | None = None
    worst_flag = "ok"

    for book in event.bookmakers:
        for market in book.markets:
            raw = _market_raw_probs(market.outcomes)
            if not raw:
                continue
            total = sum(raw)
            overround = total - 1.0
            market.overround = round(overround, 4)
            local_fair = [p / total for p in raw]

            for idx, outcome in enumerate(market.outcomes):
                key = (market.key, outcome.name)
                fair = consensus.get(key, local_fair[idx])
                outcome.implied_probability = round(raw[idx], 4)
                outcome.fair_probability = round(fair, 4)
                outcome.overround_share = round(raw[idx] - local_fair[idx], 4)

                # Cross-book edge only when ≥2 books quote this outcome.
                # Single-book vig-removed "EV" is identical for every side — not useful.
                if counts.get(key, 1) >= 2:
                    outcome.relative_value = round(fair * outcome.price - 1.0, 4)
                else:
                    outcome.relative_value = 0.0

                flag, reason = risk_flag_for_value(outcome.relative_value, overround)
                outcome.risk_flag = flag  # type: ignore[assignment]
                outcome.risk_reason = reason

                if flag == "pull":
                    worst_flag = "pull"
                elif flag == "caution" and worst_flag == "ok":
                    worst_flag = "caution"

                score = (outcome.relative_value, outcome.fair_probability)
                best_score = (best_value, -1.0)
                if score > best_score:
                    best_value = outcome.relative_value
                    best_label = f"{outcome.name} @ {book.title} ({market.key})"

            order = sorted(
                range(len(market.outcomes)),
                key=lambda i: (
                    market.outcomes[i].relative_value,
                    market.outcomes[i].fair_probability,
                ),
                reverse=True,
            )
            for rank, idx in enumerate(order, start=1):
                market.outcomes[idx].safety_rank = rank

    event.best_value_outcome = best_label
    event.alert_level = worst_flag  # type: ignore[assignment]
    if worst_flag == "pull":
        event.analysis_summary = (
            "At least one priced outcome shows a strong educational pull/caution signal "
            "(price worse than consensus fair odds, or high overround)."
        )
    elif worst_flag == "caution":
        event.analysis_summary = (
            "Some outcomes show muted educational value vs consensus fair odds — review carefully."
        )
    else:
        event.analysis_summary = (
            "Markets enriched with consensus fair probabilities and relative value vs those odds. "
            "Educational metrics only."
        )
    return event


def flatten_rankings(events: list[EventOdds], limit: int = 40) -> list[RankedOutcome]:
    rows: list[RankedOutcome] = []
    for event in events:
        matchup = f"{event.away_team} @ {event.home_team}"
        for book in event.bookmakers:
            for market in book.markets:
                for outcome in market.outcomes:
                    note = (
                        "vs consensus fair odds"
                        if abs(outcome.relative_value) > 1e-9
                        else "single-book quote (no cross-book edge signal)"
                    )
                    analysis = (
                        f"Implied {outcome.implied_probability:.1%} → fair "
                        f"{outcome.fair_probability:.1%}; book overround {market.overround:.1%}. "
                        f"Relative value {outcome.relative_value:+.2%} ({note})."
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
    rows.sort(key=lambda r: (r.relative_value, r.fair_probability), reverse=True)
    for i, row in enumerate(rows, start=1):
        row.safety_rank = i
    return rows[:limit]
