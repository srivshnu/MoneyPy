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
	recurring_amount: float
	total_contributions: float
	maturity_amount: float
	total_interest: float
	schedule: List[CIScheduleRow]


COMPOUNDING_FREQ = {
	"Monthly": 12,
	"Quarterly": 4,
	"Half-Yearly": 2,
	"Yearly": 1,
}


def calculate_runway(total_liquid: float, monthly_liabilities: float) -> float:
	if monthly_liabilities <= 0:
		return 0.0
	return round(float(total_liquid) / float(monthly_liabilities), 2)


def calculate_sinking_fund_monthly(target_amount: float, months: int, annual_rate: float = 0.0) -> float:
	if months <= 0:
		return 0.0
	monthly_rate = annual_rate / 12 / 100
	if monthly_rate == 0:
		return round(float(target_amount) / months, 2)
	factor = (1 + monthly_rate) ** months - 1
	return round(float(target_amount) * monthly_rate / factor, 2)


def _sort_debts(debts, method: str):
	if method == 'snowball':
		return sorted(debts, key=lambda d: (d['balance'], d['annual_rate']))
	return sorted(debts, key=lambda d: (-d['annual_rate'], d['balance']))


def simulate_debt_repayment(debts: list, monthly_budget: float, method: str = 'snowball') -> dict:
	if monthly_budget <= 0:
		raise ValueError('Monthly budget must be greater than zero.')
	if method not in ('snowball', 'avalanche'):
		raise ValueError('Method must be snowball or avalanche.')

	active_debts = [
		{
			'name': d['name'],
			'balance': float(d['balance']),
			'annual_rate': float(d['annual_rate']),
			'min_payment': float(d.get('min_payment', 0.0)),
		}
		for d in debts if float(d.get('balance', 0.0)) > 0.0
	]

	if not active_debts:
		return {'months': 0, 'total_interest': 0.0, 'total_paid': 0.0, 'monthly_balances': []}

	monthly_balances = []
	total_interest = 0.0
	total_paid = 0.0
	month = 0
	max_months = 600

	while any(d['balance'] > 0.01 for d in active_debts) and month < max_months:
		month += 1
		# Accrue interest on each debt before payment
		for d in active_debts:
			if d['balance'] <= 0.0:
				continue
			interest = round(d['balance'] * d['annual_rate'] / 12 / 100, 2)
			d['balance'] = round(d['balance'] + interest, 2)
			total_interest += interest

		budget_remaining = float(monthly_budget)
		# Cover minimum payments first
		for d in active_debts:
			if d['balance'] <= 0.0:
				continue
			payment = min(d['min_payment'], d['balance'])
			if budget_remaining >= payment:
				d['balance'] = round(d['balance'] - payment, 2)
				budget_remaining = round(budget_remaining - payment, 2)
				total_paid += payment
			else:
				payment = round(budget_remaining, 2)
				d['balance'] = round(d['balance'] - payment, 2)
				total_paid += payment
				budget_remaining = 0.0
				break

		# Apply extra funds to prioritized debt
		if budget_remaining > 0.0:
			target_debts = [d for d in active_debts if d['balance'] > 0.01]
			if target_debts:
				target_debts = _sort_debts(target_debts, method)
				while budget_remaining > 0.0 and target_debts:
					target = target_debts[0]
					payment = min(budget_remaining, target['balance'])
					target['balance'] = round(target['balance'] - payment, 2)
					budget_remaining = round(budget_remaining - payment, 2)
					total_paid += payment
					if target['balance'] <= 0.01:
						target_debts.pop(0)

		monthly_balances.append(
			{'Month': month, **{f"{d['name']} Balance": max(round(d['balance'], 2), 0.0) for d in active_debts}}
		)

	return {
		'months': month,
		'total_interest': round(total_interest, 2),
		'total_paid': round(total_paid, 2),
		'monthly_balances': monthly_balances,
	}


def project_net_worth(current_assets: float, current_liabilities: float, asset_growth: float, liability_reduction: float, months: int) -> list:
	assets = float(current_assets)
	liabilities = float(current_liabilities)
	monthly_asset_rate = (1 + asset_growth / 100) ** (1 / 12) - 1 if asset_growth != 0 else 0.0
	monthly_liability_rate = 1 - (1 - liability_reduction / 100) ** (1 / 12) if liability_reduction != 0 else 0.0
	projection = []
	previous_net_worth = assets - liabilities

	for month in range(1, months + 1):
		assets = round(assets * (1 + monthly_asset_rate), 2)
		liabilities = round(liabilities * (1 - monthly_liability_rate), 2)
		net_worth = round(assets - liabilities, 2)
		velocity = round(net_worth - previous_net_worth, 2)
		projection.append({
			'Month': month,
			'Assets': assets,
			'Liabilities': liabilities,
			'Net Worth': net_worth,
			'velocity': velocity,
		})
		previous_net_worth = net_worth

	return projection


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


def generate_ci_schedule(principal: float, annual_rate: float, tenure_years: int, compounding: str = "Monthly", recurring_amount: float = 0.0) -> CISummary:
    total_months = tenure_years * 12
    monthly_rate = annual_rate / 12 / 100
    schedule = []
    opening = float(principal)
    cumulative = 0.0
    total_contributions = 0.0
    year_opening = opening
    year_interest = 0.0

    for month in range(1, total_months + 1):
        interest = round(opening * monthly_rate, 2)
        closing = round(opening + interest + recurring_amount, 2)
        cumulative += interest
        year_interest += interest
        total_contributions += recurring_amount
        opening = closing

        if month % 12 == 0:
            year = month // 12
            schedule.append(CIScheduleRow(
                year=year,
                opening_balance=year_opening,
                interest_earned=round(year_interest, 2),
                closing_balance=opening,
                cumulative_interest=round(cumulative, 2),
            ))
            year_opening = opening
            year_interest = 0.0

    maturity = schedule[-1].closing_balance if schedule else principal
    total_interest = round(sum(r.interest_earned for r in schedule), 2)

    return CISummary(
        principal=principal,
        annual_rate=annual_rate,
        tenure_years=tenure_years,
        compounding=compounding,
        recurring_amount=recurring_amount,
        total_contributions=round(total_contributions, 2),
		maturity_amount=maturity,
		total_interest=total_interest,
		schedule=schedule,
	)
