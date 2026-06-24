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

loan_mod = load_module_from_path(LOAN_PAGE, "loan_page")
inv_mod = load_module_from_path(INV_PAGE, "investment_page")
pay_mod = load_module_from_path(PAY_PAGE, "payment_to_tenure")

st.set_page_config(page_title="Finance Tools", layout="wide")

choice = st.sidebar.radio("Choose tool", ["Loan Calculator", "Payment → Tenure", "Investment Calculator"]) 

if choice == "Loan Calculator":
    loan_mod.render()
elif choice == "Payment → Tenure":
    pay_mod.render()
else:
    inv_mod.render()