from typing import Dict
from loan_calc import generate_loan_schedule


def compute_prepayment_impact(principal: float, annual_rate: float, tenure_months: int,
                              extra_payment_amount: float = 0.0,
                              extra_payment_type: str = 'none',
                              extra_payment_start_month: int = 1) -> Dict:
    """Compute impact of a one-time or recurring prepayment by comparing
    the base schedule with a schedule that includes extra payments.

    Returns a dict with keys: original_summary, new_summary, interest_saved,
    months_saved.
    """
    base = generate_loan_schedule(principal, annual_rate, tenure_months)

    if extra_payment_amount == 0.0 or extra_payment_type == 'none':
        return {
            'original': base,
            'updated': base,
            'interest_saved': 0.0,
            'months_saved': 0,
        }

    updated = generate_loan_schedule(
        principal, annual_rate, tenure_months,
        extra_payment_amount=extra_payment_amount,
        extra_payment_type=extra_payment_type,
        extra_payment_start_month=extra_payment_start_month,
    )

    interest_saved = float(round(base.total_interest - updated.total_interest, 2))
    months_saved = int(base.tenure_months - updated.tenure_months)

    return {
        'original': base,
        'updated': updated,
        'interest_saved': interest_saved,
        'months_saved': months_saved,
    }
