import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from logic.prepayment import compute_prepayment_impact
from ui_helpers import validate_required


def render():
    st.markdown("## 💸 Prepayment Impact Calculator")
    st.markdown("---")

    with st.form('prepay'):
        col1, col2, col3 = st.columns(3)
        with col1:
            principal = st.number_input("Loan Principal (₹)", min_value=1000.0, value=500000.0, step=1000.0, format="%.2f")
        with col2:
            rate = st.number_input("Annual Interest Rate (%)", min_value=0.0, value=8.5, step=0.1, format="%.2f")
        with col3:
            tenure = st.number_input("Tenure (Months)", min_value=1, value=60, step=1)

        extra_type = st.radio("Extra payment type", options=['none', 'one-time', 'recurring'])
        extra_amount = st.number_input("Extra Payment Amount (₹)", min_value=0.0, value=0.0, step=100.0, format="%.2f")
        extra_start = st.number_input("Start Month for Extra Payment (1-based)", min_value=1, value=1, step=1)

        submitted = st.form_submit_button("Compute Impact")

    if submitted:
        missing = validate_required({
            'Loan Principal': principal,
            'Annual Interest Rate (%)': rate,
            'Tenure (Months)': tenure,
        })
        if missing:
            return

        # if extra payment specified, ensure amount is provided
        if extra_type != 'none' and (extra_amount is None or extra_amount <= 0):
            st.error('Extra payment selected but no extra amount provided.')
            return

        result = compute_prepayment_impact(principal, rate, tenure, extra_amount, extra_type, extra_start)

        orig = result['original']
        upd = result['updated']

        st.markdown("### Summary")
        c1, c2, c3 = st.columns(3)
        c1.metric("Original Total Interest", f"₹{orig.total_interest:,.2f}")
        c2.metric("New Total Interest", f"₹{upd.total_interest:,.2f}")
        c3.metric("Interest Saved", f"₹{result['interest_saved']:,.2f}")

        c4, c5 = st.columns(2)
        c4.metric("Original Tenure (months)", f"{orig.tenure_months}")
        c5.metric("New Tenure (months)", f"{upd.tenure_months}")
        st.metric("Months Reduced", f"{result['months_saved']}")

        st.markdown("---")
        # Line chart of outstanding balance
        df_orig = pd.DataFrame({"Month": [r.period for r in orig.schedule], "Original": [r.opening_balance for r in orig.schedule]}).set_index('Month')
        df_upd = pd.DataFrame({"Month": [r.period for r in upd.schedule], "With Prepayment": [r.opening_balance for r in upd.schedule]}).set_index('Month')
        combined = pd.concat([df_orig, df_upd], axis=1).fillna(method='ffill')
        # interactive line chart
        plot_df = combined.reset_index().melt(id_vars='Month', value_vars=['Original', 'With Prepayment'], var_name='Scenario', value_name='Outstanding')
        fig = px.line(plot_df, x='Month', y='Outstanding', color='Scenario', title='Outstanding Balance Comparison')
        fig.update_traces(mode='lines', hovertemplate='Month: %{x}<br>Balance: %{y:,.2f}')
        fig.update_layout(height=400)
        st.plotly_chart(fig, width='stretch')

        # Pie charts for principal vs interest
        st.markdown("### Principal vs Interest Breakdown")
        # Use plotly pie charts for interactivity
        pie_df = pd.DataFrame({
            'Label': ['Principal', 'Interest'],
            'Original': [orig.principal, orig.total_interest],
            'With Prepayment': [upd.principal, upd.total_interest],
        })
        fig1 = px.pie(pie_df, values='Original', names='Label', title='Original', hole=0)
        fig2 = px.pie(pie_df, values='With Prepayment', names='Label', title='With Prepayment', hole=0)
        st.plotly_chart(fig1, width='stretch')
        st.plotly_chart(fig2, width='stretch')
