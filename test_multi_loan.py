from logic.multi_loan import compare_two_loans


def test_compare_tenure_variation():
    a = {'principal': 300000.0, 'annual_rate': 8.0, 'tenure_months': 180}
    b = {'principal': 300000.0, 'annual_rate': 8.0, 'tenure_months': 240}
    res = compare_two_loans(a, b)
    # longer tenure B should have higher total interest and higher total payment
    assert res['delta_total_interest'] > 0
    assert res['delta_total_payment'] > 0


def test_compare_rate_difference():
    a = {'principal': 200000.0, 'annual_rate': 7.5, 'tenure_months': 120}
    b = {'principal': 200000.0, 'annual_rate': 9.0, 'tenure_months': 120}
    res = compare_two_loans(a, b)
    assert res['delta_total_interest'] > 0
    assert res['delta_total_payment'] > 0
