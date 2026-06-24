import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from loan_calc import generate_loan_schedule
from excel_export import export_comparison_excel


def render():
    st.markdown("## 🔁 Multi-Loan Comparison")
    st.markdown("---")

    num = st.number_input("Number of loans to compare", min_value=2, max_value=8, value=2, step=1)

    # collect inputs inside a single form so all values submit together
    with st.form('multi_compare'):
        loans = []
        for i in range(int(num)):
            st.markdown(f"**Loan {i+1}**")
            col1, col2, col3 = st.columns(3)
            with col1:
                p = st.number_input(f"Principal (₹)", key=f'p_{i}', min_value=0.0, value=500000.0, step=1000.0, format="%.2f")
            with col2:
                r = st.number_input(f"Annual Rate (%)", key=f'r_{i}', min_value=0.0, value=8.5, step=0.1, format="%.2f")
            with col3:
                t = st.number_input(f"Tenure (months)", key=f't_{i}', min_value=1, value=60, step=1)
            # extra payment inputs
            c4, c5, c6 = st.columns(3)
            with c4:
                extra_amt = st.number_input(f"Extra Payment Amount (₹)", key=f'ex_amt_{i}', min_value=0.0, value=0.0, step=100.0, format="%.2f")
            with c5:
                extra_type = st.selectbox(f"Extra Payment Type", options=['none', 'one-time', 'recurring'], key=f'ex_type_{i}')
            with c6:
                extra_start = st.number_input(f"Extra Start Month", key=f'ex_start_{i}', min_value=1, value=1, step=1)

            loans.append({
                'principal': float(p),
                'annual_rate': float(r),
                'tenure_months': int(t),
                'extra_payment_amount': float(extra_amt),
                'extra_payment_type': extra_type,
                'extra_payment_start_month': int(extra_start),
            })

        submitted = st.form_submit_button("Compare Loans")

    if submitted:
        summaries = []
        for idx, params in enumerate(loans):
            s = generate_loan_schedule(
                params['principal'], params['annual_rate'], params['tenure_months'],
                extra_payment_amount=params.get('extra_payment_amount', 0.0),
                extra_payment_type=params.get('extra_payment_type', 'none'),
                extra_payment_start_month=params.get('extra_payment_start_month', 1),
            )
            summaries.append((f"Loan {idx+1}", s))

        # Metrics table
        rows = []
        for name, s in summaries:
            rows.append({
                'Loan': name,
                'EMI': s.emi,
                'Tenure (months)': s.tenure_months,
                'Total Payment': s.total_payment,
                'Total Interest': s.total_interest,
            })
        df = pd.DataFrame(rows).set_index('Loan')
        # formatted display
        df_display = df.copy()
        df_display['EMI'] = df_display['EMI'].apply(lambda x: f"₹{x:,.2f}")
        df_display['Total Payment'] = df_display['Total Payment'].apply(lambda x: f"₹{x:,.2f}")
        df_display['Total Interest'] = df_display['Total Interest'].apply(lambda x: f"₹{x:,.2f}")
        st.markdown("### Summary Metrics")
        st.dataframe(df_display, use_container_width=True)

        st.markdown("---")
        # Combined outstanding balance chart (interactive Plotly)
        balance_frames = []
        for name, s in summaries:
            dfb = pd.DataFrame({'Month': [r.period for r in s.schedule], 'Outstanding': [r.opening_balance for r in s.schedule]})
            dfb['Loan'] = name
            balance_frames.append(dfb)
        combined_df = pd.concat(balance_frames, axis=0)
        fig = px.line(combined_df, x='Month', y='Outstanding', color='Loan', title='Outstanding Balance Comparison')
        fig.update_traces(mode='lines', hovertemplate='Month: %{x}<br>Balance: %{y:,.2f}')
        fig.update_layout(legend_title_text='Loan', height=400)
        st.plotly_chart(fig, use_container_width=True)

        # Export button
        try:
            xlsx = export_comparison_excel(summaries)
            st.download_button(label="⬇️ Download Comparison Excel", data=xlsx, file_name="loan_comparison.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        except Exception as e:
            st.error(f"Could not create Excel export: {e}")

        # Optional pairwise deltas vs first loan
        base_name, base_s = summaries[0]
        deltas = []
        for name, s in summaries[1:]:
            deltas.append({
                'Comparison': f"{name} vs {base_name}",
                'Δ EMI': round(s.emi - base_s.emi, 2),
                'Δ Total Interest': round(s.total_interest - base_s.total_interest, 2),
                'Δ Total Payment': round(s.total_payment - base_s.total_payment, 2),
                'Δ Tenure (months)': s.tenure_months - base_s.tenure_months,
            })
        if deltas:
            deltas_df = pd.DataFrame(deltas)
            deltas_display = deltas_df.copy()
            deltas_display['Δ EMI'] = deltas_display['Δ EMI'].apply(lambda x: f"₹{x:,.2f}")
            deltas_display['Δ Total Interest'] = deltas_display['Δ Total Interest'].apply(lambda x: f"₹{x:,.2f}")
            deltas_display['Δ Total Payment'] = deltas_display['Δ Total Payment'].apply(lambda x: f"₹{x:,.2f}")
            st.markdown("### Pairwise Deltas (vs first loan)")
            st.dataframe(deltas_display, use_container_width=True)

            # Provide CSV and Excel downloads for deltas
            csv_bytes = deltas_df.to_csv(index=False).encode('utf-8')
            st.download_button(label="⬇️ Download Deltas CSV", data=csv_bytes, file_name="loan_deltas.csv", mime='text/csv')

            # Excel summary with pandas
            try:
                import io
                buf = io.BytesIO()
                with pd.ExcelWriter(buf, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name='Summary')
                    deltas_df.to_excel(writer, sheet_name='Deltas', index=False)
                buf.seek(0)
                st.download_button(label="⬇️ Download Summary Excel", data=buf.getvalue(), file_name='loan_summary.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            except Exception as e:
                st.error(f"Could not create summary Excel: {e}")
