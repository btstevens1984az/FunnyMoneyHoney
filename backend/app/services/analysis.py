"""Transparent educational 'thinking' analysis — not a prediction engine."""

from __future__ import annotations

from app.schemas import AnalysisRequest, AnalysisResponse, EventOdds

DISCLAIMER = (
    "Not financial or gambling advice. The educational score is a transparent heuristic "
    "derived from odds math (implied probability, overround, relative value). "
    "It is not a proven win rate, not AI clairvoyance, and does not predict future outcomes. "
    "Gambling involves risk of loss."
)


def analyze(
    req: AnalysisRequest,
    events: list[EventOdds] | None = None,
) -> AnalysisResponse:
    thinking: list[str] = [
        "Collect market prices and convert decimal odds → raw implied probabilities.",
        "Sum market implied probabilities to measure bookmaker overround (vig).",
        "Normalize to fair probabilities that sum to 100% (vig-removed).",
        "Compute relative value = fair_probability × decimal_odds − 1.",
        "Flag caution/pull when relative value is negative or overround is elevated.",
    ]

    fair = req.fair_probability
    odds = req.decimal_odds
    label = req.outcome_name or "selected outcome"

    if events and req.event_id:
        for event in events:
            if event.id != req.event_id:
                continue
            thinking.append(
                f"Matched event {event.away_team} @ {event.home_team} ({event.sport_title})."
            )
            for book in event.bookmakers:
                for market in book.markets:
                    for outcome in market.outcomes:
                        if req.outcome_name and outcome.name != req.outcome_name:
                            continue
                        fair = outcome.fair_probability
                        odds = outcome.price
                        label = outcome.name
                        thinking.append(
                            f"{book.title}/{market.key}: price {odds:.2f}, "
                            f"implied {outcome.implied_probability:.1%}, "
                            f"fair {fair:.1%}, relative value {outcome.relative_value:+.2%}."
                        )
                        if fair is not None and odds is not None:
                            break

    score = 50.0
    recommendation = "study"

    if fair is not None and odds is not None and odds > 1:
        rel = fair * odds - 1.0
        thinking.append(f"Relative value for {label}: {rel:+.2%}.")
        score = max(0.0, min(100.0, 50.0 + rel * 200.0))
        if rel <= -0.08:
            recommendation = "avoid"
            thinking.append(
                "Deeply negative relative value → educational recommendation: avoid / pull attention."
            )
        elif rel <= -0.03:
            recommendation = "caution"
            thinking.append(
                "Slightly negative relative value → educational recommendation: caution."
            )
        else:
            recommendation = "study"
            thinking.append(
                "Relative value not deeply negative → still study-only; no stake recommendation."
            )
    else:
        thinking.append("Insufficient price/probability inputs — defaulting to study-only posture.")

    thinking.append(
        "Important: this score is not a 99.x% success claim. No model here asserts historical profit."
    )

    summary = (
        f"Educational analysis for {label}: score {score:.0f}/100 with recommendation "
        f"'{recommendation}'. Use as a learning lens on odds structure, not as a tip sheet."
    )

    return AnalysisResponse(
        thinking=thinking,
        educational_score=round(score, 1),
        recommendation=recommendation,  # type: ignore[arg-type]
        summary=summary,
        disclaimer=DISCLAIMER,
    )
