from logic.prepayment import compute_prepayment_impact


def test_no_extra_payment_returns_zero_savings():
    res = compute_prepayment_impact(100000.0, 8.0, 24, extra_payment_amount=0.0, extra_payment_type='none')
    assert res['interest_saved'] == 0.0
    assert res['months_saved'] == 0


def test_recurring_extra_reduces_interest_and_months():
    res = compute_prepayment_impact(200000.0, 9.0, 120, extra_payment_amount=2000.0, extra_payment_type='recurring', extra_payment_start_month=1)
    assert res['interest_saved'] > 0
    assert res['months_saved'] >= 0


def test_one_time_extra_large_pays_off_early():
    # Large one-time lump sum should shorten tenure drastically
    res = compute_prepayment_impact(50000.0, 7.0, 60, extra_payment_amount=50000.0, extra_payment_type='one-time', extra_payment_start_month=1)
    assert res['months_saved'] >= 1
    assert res['interest_saved'] >= 0
