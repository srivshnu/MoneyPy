import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from loan_calc import generate_loan_schedule


def render():
    st.markdown("## 📊 Amortization Charts")
    st.markdown("---")

    with st.form('chart_form'):
        principal = st.number_input("Loan Principal (₹)", min_value=1000.0, value=500000.0, step=1000.0, format="%.2f")
        rate = st.number_input("Annual Interest Rate (%)", min_value=0.0, value=8.5, step=0.1, format="%.2f")
        tenure = st.number_input("Tenure (Months)", min_value=1, value=60, step=1)
        submitted = st.form_submit_button("Generate Charts")

    if submitted:
        summary = generate_loan_schedule(principal, rate, tenure)

        st.markdown("### Outstanding Balance Over Time")
        df = pd.DataFrame({
            'Month': [r.period for r in summary.schedule],
            'Outstanding': [r.opening_balance for r in summary.schedule]
        }).set_index('Month')
        fig = px.line(df.reset_index(), x='Month', y='Outstanding', title='Outstanding Balance Over Time')
        fig.update_traces(mode='lines', line=dict(width=2, color='#2E75B6'))
        fig.update_layout(height=400)
        st.plotly_chart(fig, width='stretch')

        st.markdown("### Principal vs Interest (Total)")
        pie_df = pd.DataFrame({'Label': ['Principal', 'Interest'], 'Value': [summary.principal, summary.total_interest]})
        fig = px.pie(pie_df, values='Value', names='Label', title='Principal vs Interest', hole=0)
        st.plotly_chart(fig, width='stretch')
