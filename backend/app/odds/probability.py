"""Implied probability and overround helpers (educational metrics only)."""

from __future__ import annotations


def american_to_decimal(american: float) -> float:
    if american > 0:
        return 1.0 + (american / 100.0)
    return 1.0 + (100.0 / abs(american))


def decimal_to_implied(decimal_odds: float) -> float:
    if decimal_odds <= 1.0:
        raise ValueError("decimal odds must be > 1")
    return 1.0 / decimal_odds


def remove_overround(implied: list[float]) -> tuple[list[float], float]:
    """Normalize raw implied probs so they sum to 1.0 (remove bookmaker margin)."""
    total = sum(implied)
    if total <= 0:
        raise ValueError("implied probabilities must sum to a positive value")
    fair = [p / total for p in implied]
    overround = total - 1.0
    return fair, overround


def relative_value(fair_probability: float, decimal_odds: float) -> float:
    """
    Educational EV-style metric: fair_p * decimal_odds - 1.
    Positive ≈ market price above fair estimate after vig removal.
    """
    return fair_probability * decimal_odds - 1.0


def risk_flag_for_value(relative_value_score: float, overround: float) -> tuple[str, str | None]:
    """Heuristic caution / pull signals — not betting advice."""
    if overround >= 0.12 or relative_value_score <= -0.06:
        return (
            "pull",
            "Educational signal: this price is meaningfully worse than consensus fair odds, "
            "or market overround is high. Study or skip — do not chase.",
        )
    if overround >= 0.075 or relative_value_score <= -0.02:
        return (
            "caution",
            "Educational signal: muted or negative relative value vs consensus fair odds, "
            "or elevated overround. Treat as study-only.",
        )
    return "ok", None
