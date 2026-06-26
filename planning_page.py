import streamlit as st
import pandas as pd
import os
import sys

# Ensure local modules import reliably
sys.path.insert(0, os.path.dirname(__file__))

from investment_calc import generate_rd_schedule, calculate_runway, simulate_debt_repayment, calculate_sinking_fund_monthly, project_net_worth
from ui_helpers import validate_required


def _format_currency(value: float) -> str:
    return f"₹{value:,.2f}"


def render():
    st.markdown("## 📊 Personal Finance Planning Hub")
    st.markdown("---")

    with st.expander("Emergency Fund Runway Calculator", expanded=True):
        with st.form("runway_form"):
            c1, c2 = st.columns(2)
            with c1:
                savings = st.number_input("Current Liquid Savings (₹)", min_value=0.0, value=200000.0, step=1000.0, format="%.2f", key="runway_savings")
                fixed_deposits = st.number_input("Liquid Fixed Deposits / Cash Equivalents (₹)", min_value=0.0, value=100000.0, step=1000.0, format="%.2f", key="runway_fds")
                other_liquid = st.number_input("Other Liquid Assets (₹)", min_value=0.0, value=25000.0, step=500.0, format="%.2f", key="runway_other")
            with c2:
                monthly_needs = st.number_input("Essential Monthly Liabilities (₹)", min_value=1.0, value=50000.0, step=500.0, format="%.2f", key="runway_needs")
                rent = st.number_input("Monthly Rent / Housing Cost (₹)", min_value=0.0, value=15000.0, step=500.0, format="%.2f", key="runway_rent")
                utilities = st.number_input("Monthly Utilities / Bills (₹)", min_value=0.0, value=5000.0, step=500.0, format="%.2f", key="runway_util")
            runway_submit = st.form_submit_button("Calculate Runway")

        if runway_submit:
            missing = validate_required({
                'Current Liquid Savings': savings,
                'Liquid Fixed Deposits / Cash Equivalents': fixed_deposits,
                'Essential Monthly Liabilities': monthly_needs,
            })
            if missing:
                return
            total_liquid = float(savings + fixed_deposits + other_liquid)
            runway_months = calculate_runway(total_liquid, monthly_needs)
            st.metric("Liquid Reserves", _format_currency(total_liquid))
            st.metric("Runway Multiplier", f"{runway_months:,.2f} months")
            st.info(f"Your liquid reserves provide a {runway_months:,.2f}-month survival runway before you need to liquidate assets.")
            if runway_months < 3:
                st.warning("Runway is short; consider increasing liquid savings or cutting essential expenses.")
            elif runway_months < 6:
                st.info("Moderate runway. Keep an eye on cash flow and savings pace.")
            else:
                st.success("Healthy runway. You have a strong emergency cushion.")

    with st.expander("Debt Snowball vs Debt Avalanche Simulator", expanded=False):
        with st.form("debt_form"):
            st.markdown("Enter up to 4 outstanding debts or credit lines.")
            debts = []
            for i in range(1, 5):
                cols = st.columns(4)
                with cols[0]:
                    name = st.text_input(f"Debt {i} Name", value=f"Debt {i}", key=f"debt_name_{i}")
                with cols[1]:
                    balance = st.number_input(f"Balance (₹)", min_value=0.0, value=0.0, step=100.0, format="%.2f", key=f"debt_balance_{i}")
                with cols[2]:
                    rate = st.number_input(f"Annual Rate (%)", min_value=0.0, value=8.0, step=0.1, format="%.2f", key=f"debt_rate_{i}")
                with cols[3]:
                    min_pay = st.number_input(f"Min Monthly Payment (₹)", min_value=0.0, value=0.0, step=100.0, format="%.2f", key=f"debt_min_{i}")
                debts.append({
                    'name': name.strip() or f"Debt {i}",
                    'balance': balance,
                    'annual_rate': rate,
                    'min_payment': min_pay,
                })
            monthly_budget = st.number_input("Total Monthly Repayment Budget (₹)", min_value=0.0, value=15000.0, step=500.0, format="%.2f", key="debt_budget")
            debt_submit = st.form_submit_button("Compare Strategies")

        if debt_submit:
            eligible_debts = [d for d in debts if d['balance'] > 0.0]
            if not eligible_debts:
                st.error("Please add at least one debt balance greater than zero.")
            else:
                for method in ["snowball", "avalanche"]:
                    result = simulate_debt_repayment(eligible_debts, monthly_budget, method=method)
                    with st.container():
                        title = "Debt Snowball" if method == "snowball" else "Debt Avalanche"
                        st.markdown(f"### {title}")
                        st.markdown(f"- Months to repay: **{result['months']}" + "**")
                        st.markdown(f"- Total interest paid: **{_format_currency(result['total_interest'])}**")
                        st.markdown(f"- Total amount paid: **{_format_currency(result['total_paid'])}**")
                        df = pd.DataFrame(result['monthly_balances'])
                        df = df.set_index('Month')
                        st.line_chart(df)
                        st.markdown("---")
                faster = "Debt Avalanche" if result['months'] else "Debt Snowball"
                st.info("Deposit the extra payment amount toward the best strategy after reviewing both payoff horizons and total interest.")

    with st.expander("Sinking Fund Allocation Planner", expanded=False):
        with st.form("sinking_form"):
            c1, c2 = st.columns(2)
            with c1:
                target_amount = st.number_input("Target Expense Amount (₹)", min_value=0.0, value=120000.0, step=1000.0, format="%.2f", key="sink_amount")
                target_months = st.number_input("Time Horizon (Months)", min_value=1, value=12, step=1, key="sink_months")
            with c2:
                assumed_rate = st.number_input("Expected Annual Yield (%)", min_value=0.0, value=6.0, step=0.1, format="%.2f", key="sink_rate")
                rd_rate = st.number_input("Recurring Deposit Rate (%)", min_value=0.0, value=6.0, step=0.1, format="%.2f", key="sink_rd_rate")
            sink_submit = st.form_submit_button("Calculate Contribution")

        if sink_submit:
            missing = validate_required({
                'Target Expense Amount': target_amount,
                'Time Horizon (Months)': target_months,
            })
            if missing:
                return
            monthly_contribution = calculate_sinking_fund_monthly(target_amount, int(target_months), assumed_rate)
            rd_summary = generate_rd_schedule(monthly_contribution, rd_rate, int(target_months))
            st.metric("Monthly Contribution Needed", _format_currency(monthly_contribution))
            st.markdown(f"A recurring deposit of ₹{monthly_contribution:,.2f} at {rd_rate:.2f}% p.a. for {int(target_months)} months will mature to approximately ₹{rd_summary.maturity_amount:,.2f}.")
            if rd_summary.maturity_amount >= target_amount:
                st.success("This RD plan meets your sinking fund target.")
            else:
                st.warning("This RD plan falls short of the target; increase the monthly contribution or choose a higher yield.")

    with st.expander("Rule-Based Budget Optimizer", expanded=False):
        with st.form("budget_form"):
            income = st.number_input("Net Monthly Income (₹)", min_value=0.0, value=200000.0, step=1000.0, format="%.2f", key="budget_income")
            needs = st.number_input("Actual Needs Spend (₹)", min_value=0.0, value=90000.0, step=500.0, format="%.2f", key="budget_needs")
            wants = st.number_input("Actual Wants Spend (₹)", min_value=0.0, value=40000.0, step=500.0, format="%.2f", key="budget_wants")
            savings = st.number_input("Actual Savings / Investments (₹)", min_value=0.0, value=70000.0, step=500.0, format="%.2f", key="budget_savings")
            home_emi = st.number_input("Home Loan EMI (₹)", min_value=0.0, value=60000.0, step=500.0, format="%.2f", key="budget_emi")
            budget_submit = st.form_submit_button("Analyze Budget")

        if budget_submit:
            if income <= 0:
                st.error("Net monthly income must be greater than zero.")
            else:
                recommended_needs = income * 0.50
                recommended_wants = income * 0.30
                recommended_savings = income * 0.20
                actual_total = needs + wants + savings
                st.markdown("### Recommended 50/30/20 Buckets")
                st.markdown(f"- Needs: ₹{recommended_needs:,.2f}")
                st.markdown(f"- Wants: ₹{recommended_wants:,.2f}")
                st.markdown(f"- Savings: ₹{recommended_savings:,.2f}")
                st.markdown("### Actual Allocation")
                st.markdown(f"- Needs: ₹{needs:,.2f} ({needs / income * 100:.1f}%)")
                st.markdown(f"- Wants: ₹{wants:,.2f} ({wants / income * 100:.1f}%)")
                st.markdown(f"- Savings: ₹{savings:,.2f} ({savings / income * 100:.1f}%)")
                if actual_total > income:
                    st.error("Your total allocation exceeds your net income. Adjust spending or savings immediately.")
                emi_ratio = home_emi / income
                if emi_ratio >= 0.40:
                    st.error("House-poor alert: Your home loan EMI is 40% or more of your net income.")
                elif emi_ratio >= 0.35:
                    st.warning("Your home loan EMI is above 35% of net income; this is a risk management threshold.")
                else:
                    st.success("Home loan EMI is within a comfortable range.")

    with st.expander("Net Worth Velocity Tracker", expanded=False):
        with st.form("velocity_form"):
            c1, c2 = st.columns(2)
            with c1:
                current_assets = st.number_input("Current Total Assets (₹)", min_value=0.0, value=800000.0, step=1000.0, format="%.2f", key="nw_assets")
                asset_growth = st.number_input("Expected Annual Asset Growth (%)", min_value=-20.0, max_value=50.0, value=10.0, step=0.1, format="%.2f", key="nw_asset_growth")
                months = st.number_input("Projection Horizon (Months)", min_value=1, value=24, step=1, key="nw_months")
            with c2:
                current_liabilities = st.number_input("Current Total Liabilities (₹)", min_value=0.0, value=500000.0, step=1000.0, format="%.2f", key="nw_liabilities")
                liability_reduction = st.number_input("Expected Annual Liability Reduction (%)", min_value=0.0, max_value=50.0, value=8.0, step=0.1, format="%.2f", key="nw_liability_reduction")
            velocity_submit = st.form_submit_button("Project Net Worth")

        if velocity_submit:
            if months <= 0:
                st.error("Projection horizon must be at least one month.")
            else:
                projection = project_net_worth(current_assets, current_liabilities, asset_growth, liability_reduction, int(months))
                df = pd.DataFrame(projection)
                df = df.set_index('Month')
                st.metric("Net Worth Velocity", f"₹{projection[-1]['velocity']:, .2f} / month")
                st.line_chart(df[['Assets', 'Liabilities', 'Net Worth']])
                convergence = next((row['Month'] for row in projection if row['Net Worth'] >= 0), None)
                if convergence:
                    st.success(f"Projected net worth convergence in {convergence} months.")
                else:
                    st.info("Net worth stays below zero during the projection horizon.")
