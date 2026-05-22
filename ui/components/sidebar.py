"""
OpenQuant — Sidebar component.

Handles ticker input, validation badges,
and assumption controls.
Returns nothing — writes directly to st.sidebar.
"""

from __future__ import annotations
import streamlit as st
from ui.state import StateKeys, get, set_state, clear_analysis
from config import (
    DEFAULT_RISK_FREE_RATE,
    DEFAULT_MARKET_RISK_PREMIUM,
    DEFAULT_TERMINAL_GROWTH_RATE,
    MAX_TERMINAL_GROWTH_RATE,
)


def render_sidebar() -> None:
    """Render the complete sidebar."""
    with st.sidebar:
        st.markdown("## 📊 OpenQuant")
        st.caption(
            "Transparent educational investment analysis. "
            "Every formula. Real data. Free."
        )
        st.divider()

        _render_ticker_input()
        st.divider()
        _render_assumptions()
        st.divider()
        _render_display_options()
        st.divider()
        _render_data_source_badge()


def _render_ticker_input() -> None:
    """Ticker input with validation badge."""
    st.markdown("**Company**")

    ticker_input = st.text_input(
        "Ticker symbol",
        value=get(StateKeys.TICKER, ""),
        placeholder="e.g. AAPL, MSFT, XOM",
        help="US-listed companies only. International coverage in v2.",
        label_visibility="collapsed",
    ).upper().strip()

    # Detect change
    if ticker_input != get(StateKeys.TICKER, ""):
        set_state(StateKeys.TICKER, ticker_input)
        set_state(StateKeys.TICKER_VALID, False)
        set_state(StateKeys.TICKER_VALIDATION, None)
        clear_analysis()

    validation = get(StateKeys.TICKER_VALIDATION)

    if ticker_input and validation is None:
        # Show validate button
        if st.button("Validate ticker", use_container_width=True):
            with st.spinner(f"Checking {ticker_input}..."):
                try:
                    from core.data import DataFetcher
                    fetcher = DataFetcher()
                    result = fetcher.validate_ticker(ticker_input)
                    set_state(StateKeys.TICKER_VALIDATION, result)
                    set_state(StateKeys.TICKER_VALID, result.is_valid)
                    set_state(StateKeys.DATA_SOURCE, "SEC EDGAR")
                except Exception as e:
                    st.error(f"Validation failed: {e}")

    if validation is not None:
        badge_color = {
            "green": "🟢",
            "amber": "🟡",
            "red": "🔴",
        }.get(validation.badge, "⚪")

        st.caption(f"{badge_color} {validation.message}")

    # US-only note
    st.caption("🇺🇸 US companies only · International in v2")


def _render_assumptions() -> None:
    """Key assumption controls."""
    st.markdown("**Assumptions**")

    rf = st.number_input(
        "Risk-free rate (%)",
        min_value=0.0,
        max_value=15.0,
        value=get(StateKeys.RISK_FREE_RATE, DEFAULT_RISK_FREE_RATE) * 100,
        step=0.1,
        format="%.1f",
        help="10-year US Treasury yield. Default: 4.5%",
    ) / 100
    set_state(StateKeys.RISK_FREE_RATE, rf)

    mrp = st.number_input(
        "Market risk premium (%)",
        min_value=0.0,
        max_value=15.0,
        value=get(StateKeys.MARKET_RISK_PREMIUM, DEFAULT_MARKET_RISK_PREMIUM) * 100,
        step=0.1,
        format="%.1f",
        help="E(Rm) - Rf. Damodaran estimate: 5.5%",
    ) / 100
    set_state(StateKeys.MARKET_RISK_PREMIUM, mrp)

    tg = st.number_input(
        "Terminal growth (%)",
        min_value=0.0,
        max_value=MAX_TERMINAL_GROWTH_RATE * 100,
        value=get(StateKeys.TERMINAL_GROWTH, DEFAULT_TERMINAL_GROWTH_RATE) * 100,
        step=0.1,
        format="%.1f",
        help=f"Long-run nominal GDP growth. Capped at {MAX_TERMINAL_GROWTH_RATE:.0%}.",
    ) / 100
    set_state(StateKeys.TERMINAL_GROWTH, tg)


def _render_display_options() -> None:
    """Display preference toggles."""
    st.markdown("**Display**")

    show_formulas = st.toggle(
        "Show formulas",
        value=get(StateKeys.SHOW_FORMULAS, False),
        help="Show mathematical formulas alongside every calculation.",
    )
    set_state(StateKeys.SHOW_FORMULAS, show_formulas)

    use_ex_sbc = st.toggle(
        "FCF excluding SBC",
        value=get(StateKeys.USE_EX_SBC, False),
        help="Use FCF excluding stock-based compensation as the base for projections.",
    )
    set_state(StateKeys.USE_EX_SBC, use_ex_sbc)


def _render_data_source_badge() -> None:
    """Show which data source was used."""
    source = get(StateKeys.DATA_SOURCE, "Not fetched")
    st.caption(f"📡 Data: {source}")
    st.caption("v1.0.0 · [GitHub](https://github.com/a-bv/openquant)")
