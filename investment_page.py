import streamlit as st
import pandas as pd
import sys, os
# Ensure local folder is on sys.path so imports resolve reliably
sys.path.insert(0, os.path.dirname(__file__))

from investment_calc import generate_fd_schedule, generate_rd_schedule, generate_ci_schedule
from excel_export import export_fd_excel, export_rd_excel, export_ci_excel
from ui_helpers import validate_required

COMPOUNDING_OPTIONS = ["Monthly", "Quarterly", "Half-Yearly", "Yearly"]


def render():
    st.markdown("## 💰 Investment Calculator")
    st.markdown("---")

    tab_fd, tab_rd, tab_ci = st.tabs(["📄 Fixed Deposit (FD)", "🔄 Recurring Deposit (RD)", "📈 Compound Interest"])

    # ── FD ────────────────────────────────────────────────────────────────────
    with tab_fd:
        st.markdown("### Fixed Deposit")
        with st.form("fd_form"):
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                fd_principal = st.number_input("Principal (₹)", min_value=500.0,
                                                value=1_00_000.0, step=500.0, format="%.2f", key="fd_p")
            with c2:
                fd_rate = st.number_input("Annual Rate (%)", min_value=0.1,
                                           max_value=20.0, value=7.0, step=0.1, format="%.2f", key="fd_r")
            with c3:
                fd_tenure = st.number_input("Tenure (Months)", min_value=1,
                                             max_value=120, value=12, step=1, key="fd_t")
            with c4:
                fd_comp = st.selectbox("Compounding", COMPOUNDING_OPTIONS, index=1, key="fd_c")
            fd_submit = st.form_submit_button("📊 Calculate FD", width='stretch')

        if fd_submit:
            missing = validate_required({
                'FD Principal': fd_principal,
                'FD Annual Rate (%)': fd_rate,
                'FD Tenure (Months)': fd_tenure,
            })
            if missing:
                return
            s = generate_fd_schedule(fd_principal, fd_rate, fd_tenure, fd_comp)

            k1, k2, k3, k4 = st.columns(4)
            k1.metric("Principal", f"₹{s.principal:,.2f}")
            k2.metric("Maturity Amount", f"₹{s.maturity_amount:,.2f}")
            k3.metric("Total Interest", f"₹{s.total_interest:,.2f}")
            k4.metric("Effective Yield", f"{s.total_interest/s.principal*100:.2f}%")

            st.markdown("#### 📈 Balance Growth")
            chart = pd.DataFrame({
                "Month": [r.period for r in s.schedule],
                "Balance (₹)": [r.closing_balance for r in s.schedule],
                "Cumulative Interest (₹)": [r.cumulative_interest for r in s.schedule],
            }).set_index("Month")
            st.line_chart(chart)

            st.markdown("#### 📋 Monthly Breakup")
            df = pd.DataFrame([{
                "Month":                    r.period,
                "Opening Balance (₹)":      f"₹{r.opening_balance:,.2f}",
                "Interest Earned (₹)":      f"₹{r.interest_earned:,.2f}",
                "Closing Balance (₹)":      f"₹{r.closing_balance:,.2f}",
                "Cumulative Interest (₹)":  f"₹{r.cumulative_interest:,.2f}",
            } for r in s.schedule])
            st.dataframe(df, width='stretch', hide_index=True)

            xlsx = export_fd_excel(s)
            st.download_button("⬇️  Download FD Excel Report", xlsx,
                               "fd_report.xlsx",
                               "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                               width='stretch')

    # ── RD ────────────────────────────────────────────────────────────────────
    with tab_rd:
        st.markdown("### Recurring Deposit")
        with st.form("rd_form"):
            c1, c2, c3 = st.columns(3)
            with c1:
                rd_install = st.number_input("Monthly Installment (₹)", min_value=100.0,
                                              value=5_000.0, step=100.0, format="%.2f", key="rd_i")
            with c2:
                rd_rate = st.number_input("Annual Rate (%)", min_value=0.1,
                                           max_value=20.0, value=6.5, step=0.1, format="%.2f", key="rd_r")
            with c3:
                rd_tenure = st.number_input("Tenure (Months)", min_value=6,
                                             max_value=120, value=24, step=1, key="rd_t")
            rd_submit = st.form_submit_button("📊 Calculate RD", width='stretch')

        if rd_submit:
            missing = validate_required({
                'RD Monthly Installment': rd_install,
                'RD Annual Rate (%)': rd_rate,
                'RD Tenure (Months)': rd_tenure,
            })
            if missing:
                return
            s = generate_rd_schedule(rd_install, rd_rate, rd_tenure)

            k1, k2, k3, k4 = st.columns(4)
            k1.metric("Total Deposited", f"₹{s.total_deposited:,.2f}")
            k2.metric("Maturity Amount", f"₹{s.maturity_amount:,.2f}")
            k3.metric("Total Interest", f"₹{s.total_interest:,.2f}")
            k4.metric("Effective Yield", f"{s.total_interest/s.total_deposited*100:.2f}%")

            st.markdown("#### 📈 Deposit Growth")
            chart = pd.DataFrame({
                "Month": [r.period for r in s.schedule],
                "Total Deposited (₹)": [r.total_deposited for r in s.schedule],
                "Closing Balance (₹)": [r.closing_balance for r in s.schedule],
            }).set_index("Month")
            st.line_chart(chart)

            st.markdown("#### 📋 Monthly Breakup")
            df = pd.DataFrame([{
                "Month":                    r.period,
                "Installment (₹)":          f"₹{r.installment:,.2f}",
                "Opening Balance (₹)":      f"₹{r.opening_balance:,.2f}",
                "Interest Earned (₹)":      f"₹{r.interest_earned:,.2f}",
                "Closing Balance (₹)":      f"₹{r.closing_balance:,.2f}",
                "Total Deposited (₹)":      f"₹{r.total_deposited:,.2f}",
                "Cumulative Interest (₹)":  f"₹{r.cumulative_interest:,.2f}",
            } for r in s.schedule])
            st.dataframe(df, width='stretch', hide_index=True)

            xlsx = export_rd_excel(s)
            st.download_button("⬇️  Download RD Excel Report", xlsx,
                               "rd_report.xlsx",
                               "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                               width='stretch')

    # ── CI ────────────────────────────────────────────────────────────────────
    with tab_ci:
        st.markdown("### Compound Interest Investment")
        with st.form("ci_form"):
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                ci_principal = st.number_input("Principal (₹)", min_value=500.0,
                                                value=1_00_000.0, step=500.0, format="%.2f", key="ci_p")
            with c2:
                ci_rate = st.number_input("Annual Rate (%)", min_value=0.1,
                                           max_value=30.0, value=8.0, step=0.1, format="%.2f", key="ci_r")
            with c3:
                ci_years = st.number_input("Tenure (Years)", min_value=1,
                                            max_value=40, value=5, step=1, key="ci_y")
            with c4:
                ci_comp = st.selectbox("Compounding", COMPOUNDING_OPTIONS, index=0, key="ci_c")
            ci_submit = st.form_submit_button("📊 Calculate CI", width='stretch')

        if ci_submit:
            missing = validate_required({
                'CI Principal': ci_principal,
                'CI Annual Rate (%)': ci_rate,
                'CI Tenure (Years)': ci_years,
            })
            if missing:
                return
            s = generate_ci_schedule(ci_principal, ci_rate, ci_years, ci_comp)

            k1, k2, k3, k4 = st.columns(4)
            k1.metric("Principal", f"₹{s.principal:,.2f}")
            k2.metric("Maturity Amount", f"₹{s.maturity_amount:,.2f}")
            k3.metric("Total Interest", f"₹{s.total_interest:,.2f}")
            k4.metric("Effective Yield", f"{s.total_interest/s.principal*100:.2f}%")

            st.markdown("#### 📈 Yearly Growth")
            chart = pd.DataFrame({
                "Year": [r.year for r in s.schedule],
                "Closing Balance (₹)": [r.closing_balance for r in s.schedule],
                "Cumulative Interest (₹)": [r.cumulative_interest for r in s.schedule],
            }).set_index("Year")
            st.line_chart(chart)

            st.markdown("#### 📋 Yearly Breakup")
            df = pd.DataFrame([{
                "Year":                     r.year,
                "Opening Balance (₹)":      f"₹{r.opening_balance:,.2f}",
                "Interest Earned (₹)":      f"₹{r.interest_earned:,.2f}",
                "Closing Balance (₹)":      f"₹{r.closing_balance:,.2f}",
                "Cumulative Interest (₹)":  f"₹{r.cumulative_interest:,.2f}",
            } for r in s.schedule])
            st.dataframe(df, width='stretch', hide_index=True)

            xlsx = export_ci_excel(s)
            st.download_button("⬇️  Download CI Excel Report", xlsx,
                               "ci_report.xlsx",
                               "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                               width='stretch')