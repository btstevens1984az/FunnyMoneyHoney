"""Monte Carlo daily bankroll simulator — educational projections only."""

from __future__ import annotations

import random
from statistics import mean, median

from app.schemas import SimulateRequest, SimulateResponse, SimulateSelection

DISCLAIMER = (
    "Not financial or gambling advice. Past or simulated results do not predict future outcomes. "
    "Gambling involves risk of loss. FunnyMoneyHoney never places bets and has no sportsbook login."
)


def _default_selections() -> list[SimulateSelection]:
    return [
        SimulateSelection(
            label="Sample favorite (demo)",
            fair_probability=0.58,
            decimal_odds=1.80,
            stake_fraction=0.5,
        ),
        SimulateSelection(
            label="Sample underdog (demo)",
            fair_probability=0.42,
            decimal_odds=2.20,
            stake_fraction=0.5,
        ),
    ]


def run_simulation(req: SimulateRequest) -> SimulateResponse:
    selections = req.selections or _default_selections()
    rng = random.Random(req.seed if req.seed is not None else 42)

    endings: list[float] = []
    path_accum = [0.0] * (req.days + 1)
    wins = 0
    decisions = 0

    for _ in range(req.trials):
        bankroll = 0.0  # track P&L relative to staking plan; stake is flat daily
        daily_path = [0.0]
        for _day in range(req.days):
            day_pnl = 0.0
            remaining = 1.0
            for i, sel in enumerate(selections):
                frac = sel.stake_fraction if i < len(selections) - 1 else remaining
                remaining = max(0.0, remaining - frac)
                stake = req.daily_stake * frac
                decisions += 1
                if rng.random() < sel.fair_probability:
                    day_pnl += stake * (sel.decimal_odds - 1.0)
                    wins += 1
                else:
                    day_pnl -= stake
            bankroll += day_pnl
            daily_path.append(bankroll)
        endings.append(bankroll)
        for i, v in enumerate(daily_path):
            path_accum[i] += v

    endings_sorted = sorted(endings)
    p05 = endings_sorted[max(0, int(0.05 * len(endings_sorted)) - 1)]
    p95 = endings_sorted[min(len(endings_sorted) - 1, int(0.95 * len(endings_sorted)))]

    projected_path = [
        {"day": i, "expected_pnl": round(path_accum[i] / req.trials, 2)}
        for i in range(len(path_accum))
    ]

    # Histogram buckets
    lo, hi = min(endings), max(endings)
    buckets = 12
    width = (hi - lo) / buckets if hi != lo else 1.0
    hist = [{"bucket_start": round(lo + i * width, 2), "count": 0.0} for i in range(buckets)]
    for e in endings:
        idx = min(buckets - 1, int((e - lo) / width) if width else 0)
        hist[idx]["count"] += 1

    win_rate = wins / decisions if decisions else 0.0

    return SimulateResponse(
        daily_stake=req.daily_stake,
        days=req.days,
        trials=req.trials,
        expected_ending_bankroll=round(mean(endings), 2),
        median_ending_bankroll=round(median(endings), 2),
        p05_ending_bankroll=round(p05, 2),
        p95_ending_bankroll=round(p95, 2),
        win_rate_estimate=round(win_rate, 4),
        projected_path=projected_path,
        histogram=hist,
        educational_note=(
            "This Monte Carlo path uses your stated fair probabilities and prices. "
            "It is a teaching tool for variance and bankroll shape — not a forecast of real sports results. "
            "No historical profit figure or win-rate guarantee is claimed by this software."
        ),
        disclaimer=DISCLAIMER,
    )
