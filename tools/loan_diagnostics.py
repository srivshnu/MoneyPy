import os, sys

# Ensure the local `logic` package directory is importable even if there's a top-level
# module named `logic.py` in the workspace. Insert the `logic` folder into sys.path
# and import the modules by name from there.
logic_dir = os.path.join(os.getcwd(), "logic")
if logic_dir not in sys.path:
    sys.path.insert(0, logic_dir)

from loan_calc import generate_loan_schedule, calculate_emi


def check_scenario(principal, rate, tenure):
    s = generate_loan_schedule(principal, rate, tenure)
    anomalies = []

    if s.emi < 0:
        anomalies.append("Negative EMI")

    if len(s.schedule) != tenure:
        anomalies.append("Schedule length mismatch")

    last_closing = round(s.schedule[-1].closing_balance, 2)
    if abs(last_closing) > 0.01:
        anomalies.append(f"Residual closing balance {last_closing}")

    if any(r.closing_balance < 0 for r in s.schedule):
        anomalies.append("Negative balance in schedule")

    recovered = round(sum(r.principal for r in s.schedule), 2)
    if round(recovered - s.principal, 2) != 0.0:
        anomalies.append(f"Principal mismatch recovered={recovered} vs principal={s.principal}")

    total_interest = round(sum(r.interest for r in s.schedule), 2)
    if round(total_interest - s.total_interest, 2) != 0.0:
        anomalies.append(f"Interest mismatch {total_interest} vs {s.total_interest}")

    # Verify EMI computation formula
    emi_formula = calculate_emi(principal, rate, tenure)
    if round(emi_formula - s.emi, 2) != 0.0:
        # Allow for last period adjusted EMI difference
        if tenure > 1 and round(emi_formula - s.schedule[-1].emi, 2) != 0.0:
            anomalies.append(f"EMI formula mismatch formula={emi_formula} summary_emi={s.emi}")

    return anomalies


def run_diagnostics():
    anomalies_found = []
    scenarios = []

    # generate varied scenarios
    principals = [1000.0, 10000.0, 500000.0, 1_000_000.0]
    rates = [0.0, 0.5, 4.5, 8.5, 15.0]
    tenures = [1, 6, 12, 60, 120, 240, 360]

    for p in principals:
        for r in rates:
            for t in tenures:
                scenarios.append((p, r, t))

    for p, r, t in scenarios:
        anomalies = check_scenario(p, r, t)
        if anomalies:
            anomalies_found.append(((p, r, t), anomalies))

    if not anomalies_found:
        print("Diagnostics: no anomalies found across all scenarios.")
    else:
        print(f"Diagnostics: {len(anomalies_found)} anomalies found:")
        for (p, r, t), anoms in anomalies_found:
            print(f" - P={p}, R={r}%, Tenure={t}: {anoms}")


if __name__ == '__main__':
    run_diagnostics()
