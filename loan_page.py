import streamlit as st
import pandas as pd
import sys, os
# Ensure this folder is on sys.path so local modules import reliably
sys.path.insert(0, os.path.dirname(__file__))

import decimal
from loan_calc import generate_loan_schedule, compute_tenure_from_payment
from excel_export import export_loan_excel


def render():
    st.markdown("## 🏦 Loan Calculator — Reducing Balance (EMI)")
    st.markdown("---")

    with st.form("loan_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            principal = st.number_input("Loan Principal (₹)", min_value=1000.0,
                                         max_value=1_00_00_00_000.0, value=5_00_000.0,
                                         step=1000.0, format="%.2f")
        with col2:
            rate = st.number_input("Annual Interest Rate (%)", min_value=0.1,
                                    max_value=50.0, value=8.5, step=0.1, format="%.2f")
        with col3:
            tenure = st.number_input("Tenure (Months)", min_value=1,
                                      max_value=480, value=60, step=1)

        # Extra / Prepayment options (always visible; enter 0 to disable)
        st.markdown("""**Extra / Prepayment options (enter 0 to disable)**""")
        extra_type = st.radio("Extra payment type", options=['none', 'one-time', 'recurring'])
        extra_amount = st.number_input("Extra Payment Amount (₹)", min_value=0.0, value=0.0, step=100.0, format="%.2f")
        extra_start = st.number_input("Start Month for Extra Payment (1-based)", min_value=1, max_value=10000, value=1, step=1)
        rate_schedule_text = st.text_input("Rate schedule (format: start_month:rate, e.g. 1:8.5,13:9.0)", value="")

        # (Tax deduction inputs removed)

        submitted = st.form_submit_button("📊 Calculate EMI", width='stretch')

    if submitted:
        # Parse rate schedule if provided
        rate_schedule = None
        if rate_schedule_text.strip():
            try:
                parts = [p.strip() for p in rate_schedule_text.split(',') if p.strip()]
                rate_schedule = []
                for part in parts:
                    s, rt = part.split(':')
                    rate_schedule.append((int(s), float(rt)))
            except Exception as e:
                st.error(f"Could not parse rate schedule: {e}")
                return

        summary = generate_loan_schedule(
            principal, rate, tenure,
            rate_schedule=rate_schedule,
            extra_payment_amount=extra_amount if extra_type != 'none' else 0.0,
            extra_payment_type=extra_type if extra_type != 'none' else 'none',
            extra_payment_start_month=extra_start if extra_type != 'none' else 1,
        )

        # ── KPI cards ──
        st.markdown("### 📌 Loan Summary")
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Monthly EMI", f"₹{summary.emi:,.2f}")
        k2.metric("Total Payment", f"₹{summary.total_payment:,.2f}")
        k3.metric("Total Interest", f"₹{summary.total_interest:,.2f}")
        k4.metric("Interest %", f"{summary.total_interest/summary.principal*100:.1f}%")

        st.markdown("---")

        # (Tax deduction display removed)

        # ── Chart ──
        st.markdown("### 📈 Principal vs Interest (Running)")
        chart_data = pd.DataFrame({
            "Month": [r.period for r in summary.schedule],
            "Principal Paid (Cumulative)": [
                sum(x.principal for x in summary.schedule[:i+1])
                for i in range(len(summary.schedule))
            ],
            "Interest Paid (Cumulative)": [
                sum(x.interest for x in summary.schedule[:i+1])
                for i in range(len(summary.schedule))
            ],
            "Outstanding Balance": [r.closing_balance for r in summary.schedule],
        }).set_index("Month")
        st.line_chart(chart_data)

        # ── Table ──
        actual_months = len(summary.schedule)
        years = actual_months // 12
        months = actual_months % 12
        dur_parts = []
        if years:
            dur_parts.append(f"{years} year{'s' if years>1 else ''}")
        if months:
            dur_parts.append(f"{months} month{'s' if months>1 else ''}")
        dur_text = ' '.join(dur_parts) if dur_parts else '0 months'
        st.markdown(f"### 📋 Amortization Schedule — {actual_months} months ({dur_text})")

        df = pd.DataFrame([{
            "Month":             r.period,
            "Opening Balance (₹)": f"₹{r.opening_balance:,.2f}",
            "EMI (₹)":           f"₹{r.emi:,.2f}",
            "Extra Payment (₹)": f"₹{getattr(r, 'extra_payment', 0.0):,.2f}",
            "Principal (₹)":     f"₹{r.principal:,.2f}",
            "Interest (₹)":      f"₹{r.interest:,.2f}",
            "Closing Balance (₹)": f"₹{r.closing_balance:,.2f}",
        } for r in summary.schedule])
        st.dataframe(df, width='stretch', hide_index=True)

        # ── Download ──
        xlsx_bytes = export_loan_excel(summary)
        st.download_button(
            label="⬇️  Download Excel Report",
            data=xlsx_bytes,
            file_name="loan_amortization.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            width='stretch',
        )