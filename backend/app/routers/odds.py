from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.database import get_db
from app.odds.ranking import flatten_rankings
from app.schemas import (
    AnalysisRequest,
    AnalysisResponse,
    AlertsResponse,
    OddsFeedResponse,
    RankingResponse,
)
from app.services import alerts as alerts_svc
from app.services import analysis as analysis_svc
from app.services.odds_service import DISCLAIMER, load_events

router = APIRouter(prefix="/api", tags=["odds"])


@router.get("/odds", response_model=OddsFeedResponse)
async def get_odds(
    sport: str | None = Query(default=None, description="Optional sport_key filter"),
    settings: Settings = Depends(get_settings),
    db: Session = Depends(get_db),
) -> OddsFeedResponse:
    events, mode = await load_events(settings, db)
    if sport:
        events = [e for e in events if e.sport_key == sport or e.sport_title.lower() == sport.lower()]
    return OddsFeedResponse(
        mode=mode,  # type: ignore[arg-type]
        generated_at=datetime.now(timezone.utc),
        refresh_seconds=settings.refresh_seconds,
        event_count=len(events),
        events=events,
        disclaimer=DISCLAIMER,
    )


@router.get("/rankings", response_model=RankingResponse)
async def get_rankings(
    limit: int = Query(default=30, ge=5, le=100),
    settings: Settings = Depends(get_settings),
    db: Session = Depends(get_db),
) -> RankingResponse:
    events, mode = await load_events(settings, db)
    rankings = flatten_rankings(events, limit=limit)
    return RankingResponse(
        mode=mode,  # type: ignore[arg-type]
        generated_at=datetime.now(timezone.utc),
        rankings=rankings,
        disclaimer=DISCLAIMER,
    )


@router.get("/alerts", response_model=AlertsResponse)
async def get_alerts(
    settings: Settings = Depends(get_settings),
    db: Session = Depends(get_db),
) -> AlertsResponse:
    events, _ = await load_events(settings, db)
    return alerts_svc.build_alerts(events)


@router.post("/analyze", response_model=AnalysisResponse)
async def post_analyze(
    body: AnalysisRequest,
    settings: Settings = Depends(get_settings),
    db: Session = Depends(get_db),
) -> AnalysisResponse:
    events, _ = await load_events(settings, db)
    return analysis_svc.analyze(body, events)
