# save_export_test.py
from loan_calc import generate_loan_schedule
from excel_export import export_comparison_excel

s1 = generate_loan_schedule(300000.0, 8.0, 180, extra_payment_amount=1000.0, extra_payment_type='recurring', extra_payment_start_month=1)
s2 = generate_loan_schedule(300000.0, 8.0, 240)
xlsx = export_comparison_excel([('Loan A', s1), ('Loan B', s2)])
with open('debug_loan_comparison.xlsx', 'wb') as f:
    f.write(xlsx)
print('Wrote debug_loan_comparison.xlsx')