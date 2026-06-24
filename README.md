```markdown
# Financial Calculators Suite

A professional financial computing and analysis toolkit built with Python and Streamlit. This suite provides high-precision calculations for reducing balance loans, prepayment options, annual tax deduction logic, and diverse investment pathways including Fixed Deposits (FD), Recurring Deposits (RD), and Compound Interest (CI) schedules.

## Features

### 1. Loan & Core Calculations
* **Reducing Balance (EMI) Engine:** Computes stable reducing balance loans with robust Decimal precision to avoid fractional floating-point inaccuracies.
* **Prepayment & Rate Schedules:** Supports flexible simulations for one-time or recurring prepayments and multi-period interest rate adjustments.
* **Tax Benefit Estimator:** Dynamically groups amortization schedules into yearly periods, capping output against configurable investment parameters (such as Section 80C and 24b constraints).
* **Payment to Tenure:** Resolves reverse loan parameters to determine the total months required to clear liabilities given a fixed premium target.

### 2. Investment Portfolio Planners
* **Fixed Deposits (FD):** Tracks deposit appreciation over configurable compounding frequencies (Monthly, Quarterly, Half-Yearly, Yearly) with accurate yield metrics.
* **Recurring Deposits (RD):** Models fixed monthly installments, calculating cumulative compounding growth matrices alongside total interest yields.
* **Compound Interest (CI):** Breaks down long-term wealth assets into a clean, multi-year performance structure.

### 3. Data Portability & Reporting
* **Excel Amortization Sheets:** Generates professional-grade multi-sheet workbooks using styling rules, cell formatting masks, headers, alternating data alignments, and terminal balance corrections.

## System Architecture

The codebase relies on strict mathematical and application tier separation:
* `loan_calc.py`: Pure computational engine managing decimal quantization and multi-year tax calculations.
* `investment_calc.py`: Financial model dataclasses and looping algorithms for structural investment plans.
* `excel_export.py`: Template generation layer configured via openpyxl.
* `app.py`: High-level entry routing across modules (`loan_page.py`, `investment_page.py`, `payment_to_tenure.py`).

## Installation

Ensure a standard Python runtime environment is available. Install system dependencies via pip:

```bash
pip install -r requirements.txt

```

## Dependencies

* **streamlit:** User interface construction and real-time telemetry rendering.
* **pandas:** In-memory tabular structures and data framing.
* **openpyxl:** Production-ready file output composition.
* **pytest:** Mathematical accuracy and validation suite.

## Execution

To deploy the user interface wrapper locally, initialize the Streamlit runtime against the core layout script:

```bash
streamlit run app.py

```

## Testing and Verification

Validation checks are handled natively via `pytest`. The engine is checked against varying constraint profiles, including boundary evaluations for zero-interest configurations, structural compliance matrices, and early settlement calculations:

```bash
pytest test_loan_calc.py -v

```

```

```