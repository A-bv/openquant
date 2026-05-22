"""
OpenQuant — Portfolio Construction page.
Thin wrapper: calls core/portfolio.py for math, renders results.
"""

import streamlit as st
import plotly.graph_objects as go
import numpy as np

from ui.state import StateKeys, init_state, get, set_state
from ui.components.sidebar import render_sidebar
from config import DEFAULT_RISK_FREE_RATE

st.set_page_config(page_title="OpenQuant — Portfolio", page_icon="📈", layout="wide")
init_state()
render_sidebar()

st.title("📈 Portfolio Construction")
st.caption(
    "Enter tickers and weights to see how your assets combine. "
    "Every formula from the EPFL covariance matrix is computed here."
)

# ── Input ─────────────────────────────────────────────────────────────────────
st.subheader("Your Portfolio")
col1, col2 = st.columns([2, 1])

with col1:
    tickers_input = st.text_input(
        "Tickers (comma-separated)",
        value="AAPL,MSFT,XOM,BND",
        help="US-listed companies. Minimum 2, maximum 10.",
    )

with col2:
    years = st.slider("Price history (years)", 2, 10, 5)

tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]
tickers = tickers[:10]

if len(tickers) < 2:
    st.warning("Enter at least 2 tickers.")
    st.stop()

# ── Weight inputs ──────────────────────────────────────────────────────────────
st.markdown("**Weights** (must sum to 100%)")
weight_cols = st.columns(len(tickers))
weights_raw = {}
for i, (ticker, col) in enumerate(zip(tickers, weight_cols)):
    with col:
        weights_raw[ticker] = st.number_input(
            ticker, min_value=0.0, max_value=100.0,
            value=round(100.0 / len(tickers), 1),
            step=0.5, format="%.1f",
        )

total_weight = sum(weights_raw.values())
if abs(total_weight - 100.0) > 0.5:
    st.warning(f"Weights sum to {total_weight:.1f}% — must be 100%.")
    run_disabled = True
else:
    st.success(f"✅ Weights sum to {total_weight:.1f}%")
    run_disabled = False

weights = {t: w/100.0 for t, w in weights_raw.items()}

if st.button("▶ Analyse Portfolio", type="primary", disabled=run_disabled):
    with st.spinner("Fetching prices and computing portfolio metrics..."):
        try:
            from core.data import DataFetcher
            fetcher = DataFetcher()
            prices = {}
            for ticker in tickers:
                pd_data = fetcher.get_prices(ticker, years=years)
                prices[ticker] = pd_data.prices
            market_data = fetcher.get_prices("^GSPC", years=years)

            from core.portfolio import PortfolioAnalyser
            analyser = PortfolioAnalyser()
            result = analyser.analyse(
                prices, weights,
                risk_free_rate=get(StateKeys.RISK_FREE_RATE, DEFAULT_RISK_FREE_RATE),
                market_returns=market_data.prices,
            )
            set_state(StateKeys.PORTFOLIO_RESULT, result)
            set_state(StateKeys.PORTFOLIO_TICKERS, tickers)

        except Exception as e:
            st.error(f"Portfolio analysis failed: {e}")
            st.stop()

result = get(StateKeys.PORTFOLIO_RESULT)
if result is None:
    st.info("Configure your portfolio above and click Analyse.")
    st.stop()

# ── Results ───────────────────────────────────────────────────────────────────
st.divider()

if result.warnings:
    for w in result.warnings:
        st.caption(f"ℹ️ {w}")

# ── Covariance Matrix ─────────────────────────────────────────────────────────
st.subheader("📐 Covariance Matrix — V = D × C × D'")
st.caption("EPFL formula sheet — annualised daily returns")

col1, col2 = st.columns(2)
with col1:
    st.markdown("**Covariance Matrix (V)**")
    st.dataframe(result.cov_matrix.round(6), use_container_width=True)
with col2:
    st.markdown("**Correlation Matrix (C)**")
    import plotly.express as px
    fig = px.imshow(
        result.corr_matrix.round(3),
        color_continuous_scale="RdBu_r",
        zmin=-1, zmax=1,
        text_auto=".2f",
        title="Correlation Heatmap",
    )
    fig.update_layout(margin=dict(l=0,r=0,t=40,b=0))
    st.plotly_chart(fig, use_container_width=True)

if get(StateKeys.SHOW_FORMULAS, False):
    with st.expander("📐 DCD' Formula", expanded=False):
        st.code(
            "D = diag(σ_1, ..., σ_n)   [diagonal matrix of SDs]\n"
            "C = correlation matrix\n"
            "V = D × C × D'             [covariance matrix]\n"
            "σ²_p = w · V · w'          [portfolio variance]",
            language=None,
        )
        st.caption("Source: EPFL Formula Sheet")

st.divider()

# ── Five Portfolio Comparison ─────────────────────────────────────────────────
st.subheader("📊 Five Portfolio Comparisons")
st.caption(
    "Ordered by robustness — most reliable first. "
    "Max Sharpe is least reliable (sensitive to expected return estimates)."
)

portfolios = [
    ("Current Portfolio", result.current, "Your weights"),
    ("Equal Weight", result.equal_weight, "No estimation needed"),
    ("Inverse-Volatility", result.inverse_vol, "Simple risk parity approx · no expected returns"),
    ("Minimum Variance", result.min_variance, "Uses covariance only · no expected returns · most robust optimized"),
    ("Max Sharpe ⚠", result.max_sharpe, "Sensitive to return estimates · least reliable"),
]

cols = st.columns(5)
for (name, portfolio, note), col in zip(portfolios, cols):
    with col:
        st.markdown(f"**{name}**")
        st.caption(note)
        st.metric("Return", f"{portfolio.expected_return:.1%}")
        st.metric("Volatility", f"{portfolio.volatility:.1%}")
        st.metric("Sharpe", f"{portfolio.sharpe_ratio:.2f}")
        if portfolio.portfolio_beta != 0:
            st.metric("Beta", f"{portfolio.portfolio_beta:.2f}")

        # Weight breakdown
        with st.expander("Weights", expanded=False):
            for ticker, w in sorted(portfolio.weights.items()):
                st.caption(f"{ticker}: {w:.1%}")

st.divider()

# ── Efficient Frontier ────────────────────────────────────────────────────────
st.subheader("🎯 Efficient Frontier")
st.caption(
    "Long-only frontier (w ≥ 0). "
    "Monte Carlo portfolios shown as reference cloud."
)

with st.expander("⚠ Important limitation", expanded=False):
    st.caption(
        "The efficient frontier is sensitive to expected return estimates "
        "computed from historical data. Small input changes produce dramatically "
        "different 'optimal' weights. Equal weighting often performs comparably "
        "out-of-sample. Use minimum variance as the primary robust alternative."
    )

fig = go.Figure()

# Monte Carlo cloud
fig.add_trace(go.Scatter(
    x=result.monte_carlo_vols * 100,
    y=result.monte_carlo_returns * 100,
    mode="markers",
    marker=dict(
        size=3,
        color=result.monte_carlo_sharpes,
        colorscale="Viridis",
        opacity=0.4,
        showscale=True,
        colorbar=dict(title="Sharpe"),
    ),
    name="Random portfolios",
))

# Optimized frontier
if len(result.frontier_vols) > 0:
    fig.add_trace(go.Scatter(
        x=result.frontier_vols * 100,
        y=result.frontier_returns * 100,
        mode="lines",
        line=dict(color="#2563EB", width=2),
        name="Efficient frontier (long-only)",
    ))

# Portfolio markers
markers = [
    (result.current, "Current", "red", "circle"),
    (result.equal_weight, "Equal Weight", "gray", "square"),
    (result.inverse_vol, "Inv-Vol", "orange", "diamond"),
    (result.min_variance, "Min Variance", "#2563EB", "star"),
    (result.max_sharpe, "Max Sharpe", "green", "triangle-up"),
]

for portfolio, label, color, symbol in markers:
    fig.add_trace(go.Scatter(
        x=[portfolio.volatility * 100],
        y=[portfolio.expected_return * 100],
        mode="markers+text",
        marker=dict(size=12, color=color, symbol=symbol),
        text=[label],
        textposition="top center",
        name=label,
    ))

fig.update_layout(
    title="<b>Efficient Frontier — Long-Only</b>",
    xaxis_title="Annualised Volatility (%)",
    yaxis_title="Annualised Return (%)",
    font=dict(family="Inter, sans-serif"),
    plot_bgcolor="white",
    paper_bgcolor="white",
    margin=dict(l=40, r=20, t=60, b=40),
)
st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── Risk Decomposition ────────────────────────────────────────────────────────
if result.current.portfolio_beta != 0:
    st.subheader("⚖️ Risk Decomposition")
    st.caption("Systematic (market) vs idiosyncratic (diversifiable) variance")

    col1, col2 = st.columns(2)
    with col1:
        total_var = result.current.volatility ** 2
        sys_var = result.current.systematic_variance
        idio_var = result.current.idiosyncratic_variance

        sys_pct = sys_var / total_var if total_var > 0 else 0
        idio_pct = idio_var / total_var if total_var > 0 else 0

        st.metric("Portfolio Beta", f"{result.current.portfolio_beta:.3f}")
        st.metric("Systematic Risk", f"{sys_pct:.0%}")
        st.metric("Idiosyncratic Risk", f"{idio_pct:.0%}")

        st.caption(
            f"β²_p × σ²_market = {sys_var:.6f}  "
            f"({sys_pct:.0%} of total variance). "
            "The rest is diversifiable company-specific risk."
        )

    with col2:
        fig = go.Figure(go.Pie(
            labels=["Systematic (Market)", "Idiosyncratic (Diversifiable)"],
            values=[sys_pct * 100, idio_pct * 100],
            marker=dict(colors=["#2563EB", "#EF4444"]),
            textinfo="label+percent",
            hole=0.4,
        ))
        fig.update_layout(
            title="<b>Portfolio Risk Decomposition</b>",
            margin=dict(l=0, r=0, t=40, b=0),
            font=dict(family="Inter, sans-serif"),
        )
        st.plotly_chart(fig, use_container_width=True)

    if get(StateKeys.SHOW_FORMULAS, False):
        with st.expander("📐 Risk Decomposition Formula", expanded=False):
            st.code(
                "Systematic variance = β²_p × σ²_market\n"
                "Idiosyncratic variance = σ²_p − systematic variance\n"
                "β_p = Σ w_i × β_i",
                language=None,
            )
            st.caption("Source: CAPM — EPFL Formula Sheet")
