from dataclasses import dataclass
from typing import List


@dataclass
class FDScheduleRow:
	period: int
	opening_balance: float
	interest_earned: float
	closing_balance: float
	cumulative_interest: float


@dataclass
class FDSummary:
	principal: float
	annual_rate: float
	tenure_months: int
	compounding: str
	maturity_amount: float
	total_interest: float
	schedule: List[FDScheduleRow]


@dataclass
class RDScheduleRow:
	period: int
	installment: float
	opening_balance: float
	interest_earned: float
	closing_balance: float
	total_deposited: float
	cumulative_interest: float


@dataclass
class RDSummary:
	monthly_installment: float
	annual_rate: float
	tenure_months: int
	total_deposited: float
	maturity_amount: float
	total_interest: float
	schedule: List[RDScheduleRow]


@dataclass
class CIScheduleRow:
	year: int
	opening_balance: float
	interest_earned: float
	closing_balance: float
	cumulative_interest: float


@dataclass
class CISummary:
	principal: float
	annual_rate: float
	tenure_years: int
	compounding: str
	maturity_amount: float
	total_interest: float
	schedule: List[CIScheduleRow]


COMPOUNDING_FREQ = {
	"Monthly": 12,
	"Quarterly": 4,
	"Half-Yearly": 2,
	"Yearly": 1,
}


def generate_fd_schedule(principal: float, annual_rate: float, tenure_months: int, compounding: str = "Monthly") -> FDSummary:
	monthly_rate = annual_rate / 12 / 100
	schedule = []
	opening = principal
	cumulative = 0.0

	for m in range(1, tenure_months + 1):
		interest = round(opening * monthly_rate, 2)
		closing = round(opening + interest, 2)
		cumulative += interest
		schedule.append(FDScheduleRow(
			period=m,
			opening_balance=opening,
			interest_earned=interest,
			closing_balance=closing,
			cumulative_interest=round(cumulative, 2),
		))
		opening = closing

	maturity = schedule[-1].closing_balance if schedule else principal
	total_interest = round(sum(r.interest_earned for r in schedule), 2)

	return FDSummary(
		principal=principal,
		annual_rate=annual_rate,
		tenure_months=tenure_months,
		compounding=compounding,
		maturity_amount=maturity,
		total_interest=total_interest,
		schedule=schedule,
	)


def generate_rd_schedule(monthly_installment: float, annual_rate: float, tenure_months: int) -> RDSummary:
	monthly_rate = annual_rate / 12 / 100
	schedule = []
	opening = 0.0
	cumulative_interest = 0.0
	total_deposited = 0.0

	for m in range(1, tenure_months + 1):
		interest = round(opening * monthly_rate, 2)
		closing = round(opening + interest + monthly_installment, 2)
		total_deposited += monthly_installment
		cumulative_interest += interest
		schedule.append(RDScheduleRow(
			period=m,
			installment=monthly_installment,
			opening_balance=opening,
			interest_earned=interest,
			closing_balance=closing,
			total_deposited=round(total_deposited, 2),
			cumulative_interest=round(cumulative_interest, 2),
		))
		opening = closing

	maturity = schedule[-1].closing_balance if schedule else 0.0
	total_interest = round(sum(r.interest_earned for r in schedule), 2)

	return RDSummary(
		monthly_installment=monthly_installment,
		annual_rate=annual_rate,
		tenure_months=tenure_months,
		total_deposited=round(total_deposited, 2),
		maturity_amount=maturity,
		total_interest=total_interest,
		schedule=schedule,
	)


def generate_ci_schedule(principal: float, annual_rate: float, tenure_years: int, compounding: str = "Monthly") -> CISummary:
	freq = COMPOUNDING_FREQ.get(compounding, 12)
	schedule = []
	opening = float(principal)
	cumulative = 0.0

	for y in range(1, tenure_years + 1):
		factor = (1 + (annual_rate / 100) / freq) ** freq
		closing = round(opening * factor, 2)
		interest = round(closing - opening, 2)
		cumulative += interest
		schedule.append(CIScheduleRow(
			year=y,
			opening_balance=opening,
			interest_earned=interest,
			closing_balance=closing,
			cumulative_interest=round(cumulative, 2),
		))
		opening = closing

	maturity = schedule[-1].closing_balance if schedule else principal
	total_interest = round(sum(r.interest_earned for r in schedule), 2)

	return CISummary(
		principal=principal,
		annual_rate=annual_rate,
		tenure_years=tenure_years,
		compounding=compounding,
		maturity_amount=maturity,
		total_interest=total_interest,
		schedule=schedule,
	)
