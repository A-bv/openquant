"""
OpenQuant — Plotly chart builders.

All charts return fig objects.
No business logic here — pure presentation.
Every chart has a plain-language title and subtitle.
"""

from __future__ import annotations
from typing import Optional
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots


# ── Colour palette ────────────────────────────────────────────────────────────
COLOURS = {
    "primary": "#2563EB",
    "conservative": "#EF4444",
    "base": "#2563EB",
    "optimistic": "#22C55E",
    "current_price": "#F59E0B",
    "terminal_value": "#8B5CF6",
    "neutral": "#6B7280",
    "background": "#F9FAFB",
}


def _base_layout(title: str, subtitle: str = "") -> dict:
    """Base Plotly layout with consistent styling."""
    return dict(
        title=dict(
            text=f"<b>{title}</b><br><sup>{subtitle}</sup>" if subtitle else f"<b>{title}</b>",
            x=0.0,
            xanchor="left",
        ),
        font=dict(family="Inter, sans-serif", size=13),
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=40, r=20, t=60, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=-0.2),
    )


# ── FCF charts ────────────────────────────────────────────────────────────────

def fcf_history_chart(
    fcf_reported: pd.Series,
    fcf_ex_sbc: pd.Series,
    company_name: str,
) -> go.Figure:
    """Historical FCF bar chart with SBC overlay."""
    fig = go.Figure()

    years = [str(d.year) for d in fcf_reported.index]
    values_b = fcf_reported.values / 1e9

    fig.add_trace(go.Bar(
        x=years,
        y=values_b,
        name="FCF (reported)",
        marker_color=COLOURS["base"],
        opacity=0.8,
    ))

    if not fcf_ex_sbc.isna().all():
        ex_sbc_b = fcf_ex_sbc.values / 1e9
        fig.add_trace(go.Scatter(
            x=years,
            y=ex_sbc_b,
            name="FCF ex-SBC",
            mode="lines+markers",
            line=dict(color=COLOURS["conservative"], dash="dash", width=2),
            marker=dict(size=6),
        ))

    fig.update_layout(**_base_layout(
        f"{company_name} — Free Cash Flow History",
        "FCF = OCF − CapEx  ·  EPFL Exam 1 Formula",
    ))
    fig.update_yaxes(title_text="USD Billions")

    return fig


def fcf_projection_chart(
    historical_fcf: pd.Series,
    scenarios: dict,
    company_name: str,
) -> go.Figure:
    """FCF projection chart — historical + 3 scenarios."""
    fig = go.Figure()

    hist_years = [str(d.year) for d in historical_fcf.index]
    hist_values = historical_fcf.values / 1e9

    # Historical
    fig.add_trace(go.Bar(
        x=hist_years,
        y=hist_values,
        name="Historical FCF",
        marker_color=COLOURS["neutral"],
        opacity=0.6,
    ))

    # Scenarios
    colours = {
        "conservative": COLOURS["conservative"],
        "base": COLOURS["base"],
        "optimistic": COLOURS["optimistic"],
    }

    for name, projection in scenarios.items():
        proj_years = [f"Y+{i}" for i in projection.projected_fcf.index]
        proj_values = projection.projected_fcf.values / 1e9

        fig.add_trace(go.Scatter(
            x=proj_years,
            y=proj_values,
            name=f"{projection.scenario_name} ({projection.growth_rate:.1%}/yr)",
            mode="lines+markers",
            line=dict(color=colours.get(name, COLOURS["neutral"]), width=2),
            marker=dict(size=5),
        ))

    fig.update_layout(**_base_layout(
        f"{company_name} — FCF Projections",
        "10-year forecast  ·  Three scenarios",
    ))
    fig.update_yaxes(title_text="USD Billions")

    return fig


# ── DCF charts ────────────────────────────────────────────────────────────────

def dcf_waterfall_chart(dcf_scenario, company_name: str) -> go.Figure:
    """Waterfall showing PV of FCFs vs PV of terminal value."""
    pv_fcfs = dcf_scenario.pv_fcfs / 1e9
    pv_tv = dcf_scenario.pv_terminal_value / 1e9
    net_debt = dcf_scenario.net_debt / 1e9
    equity = dcf_scenario.equity_value / 1e9

    fig = go.Figure(go.Waterfall(
        name="",
        orientation="v",
        measure=["relative", "relative", "relative", "total"],
        x=["PV of FCFs\n(Years 1-10)", "PV of Terminal\nValue", "Less: Net Debt", "Equity Value"],
        y=[pv_fcfs.sum(), float(pv_tv), -float(net_debt), 0],
        connector=dict(line=dict(color="rgb(63, 63, 63)")),
        increasing=dict(marker=dict(color=COLOURS["optimistic"])),
        decreasing=dict(marker=dict(color=COLOURS["conservative"])),
        totals=dict(marker=dict(color=COLOURS["base"])),
    ))

    tv_pct = dcf_scenario.terminal_value_pct
    fig.update_layout(**_base_layout(
        f"{company_name} — {dcf_scenario.scenario_name} Scenario",
        f"Terminal value = {tv_pct:.0%} of enterprise value",
    ))
    fig.update_yaxes(title_text="USD Billions")

    return fig


def sensitivity_heatmap(
    table: pd.DataFrame,
    current_price: float,
    title: str,
    row_label: str,
    col_label: str,
) -> go.Figure:
    """Sensitivity heatmap with current price annotated."""
    values = table.values.astype(float)

    # Color scale: red (low) → white (near current price) → green (high)
    fig = go.Figure(go.Heatmap(
        z=values,
        x=list(table.columns),
        y=list(table.index),
        colorscale=[
            [0.0, "#EF4444"],
            [0.4, "#FEF3C7"],
            [0.5, "#FFFFFF"],
            [0.6, "#DCFCE7"],
            [1.0, "#22C55E"],
        ],
        text=[[f"${v:.0f}" for v in row] for row in values],
        texttemplate="%{text}",
        textfont=dict(size=11),
        showscale=True,
        colorbar=dict(title="IV ($)"),
    ))

    # Annotate current price line
    fig.add_annotation(
        text=f"Current: ${current_price:.0f}",
        xref="paper", yref="paper",
        x=1.02, y=1.05,
        showarrow=False,
        font=dict(color=COLOURS["current_price"], size=12),
    )

    fig.update_layout(**_base_layout(
        title,
        f"{row_label} (rows) × {col_label} (columns) → Implied Share Price",
    ))
    fig.update_xaxes(title_text=col_label)
    fig.update_yaxes(title_text=row_label)

    return fig


# ── WACC / Beta charts ────────────────────────────────────────────────────────

def rolling_beta_chart(
    rolling_beta: pd.Series,
    static_beta: float,
    ci_lower: float,
    ci_upper: float,
    ticker: str,
) -> go.Figure:
    """Rolling beta with static beta and CI band."""
    clean = rolling_beta.dropna()

    fig = go.Figure()

    # CI band
    fig.add_trace(go.Scatter(
        x=list(clean.index) + list(clean.index[::-1]),
        y=[ci_upper] * len(clean) + [ci_lower] * len(clean),
        fill="toself",
        fillcolor="rgba(37, 99, 235, 0.1)",
        line=dict(color="rgba(255,255,255,0)"),
        name=f"95% CI: [{ci_lower:.2f}, {ci_upper:.2f}]",
        showlegend=True,
    ))

    # Rolling beta
    fig.add_trace(go.Scatter(
        x=clean.index,
        y=clean.values,
        name="Rolling beta (90-day)",
        line=dict(color=COLOURS["base"], width=2),
    ))

    # Static beta
    fig.add_hline(
        y=static_beta,
        line_dash="dash",
        line_color=COLOURS["primary"],
        annotation_text=f"Static β = {static_beta:.3f}",
        annotation_position="right",
    )

    # Market reference
    fig.add_hline(
        y=1.0,
        line_dash="dot",
        line_color=COLOURS["neutral"],
        annotation_text="Market β = 1.0",
        annotation_position="left",
    )

    fig.update_layout(**_base_layout(
        f"{ticker} — Rolling Beta",
        "β = Cov(r_stock, r_market) / Var(r_market)  ·  EPFL Formula Sheet",
    ))
    fig.update_yaxes(title_text="Beta")

    return fig


def capital_structure_chart(wacc_result) -> go.Figure:
    """Pie chart of equity vs debt weights."""
    fig = go.Figure(go.Pie(
        labels=["Equity (E/V)", "Debt (D/V)"],
        values=[wacc_result.equity_weight, wacc_result.debt_weight],
        marker=dict(colors=[COLOURS["base"], COLOURS["conservative"]]),
        textinfo="label+percent",
        hole=0.4,
    ))

    fig.add_annotation(
        text=f"WACC<br>{wacc_result.wacc:.1%}",
        x=0.5, y=0.5,
        font=dict(size=14, color="black"),
        showarrow=False,
    )

    fig.update_layout(**_base_layout(
        f"{wacc_result.ticker} — Capital Structure",
        "WACC = (E/V)×rE + (D/V)×rD×(1−T)  ·  EPFL Formula Sheet",
    ))

    return fig


# ── Reverse DCF chart ─────────────────────────────────────────────────────────

def reverse_dcf_comparison_chart(
    implied_growth: float,
    historical_median: float,
    historical_mean: float,
    revenue_cagr: float,
    gdp_growth: float = 0.03,
    ticker: str = "",
) -> go.Figure:
    """Bar chart comparing implied vs historical growth rates."""
    labels = [
        "Market-Implied<br>FCF Growth",
        "Historical<br>Median FCF",
        "Historical<br>Mean FCF",
        "Revenue<br>CAGR (5yr)",
        "Long-run<br>GDP Growth",
    ]
    values = [
        implied_growth,
        historical_median,
        historical_mean,
        revenue_cagr,
        gdp_growth,
    ]
    colours_list = [
        COLOURS["current_price"],
        COLOURS["base"],
        COLOURS["neutral"],
        COLOURS["optimistic"],
        COLOURS["conservative"],
    ]

    fig = go.Figure(go.Bar(
        x=labels,
        y=[v * 100 for v in values],
        marker_color=colours_list,
        text=[f"{v:.1%}" for v in values],
        textposition="outside",
    ))

    fig.add_hline(
        y=gdp_growth * 100,
        line_dash="dot",
        line_color=COLOURS["neutral"],
        annotation_text="Long-run GDP",
    )

    fig.update_layout(**_base_layout(
        f"{ticker} — What Is The Market Betting On?",
        "Market-implied FCF growth vs historical benchmarks",
    ))
    fig.update_yaxes(title_text="Annual Growth Rate (%)")

    return fig


# ── FCF history sparkline ─────────────────────────────────────────────────────

def revenue_fcf_sparklines(
    revenue: pd.Series,
    fcf: pd.Series,
    company_name: str,
) -> go.Figure:
    """Dual-axis sparkline: revenue and FCF history."""
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    years = [str(d.year) for d in revenue.index]

    fig.add_trace(go.Bar(
        x=years,
        y=revenue.values / 1e9,
        name="Revenue",
        marker_color=COLOURS["neutral"],
        opacity=0.5,
    ), secondary_y=False)

    fig.add_trace(go.Scatter(
        x=years,
        y=fcf.values / 1e9,
        name="FCF",
        mode="lines+markers",
        line=dict(color=COLOURS["base"], width=2),
        marker=dict(size=6),
    ), secondary_y=True)

    fig.update_layout(**_base_layout(f"{company_name} — Revenue & FCF"))
    fig.update_yaxes(title_text="Revenue (USD Bn)", secondary_y=False)
    fig.update_yaxes(title_text="FCF (USD Bn)", secondary_y=True)

    return fig
