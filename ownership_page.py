import streamlit as st
import pandas as pd
import plotly.express as px
from loan_calc import generate_loan_schedule
from decimal import Decimal


def render():
    st.markdown("## 🧾 Co-ownership / Equity Contribution Tracker")
    st.markdown("---")

    with st.form('ownership_form'):
        col1, col2, col3 = st.columns(3)
        with col1:
            total_price = st.number_input("Property Price / Loan Principal (₹)", min_value=1.0, value=500000.0, step=1000.0, format="%.2f")
        with col2:
            annual_rate = st.number_input("Annual Interest Rate (%)", min_value=0.0, value=8.5, step=0.1, format="%.2f")
        with col3:
            tenure = st.number_input("Tenure (Months)", min_value=1, value=60, step=1)

        st.markdown("**Down payment(s)** — amounts each owner contributed toward purchase (will be subtracted from principal)")
        num = st.number_input("Number of co-owners", min_value=1, max_value=8, value=2, step=1)

        owners = []
        owner_cols = st.columns(num)
        owner_inputs = []
        for i in range(num):
            with owner_cols[i]:
                name = st.text_input(f"Owner {i+1} name", value=f"Owner {i+1}", key=f"name_{i}")
                down = st.number_input(f"Down payment (₹)", min_value=0.0, value=0.0, step=100.0, key=f"down_{i}", format="%.2f")
                monthly_share = st.number_input(f"Monthly EMI share (%)", min_value=0.0, max_value=100.0, value=round(100.0/num,2), step=1.0, key=f"share_{i}")
                extra_type = st.selectbox(f"Extra type", options=['none','one-time','recurring'], index=0, key=f"etype_{i}")
                extra_amount = st.number_input(f"Extra amount (₹)", min_value=0.0, value=0.0, step=100.0, key=f"extra_{i}", format="%.2f")
                extra_start = st.number_input(f"Extra start month", min_value=1, max_value=10000, value=1, step=1, key=f"estart_{i}")
                owners.append({
                    'name': name,
                    'down': float(down),
                    'share_pct': float(monthly_share),
                    'extra_type': extra_type,
                    'extra_amount': float(extra_amount),
                    'extra_start': int(extra_start),
                })

        submitted = st.form_submit_button('Compute Ownership Over Time', width='stretch')

    if not submitted:
        return

    # Normalize shares
    total_share = sum(o['share_pct'] for o in owners)
    if total_share == 0:
        st.error('Sum of monthly shares must be > 0')
        return
    # validate owner names
    missing = []
    for i, o in enumerate(owners):
        if not o['name'] or str(o['name']).strip() == '':
            missing.append(f'Owner {i+1}: name')
        if o['share_pct'] <= 0:
            missing.append(f'Owner {i+1}: monthly share percentage must be > 0')
    if missing:
        st.error('Please provide the following required details:\n' + '\n'.join(f'- {m}' for m in missing))
        return
    for o in owners:
        o['share'] = o['share_pct'] / total_share

    # Compute loan principal reduced by total down payments
    total_down = sum(o['down'] for o in owners)
    if total_down > total_price:
        st.error('Total down payment exceeds price')
        return
    loan_principal = float(Decimal(str(total_price)) - Decimal(str(total_down)))

    # Build combined per-period extra payments from owners (estimate length by tenure)
    # We'll first create candidate per-period extras for the original tenure; generate schedule will trim if loan pays off earlier.
    per_period_extras = {}
    for i in range(1, int(tenure) + 1):
        per_period_extras[i] = 0.0
    for o in owners:
        if o['extra_type'] == 'recurring' and o['extra_amount'] > 0:
            for m in range(o['extra_start'], int(tenure) + 1):
                per_period_extras[m] = per_period_extras.get(m, 0.0) + o['extra_amount']
        elif o['extra_type'] == 'one-time' and o['extra_amount'] > 0:
            per_period_extras[o['extra_start']] = per_period_extras.get(o['extra_start'], 0.0) + o['extra_amount']

    # Generate schedule using combined extras
    schedule = generate_loan_schedule(loan_principal, annual_rate, int(tenure), extra_payments_by_period=per_period_extras)

    # For each period, determine owner contributions (principal share + portion of extras)
    owner_cumul = {o['name']: Decimal('0.00') for o in owners}
    periods = []
    total_principal_recovered = Decimal('0.00')

    for row in schedule.schedule:
        period = row.period
        row_principal = Decimal(str(row.principal))
        row_extra = Decimal(str(getattr(row, 'extra_payment', 0.0)))
        base_principal = (row_principal - row_extra).quantize(Decimal('0.01'))

        # Owner base principal share
        base_shares = {o['name']: (base_principal * Decimal(str(o['share']))).quantize(Decimal('0.01')) for o in owners}

        # Owner requested extras for this period
        owner_requested_extras = {}
        for o in owners:
            req = Decimal('0.00')
            if o['extra_type'] == 'recurring' and period >= o['extra_start']:
                req = Decimal(str(o['extra_amount']))
            elif o['extra_type'] == 'one-time' and period == o['extra_start']:
                req = Decimal(str(o['extra_amount']))
            owner_requested_extras[o['name']] = req
        total_requested = sum(owner_requested_extras.values())

        # Scale owner extras if schedule applied less (e.g., final period)
        owner_actual_extras = {name: Decimal('0.00') for name in owner_requested_extras}
        if total_requested == Decimal('0.00'):
            pass
        else:
            total_requested = Decimal(str(total_requested))
            if total_requested == row_extra or row_extra == Decimal('0.00'):
                for name, req in owner_requested_extras.items():
                    owner_actual_extras[name] = req
            else:
                # scale factor
                factor = Decimal(str(row_extra)) / total_requested
                for name, req in owner_requested_extras.items():
                    owner_actual_extras[name] = (Decimal(str(req)) * factor).quantize(Decimal('0.01'))

        # Sum owner contributions for this period
        for o in owners:
            name = o['name']
            contrib = base_shares[name] + owner_actual_extras.get(name, Decimal('0.00'))
            owner_cumul[name] += contrib
            total_principal_recovered += contrib

        # compute ownership shares at this period
        denom = Decimal(str(total_down)) + total_principal_recovered
        period_ownership = {}
        for o in owners:
            name = o['name']
            numer = Decimal(str(o['down'])) + owner_cumul[name]
            pct = (numer / denom * Decimal('100')) if denom != Decimal('0.00') else Decimal('0.00')
            period_ownership[name] = float(pct.quantize(Decimal('0.01')))

        periods.append({'period': period, 'ownership': period_ownership, 'total_recovered': float(total_principal_recovered)})

    # Present results: final ownership
    final = periods[-1]
    st.markdown('### Final Ownership (%)')
    final_df = pd.DataFrame([{ 'Owner': name, 'Ownership %': final['ownership'][name], 'Down Payment (₹)': o['down'], 'Cumulative Principal Paid (₹)': float(owner_cumul[name]) } for name, o in zip(final['ownership'].keys(), owners)])
    st.dataframe(final_df.sort_values('Ownership %', ascending=False), width='stretch', hide_index=True)

    # Show ownership over time plot
    plot_df = []
    for p in periods:
        for name, pct in p['ownership'].items():
            plot_df.append({'Month': p['period'], 'Owner': name, 'Ownership %': pct})
    plot_df = pd.DataFrame(plot_df)
    fig = px.line(plot_df, x='Month', y='Ownership %', color='Owner', markers=True, title='Ownership % over time')
    st.plotly_chart(fig, width='stretch')

    # Detailed per-period table (first few and last few)
    expanded = st.checkbox('Show full period breakdown')
    if expanded:
        rows = []
        for p in periods:
            row = {'Month': p['period']}
            row.update(p['ownership'])
            rows.append(row)
        detail_df = pd.DataFrame(rows)
        st.dataframe(detail_df, width='stretch', hide_index=True)
