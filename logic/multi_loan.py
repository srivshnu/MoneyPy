from typing import Dict
from loan_calc import generate_loan_schedule


def compare_two_loans(a: Dict, b: Dict) -> Dict:
    """Compare two loan scenarios.

    Each argument is a dict with keys: principal, annual_rate, tenure_months,
    (optional) extra_payment_amount, extra_payment_type, extra_payment_start_month
    Returns both summaries and delta metrics.
    """
    def build_summary(params):
        return generate_loan_schedule(
            params.get('principal'),
            params.get('annual_rate'),
            params.get('tenure_months'),
            extra_payment_amount=params.get('extra_payment_amount', 0.0),
            extra_payment_type=params.get('extra_payment_type', 'none'),
            extra_payment_start_month=params.get('extra_payment_start_month', 1),
        )

    s1 = build_summary(a)
    s2 = build_summary(b)

    return {
        'a': s1,
        'b': s2,
        'delta_total_payment': float(round(s2.total_payment - s1.total_payment, 2)),
        'delta_total_interest': float(round(s2.total_interest - s1.total_interest, 2)),
        'delta_emi': float(round(s2.emi - s1.emi, 2)),
        'delta_tenure_months': int(s2.tenure_months - s1.tenure_months),
    }
