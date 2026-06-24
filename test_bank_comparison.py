from decimal import Decimal, getcontext, ROUND_HALF_UP
from loan_calc import generate_loan_schedule

getcontext().prec = 40


def reference_schedule(principal: float, annual_rate: float, tenure_months: int):
    """Independent reference amortization schedule using high-precision Decimal.

    This function computes EMI and per-period breakdown and returns a list
    of dict rows comparable to `generate_loan_schedule` output.
    """
    P = Decimal(str(principal))
    r = Decimal(str(annual_rate))
    n = int(tenure_months)
    TWO = Decimal('0.01')

    if r == 0:
        emi = (P / Decimal(n)).quantize(TWO, rounding=ROUND_HALF_UP)
    else:
        i = (r / Decimal('12')) / Decimal('100')
        factor = (Decimal(1) + i) ** n
        emi = (P * i * factor / (factor - Decimal(1))).quantize(TWO, rounding=ROUND_HALF_UP)

    balance = P
    rows = []
    for period in range(1, n + 1):
        opening = balance
        interest = (opening * ((r / Decimal('12')) / Decimal('100'))).quantize(TWO, rounding=ROUND_HALF_UP)
        principal_part = (Decimal(str(emi)) - interest).quantize(TWO, rounding=ROUND_HALF_UP)
        if period == n:
            principal_part = opening.quantize(TWO, rounding=ROUND_HALF_UP)
            emi_actual = (principal_part + interest).quantize(TWO, rounding=ROUND_HALF_UP)
        else:
            emi_actual = emi
        closing = (opening - principal_part).quantize(TWO, rounding=ROUND_HALF_UP)
        if closing < Decimal('0'):
            closing = Decimal('0.00')
        rows.append({
            'period': period,
            'opening': float(opening),
            'emi': float(emi_actual),
            'principal': float(principal_part),
            'interest': float(interest),
            'closing': float(closing),
        })
        balance = closing

    total_payment = sum(Decimal(str(r['emi'])) for r in rows)
    total_interest = sum(Decimal(str(r['interest'])) for r in rows)

    return rows, float(total_payment.quantize(TWO, rounding=ROUND_HALF_UP)), float(total_interest.quantize(TWO, rounding=ROUND_HALF_UP))


def test_compare_with_reference():
    scenarios = [
        (100000.0, 7.5, 24),
        (250000.0, 9.25, 60),
        (500000.0, 8.0, 120),
    ]

    for p, r, t in scenarios:
        summary = generate_loan_schedule(p, r, t)
        ref_rows, ref_total_payment, ref_total_interest = reference_schedule(p, r, t)

        # Compare totals
        assert round(summary.total_payment, 2) == round(ref_total_payment, 2)
        assert round(summary.total_interest, 2) == round(ref_total_interest, 2)

        # Compare first few and last row entries to ensure matching rounding convention
        for idx in [0, 1, -1]:
            srow = summary.schedule[idx]
            rrow = ref_rows[idx]
            assert round(srow.opening_balance, 2) == round(rrow['opening'], 2)
            assert round(srow.emi, 2) == round(rrow['emi'], 2)
            assert round(srow.principal, 2) == round(rrow['principal'], 2)
            assert round(srow.interest, 2) == round(rrow['interest'], 2)
            assert round(srow.closing_balance, 2) == round(rrow['closing'], 2)
