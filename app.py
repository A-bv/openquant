"""
OpenQuant — Entry point.
Sidebar configuration and page routing only.
No business logic here.
"""

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="OpenQuant",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Main tagline ──────────────────────────────────────────────────────────────
st.sidebar.markdown("## 📊 OpenQuant")
st.sidebar.caption(
    "OpenQuant does not tell you what a company is worth. "
    "It tells you what assumptions are required for the current price to make sense."
)
st.sidebar.divider()

# ── Formula toggle ────────────────────────────────────────────────────────────
show_formulas = st.sidebar.toggle(
    "Show formulas and technical detail",
    value=False,
    help="Show the mathematical formulas behind every calculation.",
)
st.session_state["show_formulas"] = show_formulas

# ── Navigation ────────────────────────────────────────────────────────────────
st.sidebar.divider()
st.sidebar.caption("Navigate using the pages above ↑")

# ── Home page ─────────────────────────────────────────────────────────────────
st.title("📊 OpenQuant")
st.subheader("Transparent educational investment analysis.")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Module 1 — Company Valuation")
    st.markdown(
        "Is the market's current bet on this company reasonable? "
        "Enter a ticker and walk through a complete professional valuation — "
        "FCF, WACC, CAPM, DCF, reverse DCF — with every formula shown."
    )
    st.page_link("pages/1_Valuation.py", label="Go to Valuation →", icon="🔍")

with col2:
    st.markdown("### Module 2 — Portfolio Construction")
    st.markdown(
        "How do your chosen assets combine? "
        "Enter tickers and weights to see the covariance matrix, "
        "efficient frontier, and five portfolio comparisons in reliability order."
    )
    st.page_link("pages/2_Portfolio.py", label="Go to Portfolio →", icon="📈")

st.divider()
st.caption(
    "Every formula traceable to its source. "
    "Every limitation honestly disclosed. "
    "Free. Open source."
)
