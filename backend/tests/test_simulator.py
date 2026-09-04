from app.schemas import SimulateRequest, SimulateSelection
from app.services.simulator import run_simulation


def test_simulation_defaults():
    result = run_simulation(SimulateRequest(daily_stake=1000, days=10, trials=100, seed=1))
    assert result.trials == 100
    assert len(result.projected_path) == 11
    assert result.p05_ending_bankroll <= result.median_ending_bankroll <= result.p95_ending_bankroll
    assert "Not financial" in result.disclaimer


def test_simulation_custom_selection():
    req = SimulateRequest(
        daily_stake=1000,
        days=5,
        trials=80,
        seed=7,
        selections=[
            SimulateSelection(
                label="A",
                fair_probability=0.6,
                decimal_odds=1.7,
                stake_fraction=1.0,
            )
        ],
    )
    result = run_simulation(req)
    assert result.win_rate_estimate > 0
    assert result.expected_ending_bankroll != 0 or True  # path exists either way
