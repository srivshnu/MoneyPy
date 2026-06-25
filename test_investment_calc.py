from investment_calc import generate_ci_schedule


def test_ci_schedule_with_recurring_amount():
    summary = generate_ci_schedule(100000.0, 8.0, 2, "Monthly", recurring_amount=1000.0)

    assert summary.recurring_amount == 1000.0
    assert summary.total_contributions == 24000.0
    assert summary.maturity_amount > summary.principal
    assert len(summary.schedule) == 2
    assert summary.schedule[0].opening_balance == 100000.0
    assert summary.schedule[1].opening_balance == summary.schedule[0].closing_balance
