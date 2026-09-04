from fastapi import APIRouter

from app import __version__
from app.config import get_settings
from app.schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    settings = get_settings()
    mode = "live" if settings.live_api_enabled else "demo"
    return HealthResponse(
        status="ok",
        version=__version__,
        mode=mode,  # type: ignore[arg-type]
        demo_mode=settings.demo_mode or not settings.odds_api_key,
        live_api_configured=bool(settings.odds_api_key.strip()),
    )
