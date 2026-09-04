from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class OddsSnapshot(Base):
    __tablename__ = "odds_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sport_key: Mapped[str] = mapped_column(String(64), index=True)
    event_id: Mapped[str] = mapped_column(String(128), index=True)
    payload_json: Mapped[str] = mapped_column(Text)
    captured_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, index=True)


class SimulationRun(Base):
    __tablename__ = "simulation_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    daily_stake: Mapped[float] = mapped_column(Float)
    days: Mapped[int] = mapped_column(Integer)
    selections_json: Mapped[str] = mapped_column(Text)
    result_json: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
