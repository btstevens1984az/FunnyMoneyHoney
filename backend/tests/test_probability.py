from app.odds.probability import (
    american_to_decimal,
    decimal_to_implied,
    relative_value,
    remove_overround,
    risk_flag_for_value,
)


def test_american_to_decimal():
    assert abs(american_to_decimal(-110) - (1 + 100 / 110)) < 1e-9
    assert abs(american_to_decimal(150) - 2.5) < 1e-9


def test_remove_overround_two_way():
    implied = [decimal_to_implied(1.91), decimal_to_implied(1.91)]
    fair, overround = remove_overround(implied)
    assert abs(sum(fair) - 1.0) < 1e-9
    assert overround > 0


def test_relative_value_and_flags():
    assert relative_value(0.55, 2.0) > 0
    flag, reason = risk_flag_for_value(-0.10, 0.05)
    assert flag == "pull"
    assert reason
    flag2, _ = risk_flag_for_value(0.02, 0.04)
    assert flag2 == "ok"


def test_consensus_relative_value_differs_across_books():
    from datetime import datetime, timezone

    from app.odds.ranking import enrich_event
    from app.schemas import Bookmaker, EventOdds, Market, Outcome

    event = EventOdds(
        id="t1",
        sport_key="basketball_nba",
        sport_title="NBA",
        commence_time=datetime.now(timezone.utc),
        home_team="Home",
        away_team="Away",
        bookmakers=[
            Bookmaker(
                key="a",
                title="BookA",
                markets=[
                    Market(
                        key="h2h",
                        outcomes=[
                            Outcome(name="Away", price=1.90),
                            Outcome(name="Home", price=1.95),
                        ],
                    )
                ],
            ),
            Bookmaker(
                key="b",
                title="BookB",
                markets=[
                    Market(
                        key="h2h",
                        outcomes=[
                            Outcome(name="Away", price=2.05),
                            Outcome(name="Home", price=1.80),
                        ],
                    )
                ],
            ),
        ],
    )
    enrich_event(event)
    away_a = event.bookmakers[0].markets[0].outcomes[0].relative_value
    away_b = event.bookmakers[1].markets[0].outcomes[0].relative_value
    assert away_b > away_a  # longer Away price should score higher vs consensus
