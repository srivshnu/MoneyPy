from loan_calc import generate_loan_schedule, compute_tenure_from_payment

def print_sample(schedule, label):
    print(f"--- {label} ---")
    print(f"Tenure months: {len(schedule.schedule)}")
    print(f"EMI: {schedule.emi}")
    print(f"Total payment: {schedule.total_payment}")
    print(f"Total interest: {schedule.total_interest}")
    print("First 3 rows:")
    for r in schedule.schedule[:3]:
        print(r)
    print("Last 3 rows:")
    for r in schedule.schedule[-3:]:
        print(r)
    print()

# Scenario 1: Variable rates with recurring extra payment
p = 500000.0
base_rate = 8.0
tenure = 240
rate_schedule = [(1, 8.0), (25, 9.0), (61, 7.5)]
summary1 = generate_loan_schedule(p, base_rate, tenure, rate_schedule=rate_schedule, extra_payment_amount=2000.0, extra_payment_type='recurring', extra_payment_start_month=13)
print_sample(summary1, 'Variable rate + recurring extra')

# Compute tenure if user pays a specific monthly payment under variable rates
monthly_payment = 25000.0
months_needed = compute_tenure_from_payment(p, base_rate, monthly_payment, rate_schedule=rate_schedule)
print(f"Months to repay with monthly payment {monthly_payment}: {months_needed}")

# (Tax-related sample removed)

# Scenario 2: No extra payments, fixed rate
summary2 = generate_loan_schedule(100000.0, 7.5, 24)
print_sample(summary2, 'Fixed rate, no extra')
