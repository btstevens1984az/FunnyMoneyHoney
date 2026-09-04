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
