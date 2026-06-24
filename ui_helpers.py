import streamlit as st
from decimal import Decimal

def _is_missing(val):
    if val is None:
        return True
    if isinstance(val, str):
        return val.strip() == ''
    if isinstance(val, (int, float, Decimal)):
        try:
            return float(val) <= 0
        except Exception:
            return False
    return False

def validate_required(field_map: dict) -> list:
    """Given a dict of {display_name: value}, returns list of missing fields.
    Also displays an error dialog listing them if any are missing.
    """
    missing = [name for name, v in field_map.items() if _is_missing(v)]
    if missing:
        msg = "The following required fields are missing or invalid:\n"
        for m in missing:
            msg += f"- {m}\n"
        st.error(msg)
    return missing
