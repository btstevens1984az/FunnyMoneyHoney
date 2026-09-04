from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class Outcome(BaseModel):
    name: str
    price: float
    point: float | None = None
    implied_probability: float = 0.0
    fair_probability: float = 0.0
    overround_share: float = 0.0
    relative_value: float = 0.0
    safety_rank: int = 0
    risk_flag: Literal["ok", "caution", "pull"] = "ok"
    risk_reason: str | None = None


class Market(BaseModel):
    key: str
    last_update: datetime | None = None
    outcomes: list[Outcome] = Field(default_factory=list)
    overround: float = 0.0


class Bookmaker(BaseModel):
    key: str
    title: str
    markets: list[Market] = Field(default_factory=list)


class EventOdds(BaseModel):
    id: str
    sport_key: str
    sport_title: str
    commence_time: datetime
    home_team: str
    away_team: str
    bookmakers: list[Bookmaker] = Field(default_factory=list)
    best_value_outcome: str | None = None
    analysis_summary: str | None = None
    alert_level: Literal["ok", "caution", "pull"] = "ok"


class OddsFeedResponse(BaseModel):
    mode: Literal["demo", "live"]
    generated_at: datetime
    refresh_seconds: int
    event_count: int
    events: list[EventOdds]
    disclaimer: str


class RankedOutcome(BaseModel):
    event_id: str
    sport_title: str
    matchup: str
    commence_time: datetime
    bookmaker: str
    market: str
    outcome: str
    price: float
    implied_probability: float
    fair_probability: float
    relative_value: float
    safety_rank: int
    risk_flag: Literal["ok", "caution", "pull"]
    risk_reason: str | None = None
    analysis: str


class RankingResponse(BaseModel):
    mode: Literal["demo", "live"]
    generated_at: datetime
    rankings: list[RankedOutcome]
    disclaimer: str


class SimulateSelection(BaseModel):
    label: str
    fair_probability: float = Field(ge=0.01, le=0.99)
    decimal_odds: float = Field(gt=1.0)
    stake_fraction: float = Field(default=1.0, gt=0, le=1)


class SimulateRequest(BaseModel):
    daily_stake: float = Field(default=1000.0, gt=0, le=1_000_000)
    days: int = Field(default=30, ge=1, le=365)
    selections: list[SimulateSelection] = Field(default_factory=list)
    trials: int = Field(default=500, ge=50, le=5000)
    seed: int | None = None


class SimulateResponse(BaseModel):
    daily_stake: float
    days: int
    trials: int
    expected_ending_bankroll: float
    median_ending_bankroll: float
    p05_ending_bankroll: float
    p95_ending_bankroll: float
    win_rate_estimate: float
    projected_path: list[dict[str, float]]
    histogram: list[dict[str, float]]
    educational_note: str
    disclaimer: str


class AlertItem(BaseModel):
    severity: Literal["info", "caution", "pull"]
    title: str
    detail: str
    event_id: str | None = None
    matchup: str | None = None


class AlertsResponse(BaseModel):
    generated_at: datetime
    alerts: list[AlertItem]
    disclaimer: str


class AnalysisRequest(BaseModel):
    event_id: str | None = None
    outcome_name: str | None = None
    fair_probability: float | None = None
    decimal_odds: float | None = None
    context: dict[str, Any] | None = None


class AnalysisResponse(BaseModel):
    thinking: list[str]
    educational_score: float = Field(
        description="0–100 educational heuristic only — not a prediction of future success."
    )
    recommendation: Literal["study", "caution", "avoid"]
    summary: str
    disclaimer: str


class HealthResponse(BaseModel):
    status: str
    version: str
    mode: Literal["demo", "live"]
    demo_mode: bool
    live_api_configured: bool
