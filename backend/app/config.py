from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = Path(__file__).resolve().parents[1] / "data"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "FunnyMoneyHoney"
    demo_mode: bool = True
    odds_api_key: str = ""
    odds_api_base: str = "https://api.the-odds-api.com/v4"
    database_url: str = "sqlite:///./funnymoneyhoney.db"
    cors_origins: str = "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173"
    default_daily_stake: float = 1000.0
    refresh_seconds: int = 30
    sports: str = "basketball_nba,americanfootball_nfl,baseball_mlb,icehockey_nhl,soccer_epl"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def sport_keys(self) -> list[str]:
        return [s.strip() for s in self.sports.split(",") if s.strip()]

    @property
    def live_api_enabled(self) -> bool:
        return bool(self.odds_api_key.strip()) and not self.demo_mode


@lru_cache
def get_settings() -> Settings:
    return Settings()
