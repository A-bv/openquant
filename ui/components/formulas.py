"""
OpenQuant — Formula display panels.
Expandable formula panels shown when formulas toggle is ON.
"""
from __future__ import annotations
import streamlit as st
from ui.state import get, StateKeys


def formula_panel(
    name: str,
    formula: str,
    source: str,
    description: str = "",
) -> None:
    """Show formula panel if formulas are enabled."""
    if not get(StateKeys.SHOW_FORMULAS, False):
        return
    with st.expander(f"📐 Formula: {name}", expanded=False):
        st.code(formula, language=None)
        st.caption(f"**Source:** {source}")
        if description:
            st.caption(description)


def capm_formula_panel(rf: float, beta: float, mrp: float, cost_equity: float) -> None:
    formula_panel(
        "Cost of Equity (CAPM)",
        f"r_E = r_f + β × (r_m − r_f)\n"
        f"    = {rf:.2%} + {beta:.3f} × {mrp:.2%}\n"
        f"    = {cost_equity:.2%}",
        "EPFL Formula Sheet — CAPM",
        "The required return on equity given the company's market risk.",
    )


def wacc_formula_panel(eq_w: float, re: float, dw: float, rd: float, t: float, wacc: float) -> None:
    formula_panel(
        "WACC",
        f"WACC = (E/V) × r_E + (D/V) × r_D × (1 − T)\n"
        f"     = {eq_w:.1%} × {re:.1%} + {dw:.1%} × {rd:.1%} × (1 − {t:.1%})\n"
        f"     = {wacc:.2%}",
        "EPFL Formula Sheet",
        "Weighted average cost of capital — the minimum return the firm must earn.",
    )


def terminal_value_formula_panel(fcf_n: float, g: float, wacc: float, tv: float) -> None:
    formula_panel(
        "Terminal Value",
        f"TV = FCF_n × (1 + g) / (WACC − g)\n"
        f"   = {fcf_n/1e9:.2f}B × (1 + {g:.2%}) / ({wacc:.2%} − {g:.2%})\n"
        f"   = ${tv/1e9:.1f}B",
        "EPFL Formula Sheet — Growing Perpetuity",
        "Requires WACC > g (enforced). Captures value beyond forecast horizon.",
    )
