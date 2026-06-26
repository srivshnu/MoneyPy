import streamlit as st
import os
import importlib.util

# Helper to load module from a file path

def load_module_from_path(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

BASE_DIR = os.path.dirname(__file__)
LOAN_PAGE = os.path.join(BASE_DIR, "loan_page.py")
INV_PAGE = os.path.join(BASE_DIR, "investment_page.py")
PAY_PAGE = os.path.join(BASE_DIR, "payment_to_tenure.py")
OWNERSHIP_PAGE = os.path.join(BASE_DIR, "ownership_page.py")

loan_mod = load_module_from_path(LOAN_PAGE, "loan_page")
inv_mod = load_module_from_path(INV_PAGE, "investment_page")
pay_mod = load_module_from_path(PAY_PAGE, "payment_to_tenure")

st.set_page_config(page_title="Finance Tools", layout="wide")


choice = st.sidebar.radio("Choose tool", [
    "Loan Calculator",
    "Payment → Tenure",
    "Investment Calculator",
    "Personal Planning Hub",
    "Prepayment Impact",
    "Amortization Charts",
    "Multi-Loan Comparison",
    "Co-ownership Tracker",
]) 

if choice == "Loan Calculator":
    loan_mod.render()
elif choice == "Payment → Tenure":
    pay_mod.render()
elif choice == "Investment Calculator":
    inv_mod.render()
elif choice == "Personal Planning Hub":
    plan_mod = load_module_from_path(os.path.join(BASE_DIR, "planning_page.py"), "planning_page")
    plan_mod.render()
elif choice == "Prepayment Impact":
    prepay_mod = load_module_from_path(os.path.join(BASE_DIR, "prepayment_page.py"), "prepayment_page")
    prepay_mod.render()
elif choice == "Amortization Charts":
    charts_mod = load_module_from_path(os.path.join(BASE_DIR, "charts_page.py"), "charts_page")
    charts_mod.render()
elif choice == "Multi-Loan Comparison":
    compare_mod = load_module_from_path(os.path.join(BASE_DIR, "multi_loan_page.py"), "multi_loan_page")
    compare_mod.render()
elif choice == "Co-ownership Tracker":
    own_mod = load_module_from_path(os.path.join(BASE_DIR, "ownership_page.py"), "ownership_page")
    own_mod.render()
else:
    inv_mod.render()