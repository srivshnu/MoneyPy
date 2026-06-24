import pytest
from loan_calc import generate_loan_schedule, calculate_emi
from loan_calc import compute_tenure_from_payment


@pytest.mark.parametrize("principal,rate,tenure", [
    (120000.0, 0.0, 12),        # zero interest
    (500000.0, 8.5, 60),        # typical home loan
    (1000000.0, 10.0, 120),     # large loan long tenure
])
def test_schedule_consistency(principal, rate, tenure):
    summary = generate_loan_schedule(principal, rate, tenure)

    # EMI should be non-negative
    assert summary.emi >= 0

    # Schedule length matches tenure
    assert len(summary.schedule) == tenure

    # Closing balance of last period should be zero (or very close)
    assert round(summary.schedule[-1].closing_balance, 2) == 0.00

    # Total payment equals sum of EMIs in the schedule
    assert round(sum(r.emi for r in summary.schedule), 2) == round(summary.total_payment, 2)

    # Total interest equals sum of interest column
    assert round(sum(r.interest for r in summary.schedule), 2) == round(summary.total_interest, 2)

    # Principal recovered equals original principal
    recovered = round(sum(r.principal for r in summary.schedule), 2)
    assert round(recovered, 2) == round(summary.principal, 2)


def test_zero_rate_emi_matches_division():
    p = 120000.0
    t = 12
    emi = calculate_emi(p, 0.0, t)
    assert emi == pytest.approx(10000.0)


def test_monthly_decreasing_balance_and_interest():
    p = 500000.0
    rate = 8.5
    t = 12
    s = generate_loan_schedule(p, rate, t)

    balances = [r.opening_balance for r in s.schedule]
    interests = [r.interest for r in s.schedule]

    # Opening balances should strictly decrease (except possible rounding equalities)
    assert all(balances[i] >= balances[i+1] for i in range(len(balances)-1))

    # Interest portion should generally decrease over time
    assert interests[0] >= interests[-1]


def test_compute_tenure_from_payment_zero_rate():
    p = 120000.0
    m = 10000.0
    months = compute_tenure_from_payment(p, 0.0, m)
    assert months == 12


def test_compute_tenure_from_payment_positive_rate():
    p = 500000.0
    r = 8.5
    # use a payment slightly higher than standard EMI for 60 months
    s = generate_loan_schedule(p, r, 60)
    emi = s.emi
    months = compute_tenure_from_payment(p, r, emi * 1.1)
    assert months < 60


def test_compute_tenure_payment_too_small():
    p = 500000.0
    r = 8.5
    # interest-only amount
    monthly_rate = r / 12.0 / 100.0
    tiny_payment = p * monthly_rate * 0.9
    with pytest.raises(ValueError):
        compute_tenure_from_payment(p, r, tiny_payment)


if __name__ == "__main__":
    # Simple runner to exercise a few scenarios and display results
    scenarios = [
        (500000.0, 8.5, 60),
        (250000.0, 7.0, 36),
        (100000.0, 6.5, 24),
    ]
    for p, r, t in scenarios:
        s = generate_loan_schedule(p, r, t)
        print(f"P={p}, R={r}%, Tenure={t} months -> EMI={s.emi}, TotalInterest={s.total_interest}, TotalPaid={s.total_payment}")
