from planning_page import normalize_debt_count, format_net_worth_velocity


def test_normalize_debt_count_clamps_to_valid_range():
    assert normalize_debt_count(0) == 1
    assert normalize_debt_count(3) == 3
    assert normalize_debt_count(12) == 10


def test_format_net_worth_velocity_uses_valid_currency_format():
    assert format_net_worth_velocity(1250.5) == "₹1,250.50 / month"
