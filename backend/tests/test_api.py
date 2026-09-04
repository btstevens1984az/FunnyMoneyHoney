import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path / 'test.db'}")
    monkeypatch.setenv("DEMO_MODE", "true")
    monkeypatch.setenv("ODDS_API_KEY", "")
    from app.config import get_settings
    from app.database import reset_engine

    get_settings.cache_clear()
    reset_engine()
    app = create_app()
    with TestClient(app) as c:
        yield c
    get_settings.cache_clear()
    reset_engine()


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["mode"] == "demo"


def test_odds_demo(client):
    r = client.get("/api/odds")
    assert r.status_code == 200
    body = r.json()
    assert body["mode"] == "demo"
    assert body["event_count"] >= 1
    assert body["events"][0]["bookmakers"][0]["markets"][0]["outcomes"][0]["implied_probability"] > 0
    assert "Not financial" in body["disclaimer"]


def test_rankings_and_alerts(client):
    r = client.get("/api/rankings")
    assert r.status_code == 200
    assert len(r.json()["rankings"]) >= 1
    a = client.get("/api/alerts")
    assert a.status_code == 200
    assert len(a.json()["alerts"]) >= 1


def test_analyze_and_simulate(client):
    odds = client.get("/api/odds").json()
    event = odds["events"][0]
    outcome = event["bookmakers"][0]["markets"][0]["outcomes"][0]
    analysis = client.post(
        "/api/analyze",
        json={"event_id": event["id"], "outcome_name": outcome["name"]},
    )
    assert analysis.status_code == 200
    assert analysis.json()["educational_score"] >= 0
    assert len(analysis.json()["thinking"]) >= 3

    sim = client.post(
        "/api/simulate",
        json={"daily_stake": 1000, "days": 7, "trials": 50, "seed": 3},
    )
    assert sim.status_code == 200
    assert "projected_path" in sim.json()
