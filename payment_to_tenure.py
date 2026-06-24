import streamlit as st
import pandas as pd
import sys, os
# Ensure this folder is on sys.path so local modules import reliably
sys.path.insert(0, os.path.dirname(__file__))

from loan_calc import generate_loan_schedule, compute_tenure_from_payment
from excel_export import export_loan_excel


def render():
    st.markdown("## 💸 Payment → Tenure Calculator")
    st.markdown("---")

    with st.form("pay_form"):
        col1, col2 = st.columns(2)
        with col1:
            principal = st.number_input("Loan Principal (₹)", min_value=1000.0,
                                         max_value=1_00_00_00_000.0, value=5_00_000.0,
                                         step=1000.0, format="%.2f")
        with col2:
            rate = st.number_input("Annual Interest Rate (%)", min_value=0.0,
                                    max_value=50.0, value=8.5, step=0.1, format="%.2f")

        monthly_payment = st.number_input("Desired Monthly Payment (₹)", min_value=1.0,
                                          value=10000.0, step=100.0, format="%.2f")

        submitted = st.form_submit_button("🔢 Compute Tenure", use_container_width=True)

    if submitted:
        try:
            months = compute_tenure_from_payment(principal, rate, monthly_payment)
        except ValueError as e:
            st.error(str(e))
            return

        years = months // 12
        rem_months = months % 12
        parts = []
        if years:
            parts.append(f"{years} year{'s' if years>1 else ''}")
        if rem_months:
            parts.append(f"{rem_months} month{'s' if rem_months>1 else ''}")
        dur_text = ' '.join(parts) if parts else '0 months'

        st.success(f"With monthly payment ₹{monthly_payment:,.2f}, loan will be repaid in {months} months ({dur_text}).")

        summary = generate_loan_schedule(principal, rate, months)

        # KPI
        st.markdown("### 📌 Result Summary")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Monthly EMI", f"₹{summary.emi:,.2f}")
        c2.metric("Total Payment", f"₹{summary.total_payment:,.2f}")
        c3.metric("Total Interest", f"₹{summary.total_interest:,.2f}")
        c4.metric("Interest %", f"{summary.total_interest/summary.principal*100:.1f}%")

        # Table
        df = pd.DataFrame([{
            "Month": r.period,
            "Opening Balance (₹)": f"₹{r.opening_balance:,.2f}",
            "EMI (₹)": f"₹{r.emi:,.2f}",
            "Principal (₹)": f"₹{r.principal:,.2f}",
            "Interest (₹)": f"₹{r.interest:,.2f}",
            "Closing Balance (₹)": f"₹{r.closing_balance:,.2f}",
        } for r in summary.schedule])
        st.dataframe(df, use_container_width=True, hide_index=True)

        xlsx_bytes = export_loan_excel(summary)
        st.download_button(
            label="⬇️  Download Excel Report",
            data=xlsx_bytes,
            file_name="payment_to_tenure.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
