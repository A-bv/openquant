"""
OpenQuant — Metric card builders.

Renders key metrics as clean cards with
optional formula panels beneath.
"""

from __future__ import annotations
from typing import Optional
import streamlit as st
from ui.state import get, StateKeys


def metric_card(
    label: str,
    value: str,
    delta: Optional[str] = None,
    formula: Optional[str] = None,
    source: Optional[str] = None,
    help_text: Optional[str] = None,
) -> None:
    """
    Render a metric with optional formula panel.

    Args:
        label: Metric name.
        value: Formatted value string.
        delta: Optional change indicator.
        formula: LaTeX-style formula string (shown if formulas enabled).
        source: Formula source (e.g. "EPFL Formula Sheet").
        help_text: Tooltip text.
    """
    st.metric(label=label, value=value, delta=delta, help=help_text)

    if formula and get(StateKeys.SHOW_FORMULAS, False):
        with st.expander("Formula", expanded=False):
            st.code(formula, language=None)
            if source:
                st.caption(f"Source: {source}")


def render_dcf_metrics(dcf_result) -> None:
    """Render three-scenario IV cards."""
    col1, col2, col3 = st.columns(3)

    with col1:
        metric_card(
            label="Conservative IV",
            value=f"${dcf_result.conservative.intrinsic_value_per_share:.2f}",
            delta=f"{dcf_result.conservative.upside_downside:+.1%}",
            formula="IV = (EV − Net Debt) / Shares\nEV = Σ FCF_t/(1+WACC)^t + TV/(1+WACC)^n",
            source="EPFL Formula Sheet — NPV",
            help_text="Intrinsic value per share assuming FCF grows at 70% of the historical median — the pessimistic scenario. Computed by discounting projected cash flows back to today's money.",
        )

    with col2:
        metric_card(
            label="Base IV",
            value=f"${dcf_result.base.intrinsic_value_per_share:.2f}",
            delta=f"{dcf_result.base.upside_downside:+.1%}",
            help_text="Intrinsic value per share assuming FCF continues growing at its historical median rate — the central scenario.",
        )

    with col3:
        metric_card(
            label="Optimistic IV",
            value=f"${dcf_result.optimistic.intrinsic_value_per_share:.2f}",
            delta=f"{dcf_result.optimistic.upside_downside:+.1%}",
            help_text="Intrinsic value per share assuming FCF grows at 130% of the historical median rate — the optimistic scenario.",
        )


def render_wacc_metrics(wacc_result) -> None:
    """Render WACC component cards."""
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        metric_card(
            label="Beta",
            value=f"{wacc_result.beta:.3f}",
            formula="β = Cov(r_stock, r_market) / Var(r_market)",
            source="EPFL Formula Sheet",
            help_text="Measures how much this stock moves relative to the market. Beta of 1.2 means the stock moves 20% more than the S&P 500. Used to estimate the return equity investors require.",
        )

    with col2:
        metric_card(
            label="Cost of Equity",
            value=f"{wacc_result.cost_of_equity:.1%}",
            formula=f"r_E = r_f + β × MRP\n= {wacc_result.risk_free_rate:.1%} + {wacc_result.beta:.2f} × {wacc_result.market_risk_premium:.1%}",
            source="EPFL Formula Sheet — CAPM",
            help_text="The return equity investors require from this company, computed using CAPM: Risk-free rate + Beta x Market Risk Premium. This is what shareholders demand for bearing the company's risk.",
        )

    with col3:
        metric_card(
            label="Cost of Debt",
            value=f"{wacc_result.cost_of_debt_pretax:.1%}",
            help_text="The effective interest rate on the company's debt, estimated as interest expense divided by average debt. Cheaper than equity because debt holders get paid first in bankruptcy.",
        )

    with col4:
        metric_card(
            label="WACC",
            value=f"{wacc_result.wacc:.1%}",
            formula="WACC = (E/V)×rE + (D/V)×rD×(1−T)",
            source="EPFL Formula Sheet",
            help_text="Weighted Average Cost of Capital — the minimum annual return the business must generate to satisfy both its shareholders and lenders. Used to discount future cash flows back to today's value.",
        )


def render_reverse_dcf_metrics(reverse_result) -> None:
    """Render reverse DCF primary output."""
    from core.reverse_dcf import ReverseDCFResult

    if not isinstance(reverse_result, ReverseDCFResult):
        st.warning("Reverse DCF could not be computed.")
        return

    col1, col2, col3 = st.columns(3)

    with col1:
        metric_card(
            label="Market-Implied Growth",
            value=f"{reverse_result.implied_growth_rate:.1%}",
            formula="Solve: IV(g*) = Current Price\nIV(g) = [Σ FCF_t(g)/(1+WACC)^t + TV(g)] / Shares − Net Debt",
            source="Reverse DCF",
            help_text="The annual FCF growth rate that mathematically justifies today's stock price, found by reverse-solving the DCF equation. This is what the market is currently betting on.",
        )

    with col2:
        metric_card(
            label="Historical Median Growth",
            value=f"{reverse_result.historical_median_growth:.1%}",
            help_text="The median year-over-year FCF growth rate over the past 5-10 years, adjusted to remove statistical outliers. This is the company's track record.",
        )

    with col3:
        diff = reverse_result.growth_vs_history
        metric_card(
            label="Implied vs Historical",
            value=f"{diff:+.1%}",
            delta="above historical" if diff > 0 else "below historical",
            help_text="How the market's implied growth expectation compares to what the company has historically delivered. A large positive gap means the market expects the company to significantly outperform its history.",
        )
