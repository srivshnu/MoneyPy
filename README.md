# Financial Calculators Suite

A professional financial computing and analysis toolkit built with Python and Streamlit. This suite provides high-precision calculations for reducing balance loans, prepayment options, annual tax deduction logic, and diverse investment pathways including Fixed Deposits (FD), Recurring Deposits (RD), and Compound Interest (CI) schedules.

## Features

### 1. Loan & Core Calculations
* **Reducing Balance (EMI) Engine:** Computes stable reducing balance loans with robust Decimal precision to avoid fractional floating-point inaccuracies.
* **Prepayment & Rate Schedules:** Supports flexible simulations for one-time or recurring prepayments and multi-period interest rate adjustments.
* **Tax Benefit Estimator:** Dynamically groups amortization schedules into yearly periods, capping output against configurable investment parameters (such as Section 80C and 24b constraints).
* **Payment to Tenure:** Resolves reverse loan parameters to determine the total months required to clear liabilities given a fixed premium target.

### New Interactive Tools (added)
- **Prepayment Impact Calculator:** Shows interest saved and months reduced for one-time or recurring prepayments.
- **Amortization Charts:** Line and pie charts for outstanding balance and principal vs interest breakdown.
- **Multi-Loan Comparison:** Side-by-side comparison of two loan scenarios (different tenures, rates, or extra payments).
- **Multi-Loan Comparison:** Side-by-side comparison of multiple loan scenarios (different tenures, rates, or extra payments). The UI now accepts a user-specified number of loans (2–8) and dynamically generates input fields for each loan. After pressing "Compare Loans" the app shows:
	- A summary metrics table (EMI, Tenure, Total Payment, Total Interest) for each loan.
	- A combined outstanding-balance line chart across all loans.
	- Pairwise deltas vs the first loan (Δ EMI, Δ Total Interest, Δ Tenure).

Usage tip: open the "Multi-Loan Comparison" page in the app, set "Number of loans to compare", fill the loan fields, then press "Compare Loans". The first loan entered is used as the reference for pairwise deltas.

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

Recommended (create and activate a virtual environment first):

Windows (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

Windows (cmd.exe):

```cmd
python -m venv .venv
.\.venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt
```

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Dependencies

* **streamlit:** User interface construction and real-time telemetry rendering.
* **pandas:** In-memory tabular structures and data framing.
* **openpyxl:** Production-ready file output composition.
* **pytest:** Mathematical accuracy and validation suite.

## Execution

To deploy the user interface wrapper locally, initialize the Streamlit runtime against the core layout script:

From the project root (activate your virtual env first):

```bash
streamlit run app.py
```

Streamlit will start a local server (default http://localhost:8501). If the browser doesn't open automatically, paste the printed URL into your browser.

If you prefer a specific port, use:

```bash
streamlit run app.py --server.port 8502
```

## Testing and Verification

Unit tests

Preferred: if you have `pytest` installed, run the full test suite:

```bash
pytest -q
```

Fallback: if `pytest` is not available in your environment, there's a lightweight runner included. From the project root run:

```bash
python run_tests.py
```

Both methods execute the loan engine and new feature tests (prepayment and multi-loan comparisons). Use the console output to inspect any failing assertions.

Troubleshooting

- If `streamlit run app.py` exits with code 1, check the console for the error stack. Common causes:
	- Missing dependencies: activate your virtual environment and re-run `pip install -r requirements.txt`.
	- Port conflicts: specify `--server.port` as shown above.
	- Import errors: ensure you run from the project root where `app.py` resides.

- If `pytest` is not found and you prefer it, install it with:

```bash
pip install pytest
```

Notes

- Primary UI pages are implemented in `loan_page.py`, `prepayment_page.py`, `charts_page.py`, and `multi_loan_page.py`.
- Computational logic lives in `logic/` (`loan_calc.py`, `prepayment.py`, `multi_loan.py`).
- Excel export uses `excel_export.py` and requires `openpyxl` (listed in `requirements.txt`).
