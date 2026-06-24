from decimal import Decimal, getcontext, ROUND_HALF_UP, ROUND_HALF_DOWN, ROUND_HALF_EVEN, ROUND_UP, ROUND_DOWN
from dataclasses import dataclass
from typing import List

# Set Decimal precision for intermediate calculations
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
    extra_payment: float = 0.0


@dataclass
class LoanSummary:
    principal: float
    annual_rate: float
    tenure_months: int
    emi: float
    total_payment: float
    total_interest: float
    schedule: List[LoanScheduleRow]


def calculate_emi(principal: float, annual_rate: float, tenure_months: int, rounding=ROUND_HALF_UP) -> float:
    """Calculate EMI using reducing balance formula with Decimal for accuracy.

    Returns rounded EMI as float (two decimal places).
    """
    p = Decimal(str(principal))
    r = Decimal(str(annual_rate))
    n = int(tenure_months)

    if r == 0:
        emi = (p / Decimal(n)).quantize(TWO_PLACES, rounding=rounding)
        return float(emi)

    monthly_rate = (r / Decimal('12')) / Decimal('100')
    factor = (Decimal('1') + monthly_rate) ** n
    emi = (p * monthly_rate * factor / (factor - Decimal('1'))).quantize(TWO_PLACES, rounding=rounding)
    return float(emi)


def compute_tenure_from_payment(principal: float, annual_rate: float, monthly_payment: float, rate_schedule: List[tuple] = None) -> int:
    """Compute number of months required to repay the loan given a fixed monthly payment.

    Returns the number of months (ceiled to next integer) or raises ValueError if
    the payment is too small to ever repay the loan.
    """
    import math

    # If a rate_schedule is provided, do a month-by-month simulation with changing rates.
    if rate_schedule:
        bal = Decimal(str(principal))
        m = Decimal(str(monthly_payment))
        # normalize schedule: list of (start_month:int, rate:Decimal)
        sched = sorted([(int(s), Decimal(str(rt))) for s, rt in rate_schedule], key=lambda x: x[0])
        month = 0
        max_months = 10000
        while bal > Decimal('0') and month < max_months:
            month += 1
            # find applicable rate
            current_rate = Decimal(str(annual_rate))
            for s, rt in sched:
                if month >= s:
                    current_rate = rt
                else:
                    break
            i = (current_rate / Decimal('12')) / Decimal('100')
            interest = (bal * i).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)
            if m <= interest:
                raise ValueError("Monthly payment too small to cover interest; loan will not be repaid")
            principal_reduction = (m - interest).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)
            bal = (bal - principal_reduction).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)
        if bal > Decimal('0'):
            raise ValueError("Payment schedule did not repay loan within reasonable bounds")
        return month

    import math

    p = float(principal)
    r = float(annual_rate)
    m = float(monthly_payment)

    if m <= 0:
        raise ValueError("Monthly payment must be greater than zero")

    if r == 0:
        # Simple division, ceil to months
        return int(math.ceil(p / m))

    i = r / 12.0 / 100.0

    # If payment is less than or equal to interest-only amount, loan never repaid
    if m <= p * i:
        raise ValueError("Monthly payment too small to cover interest; loan will not be repaid")

    # n = log(M / (M - P*i)) / log(1 + i)
    numerator = math.log(m / (m - p * i))
    denominator = math.log(1 + i)
    n = numerator / denominator
    return int(math.ceil(n))


# Tax-related helper `compute_tax_benefits` removed per project request.


def generate_loan_schedule(
    principal: float,
    annual_rate: float,
    tenure_months: int,
    *,
    rate_schedule: List[tuple] = None,
    extra_payment_amount: float = 0.0,
    extra_payment_type: str = 'none',  # 'none' | 'one-time' | 'recurring'
    extra_payment_start_month: int = 1,
    extra_payments_by_period: dict = None,
    rounding=ROUND_HALF_UP,
) -> LoanSummary:
    """Generate full amortization schedule for a reducing balance loan using Decimal.

    Supports optional extra payments (one-time or recurring). All monetary values
    are rounded to two decimals using the supplied rounding mode.
    """
    p = Decimal(str(principal))
    r = Decimal(str(annual_rate))
    n = int(tenure_months)

    emi = Decimal(str(calculate_emi(principal, annual_rate, tenure_months, rounding=rounding)))
    # normalize rate schedule if provided: list of (start_month:int, rate:Decimal)
    rate_sched = None
    if rate_schedule:
        rate_sched = sorted([(int(s), Decimal(str(rt))) for s, rt in rate_schedule], key=lambda x: x[0])
    schedule: List[LoanScheduleRow] = []
    balance = p

    # Normalize extra payment amount or use explicit per-period extra payments if provided
    extra_amt = Decimal(str(extra_payment_amount)) if extra_payment_amount else Decimal('0')
    use_period_extras = extra_payments_by_period is not None
    if use_period_extras:
        # convert keys to int and values to Decimal
        period_extras = {int(k): Decimal(str(v)) for k, v in extra_payments_by_period.items()}

    if (not use_period_extras) and extra_amt == Decimal('0'):
        # No extra payments: keep original, stable behavior (identical rounding behavior)
        for period in range(1, n + 1):
            opening = balance
            # determine monthly_rate for this period
            current_rate = r
            if rate_sched:
                for s, rt in rate_sched:
                    if period >= s:
                        current_rate = rt
                    else:
                        break
            monthly_rate = (current_rate / Decimal('12')) / Decimal('100')
            interest = (opening * monthly_rate).quantize(TWO_PLACES, rounding=rounding)
            principal_part = (emi - interest).quantize(TWO_PLACES, rounding=rounding)

            # Last period adjustment to avoid small residuals due to rounding
            if period == n:
                principal_part = opening.quantize(TWO_PLACES, rounding=rounding)
                emi_actual = (principal_part + interest).quantize(TWO_PLACES, rounding=rounding)
            else:
                emi_actual = emi

            closing = (opening - principal_part).quantize(TWO_PLACES, rounding=rounding)
            if closing < Decimal('0'):
                closing = Decimal('0.00')

            schedule.append(LoanScheduleRow(
                period=period,
                opening_balance=float(opening),
                emi=float(emi_actual),
                principal=float(principal_part),
                interest=float(interest),
                closing_balance=float(closing),
                extra_payment=0.0,
            ))
            balance = closing

        total_payment = sum(Decimal(str(r.emi)) for r in schedule)
        total_interest = sum(Decimal(str(r.interest)) for r in schedule)
    else:
        for period in range(1, n + 1):
            opening = balance
            # determine monthly_rate for this period
            current_rate = r
            if rate_sched:
                for s, rt in rate_sched:
                    if period >= s:
                        current_rate = rt
                    else:
                        break
            monthly_rate = (current_rate / Decimal('12')) / Decimal('100')
            # interest rounded per chosen rounding
            interest = (opening * monthly_rate).quantize(TWO_PLACES, rounding=rounding)
            principal_part = (emi - interest).quantize(TWO_PLACES, rounding=rounding)

            # Determine extra payment for this period
            extra_this = Decimal('0')
            if use_period_extras:
                extra_this = period_extras.get(period, Decimal('0'))
            else:
                if extra_payment_type == 'recurring' and period >= int(extra_payment_start_month):
                    extra_this = extra_amt
                elif extra_payment_type == 'one-time' and period == int(extra_payment_start_month):
                    extra_this = extra_amt

            # Apply extra payment into principal
            principal_part_total = (principal_part + extra_this).quantize(TWO_PLACES, rounding=rounding)

            # Final-period adjustment: ensure loan is paid off on the last scheduled month
            if period == n:
                principal_part_total = opening.quantize(TWO_PLACES, rounding=rounding)
                emi_actual = (principal_part_total + interest).quantize(TWO_PLACES, rounding=rounding)
                # extra_this is considered extra only if emi_actual equals base emi
                extra_paid = Decimal('0')
            else:
                # Regular handling: if extra + principal would exceed opening, cap it
                if principal_part_total >= opening:
                    principal_part_total = opening.quantize(TWO_PLACES, rounding=rounding)
                    emi_actual = (principal_part_total + interest).quantize(TWO_PLACES, rounding=rounding)
                    # when emi_actual != base emi, we do not count extra as separate beyond the emi
                    extra_paid = Decimal('0')
                else:
                    emi_actual = emi
                    extra_paid = extra_this

            closing = (opening - principal_part_total).quantize(TWO_PLACES, rounding=rounding)
            if closing < Decimal('0'):
                closing = Decimal('0.00')

            schedule.append(LoanScheduleRow(
                period=period,
                opening_balance=float(opening),
                emi=float(emi_actual),
                principal=float(principal_part_total),
                interest=float(interest),
                closing_balance=float(closing),
                extra_payment=float(extra_paid),
            ))
            balance = closing

            # If loan paid off early, stop adding further rows
            if balance == Decimal('0.00'):
                break

        total_payment = sum(Decimal(str(r.emi)) + Decimal(str(getattr(r, 'extra_payment', 0.0))) for r in schedule)
        total_interest = sum(Decimal(str(r.interest)) for r in schedule)

    return LoanSummary(
        principal=float(p),
        annual_rate=float(r),
        tenure_months=len(schedule),
        emi=float(Decimal(str(emi)).quantize(TWO_PLACES, rounding=rounding)),
        total_payment=float(total_payment.quantize(TWO_PLACES, rounding=rounding)),
        total_interest=float(total_interest.quantize(TWO_PLACES, rounding=rounding)),
        schedule=schedule,
    )