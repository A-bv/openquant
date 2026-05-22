"""
OpenQuant — Streamlit session state schema.

All session state keys defined in one place.
No magic strings anywhere in the UI layer.

Cache decorators live here too — keeping them
out of core/ (which must stay pure Python).
"""

from __future__ import annotations
from typing import Optional
import streamlit as st


# ── Session state keys ────────────────────────────────────────────────────────

class StateKeys:
    # Ticker input
    TICKER = "ticker"
    CURRENT_PRICE = "current_price"

    # Validation
    TICKER_VALIDATION = "ticker_validation"
    TICKER_VALID = "ticker_valid"

    # Fetched data
    FINANCIAL_STATEMENTS = "financial_statements"
    PRICE_DATA = "price_data"
    DATA_SOURCE = "data_source"

    # Analysis results
    FCF_ANALYSIS = "fcf_analysis"
    WACC_RESULT = "wacc_result"
    BETA_RESULT = "beta_result"
    DCF_RESULT = "dcf_result"
    REVERSE_DCF_RESULT = "reverse_dcf_result"
    SUITABILITY_REPORT = "suitability_report"
    ASSUMPTION_DIAGNOSTIC = "assumption_diagnostic"
    RED_FLAGS = "red_flags"
    MULTIPLES_RESULT = "multiples_result"
    AUDIT_TRAIL = "audit_trail"
    SENSITIVITY_GROWTH_TABLE = "sensitivity_growth_table"
    SENSITIVITY_TV_TABLE = "sensitivity_tv_table"

    # UI preferences
    SHOW_FORMULAS = "show_formulas"
    USE_EX_SBC = "use_ex_sbc"
    RISK_FREE_RATE = "risk_free_rate"
    MARKET_RISK_PREMIUM = "market_risk_premium"
    TERMINAL_GROWTH = "terminal_growth"

    # Portfolio module
    PORTFOLIO_TICKERS = "portfolio_tickers"
    PORTFOLIO_WEIGHTS = "portfolio_weights"
    PORTFOLIO_PRICE_DATA = "portfolio_price_data"
    PORTFOLIO_RESULT = "portfolio_result"


def init_state() -> None:
    """Initialise all session state keys with defaults."""
    defaults = {
        StateKeys.TICKER: "",
        StateKeys.CURRENT_PRICE: 0.0,
        StateKeys.TICKER_VALIDATION: None,
        StateKeys.TICKER_VALID: False,
        StateKeys.FINANCIAL_STATEMENTS: None,
        StateKeys.PRICE_DATA: None,
        StateKeys.DATA_SOURCE: "Not fetched",
        StateKeys.FCF_ANALYSIS: None,
        StateKeys.WACC_RESULT: None,
        StateKeys.BETA_RESULT: None,
        StateKeys.DCF_RESULT: None,
        StateKeys.REVERSE_DCF_RESULT: None,
        StateKeys.SUITABILITY_REPORT: None,
        StateKeys.ASSUMPTION_DIAGNOSTIC: None,
        StateKeys.RED_FLAGS: None,
        StateKeys.MULTIPLES_RESULT: None,
        StateKeys.AUDIT_TRAIL: None,
        StateKeys.SENSITIVITY_GROWTH_TABLE: None,
        StateKeys.SENSITIVITY_TV_TABLE: None,
        StateKeys.SHOW_FORMULAS: False,
        StateKeys.USE_EX_SBC: False,
        StateKeys.RISK_FREE_RATE: 0.045,
        StateKeys.MARKET_RISK_PREMIUM: 0.055,
        StateKeys.TERMINAL_GROWTH: 0.025,
        StateKeys.PORTFOLIO_TICKERS: [],
        StateKeys.PORTFOLIO_WEIGHTS: {},
        StateKeys.PORTFOLIO_PRICE_DATA: None,
        StateKeys.PORTFOLIO_RESULT: None,
    }
    for key, default in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default


def clear_analysis() -> None:
    """Clear all analysis results when ticker changes."""
    analysis_keys = [
        StateKeys.FINANCIAL_STATEMENTS,
        StateKeys.PRICE_DATA,
        StateKeys.FCF_ANALYSIS,
        StateKeys.WACC_RESULT,
        StateKeys.BETA_RESULT,
        StateKeys.DCF_RESULT,
        StateKeys.REVERSE_DCF_RESULT,
        StateKeys.SUITABILITY_REPORT,
        StateKeys.ASSUMPTION_DIAGNOSTIC,
        StateKeys.RED_FLAGS,
        StateKeys.MULTIPLES_RESULT,
        StateKeys.AUDIT_TRAIL,
        StateKeys.SENSITIVITY_GROWTH_TABLE,
        StateKeys.SENSITIVITY_TV_TABLE,
    ]
    for key in analysis_keys:
        st.session_state[key] = None


def get(key: str, default=None):
    """Get session state value with default."""
    return st.session_state.get(key, default)


def set(key: str, value) -> None:
    """Set session state value."""
    st.session_state[key] = value
