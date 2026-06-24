from decimal import Decimal, getcontext, ROUND_HALF_UP
from dataclasses import dataclass
from typing import List

# Set Decimal precision high enough for intermediate calculations
getcontext().prec = 28

TWO_PLACES = Decimal('0.01')


@dataclass
class LoanScheduleRow:
    period: int
    opening_balance: float
    emi: float
    principal: float
    interest: float
    closing_balance: float


@dataclass
class LoanSummary:
    principal: float
    annual_rate: float
    tenure_months: int
    emi: float
    total_payment: float
    total_interest: float
    schedule: List[LoanScheduleRow]


def calculate_emi(principal: float, annual_rate: float, tenure_months: int) -> float:
    """Calculate EMI using reducing balance formula with Decimal for accuracy.

    Returns rounded EMI as float (two decimal places).
    """
    p = Decimal(str(principal))
    r = Decimal(str(annual_rate))
    n = int(tenure_months)

    if r == 0:
        emi = (p / Decimal(n)).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)
        return float(emi)

    monthly_rate = (r / Decimal('12')) / Decimal('100')
    factor = (Decimal('1') + monthly_rate) ** n
    emi = (p * monthly_rate * factor / (factor - Decimal('1'))).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)
    return float(emi)


def generate_loan_schedule(principal: float, annual_rate: float, tenure_months: int) -> LoanSummary:
    """Generate full amortization schedule for a reducing balance loan using Decimal.

    All monetary values are rounded to two decimals using ROUND_HALF_UP to match
    typical banking conventions.
    """
    p = Decimal(str(principal))
    r = Decimal(str(annual_rate))
    n = int(tenure_months)

    emi = Decimal(str(calculate_emi(principal, annual_rate, tenure_months)))
    monthly_rate = (r / Decimal('12')) / Decimal('100')
    schedule: List[LoanScheduleRow] = []
    balance = p

    for period in range(1, n + 1):
        opening = balance
        interest = (opening * monthly_rate).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)
        principal_part = (emi - interest).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)

        # Last period adjustment to avoid small residuals due to rounding
        if period == n:
            principal_part = opening.quantize(TWO_PLACES, rounding=ROUND_HALF_UP)
            emi_actual = (principal_part + interest).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)
        else:
            emi_actual = emi

        closing = (opening - principal_part).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)
        if closing < Decimal('0'):
            closing = Decimal('0.00')

        schedule.append(LoanScheduleRow(
            period=period,
            opening_balance=float(opening),
            emi=float(emi_actual),
            principal=float(principal_part),
            interest=float(interest),
            closing_balance=float(closing),
        ))
        balance = closing

    total_payment = sum(Decimal(str(r.emi)) for r in schedule)
    total_interest = sum(Decimal(str(r.interest)) for r in schedule)

    return LoanSummary(
        principal=float(p),
        annual_rate=float(r),
        tenure_months=n,
        emi=float(Decimal(str(emi)).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)),
        total_payment=float(total_payment.quantize(TWO_PLACES, rounding=ROUND_HALF_UP)),
        total_interest=float(total_interest.quantize(TWO_PLACES, rounding=ROUND_HALF_UP)),
        schedule=schedule,
    )