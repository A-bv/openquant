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
    "implied_positive": "#639922",
    "implied_negative": "#E24B4A",
    "reference_bar": "#B4B2A9",
    "historical_line": "#378ADD",
}


def _base_layout(title: str, subtitle: str = "", height: int = 350) -> dict:
    """Base Plotly layout — transparent background, large fonts, consistent margins."""
    return dict(
        title=dict(
            text=f"<b>{title}</b><br><sup>{subtitle}</sup>" if subtitle else f"<b>{title}</b>",
            x=0.0,
            xanchor="left",
            font=dict(size=15),
        ),
        font=dict(family="Inter, sans-serif", size=14),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=50, r=30, t=80, b=80),
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, font=dict(size=13)),
        height=height,
    )


# ── FCF charts ────────────────────────────────────────────────────────────────

def fcf_history_chart(
    fcf_reported: pd.Series,
    fcf_ex_sbc: pd.Series,
    company_name: str,
) -> go.Figure:
    """Historical FCF bar chart with SBC overlay and trend line."""
    fig = go.Figure()

    years = [str(d.year) for d in fcf_reported.index]
    values_b = fcf_reported.values / 1e9

    # Bug #9: textposition per-bar so negative bars don't push labels below axis
    text_positions = ["outside" if v >= 0 else "inside" for v in values_b]
    fig.add_trace(go.Bar(
        x=years,
        y=values_b,
        name="FCF (reported)",
        marker_color=COLOURS["base"],
        opacity=1.0,
        text=[f"{v:.1f}B" for v in values_b],
        textposition=text_positions,
        textfont=dict(size=13),
        width=0.6,
    ))

    if not fcf_ex_sbc.isna().all():
        ex_sbc_b = fcf_ex_sbc.reindex(fcf_reported.index).values / 1e9
        fig.add_trace(go.Scatter(
            x=years,
            y=ex_sbc_b,
            name="FCF ex-SBC",
            mode="lines+markers",
            line=dict(color=COLOURS["conservative"], dash="dash", width=2),
            marker=dict(size=6),
        ))

    # Linear trend line
    x_idx = np.arange(len(values_b))
    if len(x_idx) >= 2:
        m, b = np.polyfit(x_idx, values_b, 1)
        trend_y = m * x_idx + b
        fig.add_trace(go.Scatter(
            x=years,
            y=trend_y,
            name="Trend",
            mode="lines",
            line=dict(color=COLOURS["current_price"], dash="dash", width=1.5),
            showlegend=True,
        ))

    layout = _base_layout(
        f"{company_name} — Free Cash Flow History",
        "FCF = OCF − CapEx",
        height=300,
    )
    fig.update_layout(**layout)
    fig.update_yaxes(
        title_text="USD Billions",
        title_font=dict(size=13),
        tickfont=dict(size=13),
    )
    fig.update_xaxes(tickfont=dict(size=13))

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

    fig.add_trace(go.Bar(
        x=hist_years,
        y=hist_values,
        name="Historical FCF",
        marker_color=COLOURS["neutral"],
        opacity=0.6,
        textfont=dict(size=13),
    ))

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

    layout = _base_layout(
        f"{company_name} — FCF Projections",
        "10-year forecast  ·  Three scenarios",
    )
    fig.update_layout(**layout)
    fig.update_yaxes(
        title_text="USD Billions",
        title_font=dict(size=13),
        tickfont=dict(size=13),
    )
    fig.update_xaxes(tickfont=dict(size=13))

    return fig


# ── DCF charts ────────────────────────────────────────────────────────────────

def dcf_waterfall_chart(dcf_scenario, company_name: str) -> go.Figure:
    """Waterfall showing PV of FCFs vs PV of terminal value."""
    pv_fcfs = dcf_scenario.pv_fcfs / 1e9
    pv_tv = dcf_scenario.pv_terminal_value / 1e9
    net_debt_val = float(dcf_scenario.net_debt / 1e9)
    equity_val = float(dcf_scenario.equity_value / 1e9)

    # Bug #8: adapt label and direction for net-cash companies (net_debt < 0)
    if net_debt_val < 0:
        debt_label = "Plus: Net Cash"
    else:
        debt_label = "Less: Net Debt"

    bar_values = [float(pv_fcfs.sum()), float(pv_tv), -net_debt_val, 0]
    bar_labels = ["PV of FCFs\n(Yrs 1–10)", "PV of Terminal\nValue", debt_label, "Equity Value"]
    bar_texts = [
        f"${float(pv_fcfs.sum()):.1f}B",
        f"${float(pv_tv):.1f}B",
        f"${abs(net_debt_val):.1f}B",
        f"${equity_val:.1f}B",
    ]

    fig = go.Figure(go.Waterfall(
        name="",
        orientation="v",
        measure=["relative", "relative", "relative", "total"],
        x=bar_labels,
        y=bar_values,
        connector=dict(line=dict(color="#9CA3AF", width=1.5)),
        increasing=dict(marker=dict(color=COLOURS["optimistic"])),
        decreasing=dict(marker=dict(color=COLOURS["conservative"])),
        totals=dict(marker=dict(color=COLOURS["base"])),
        text=bar_texts,
        textposition="outside",
        textfont=dict(size=13),
    ))

    tv_pct = dcf_scenario.terminal_value_pct
    layout = _base_layout(
        f"{company_name} — {dcf_scenario.scenario_name} Scenario",
        f"Terminal value = {tv_pct:.0%} of enterprise value",
        height=350,
    )
    layout["margin"]["b"] = 150
    fig.update_layout(**layout)
    fig.update_yaxes(
        title_text="USD Billions",
        title_font=dict(size=13),
        tickfont=dict(size=13),
    )
    fig.update_xaxes(tickfont=dict(size=13))

    # Terminal value annotation
    fig.add_annotation(
        text=f"Terminal value = {tv_pct:.0%} of total EV",
        xref="paper", yref="paper",
        x=0.98, y=0.97,
        xanchor="right",
        showarrow=False,
        font=dict(size=12, color=COLOURS["terminal_value"]),
        bgcolor="rgba(139,92,246,0.1)",
        bordercolor=COLOURS["terminal_value"],
        borderwidth=1,
        borderpad=4,
    )

    return fig


def sensitivity_heatmap(
    table: pd.DataFrame,
    current_price: float,
    title: str,
    row_label: str,
    col_label: str,
) -> go.Figure:
    """Sensitivity heatmap with highlighted cell closest to current price."""
    values = table.values.astype(float)

    # Format labels as strings for categorical axes (required for index-based shapes).
    # Columns/index may already be strings (e.g. "6.0%") or numeric floats.
    def _to_label(v) -> str:
        try:
            return f"{float(str(v).rstrip('%')) / 100:.0%}"
        except (ValueError, TypeError):
            return str(v)

    x_labels = [_to_label(c) for c in table.columns]
    y_labels = [_to_label(r) for r in table.index]

    fig = go.Figure(go.Heatmap(
        z=values,
        x=x_labels,
        y=y_labels,
        colorscale=[
            [0.0, "#EF4444"],
            [0.4, "#FEF3C7"],
            [0.5, "#FFFFFF"],
            [0.6, "#DCFCE7"],
            [1.0, "#22C55E"],
        ],
        text=[[f"${v:.0f}" for v in row] for row in values],
        texttemplate="%{text}",
        textfont=dict(size=13),
        showscale=True,
        colorbar=dict(title="IV ($)", tickfont=dict(size=12)),
    ))

    # Highlight cell closest to current_price
    diff = np.abs(values - current_price)
    min_row, min_col = np.unravel_index(diff.argmin(), diff.shape)

    # Bug #13: clamp arrow offset so annotation stays inside chart at edge cells
    n_cols = len(x_labels)
    n_rows = len(y_labels)
    ax = -55 if min_col >= n_cols // 2 else 55
    ay = 40 if min_row >= n_rows // 2 else -40

    fig.add_annotation(
        text="Today's price<br>justified here",
        x=x_labels[min_col],
        y=y_labels[min_row],
        xref="x", yref="y",
        showarrow=True,
        arrowhead=2,
        arrowcolor=COLOURS["current_price"],
        ax=ax, ay=ay,
        font=dict(size=12, color=COLOURS["current_price"]),
        bgcolor="rgba(245,158,11,0.15)",
        bordercolor=COLOURS["current_price"],
        borderwidth=2,
        borderpad=3,
    )

    layout = _base_layout(
        title,
        f"{row_label} (rows) × {col_label} (columns) → Implied Share Price",
        height=320,
    )
    fig.update_layout(**layout)
    fig.update_xaxes(
        title_text=col_label,
        title_font=dict(size=13),
        tickfont=dict(size=13),
        tickangle=0,
    )
    fig.update_yaxes(
        title_text=row_label,
        title_font=dict(size=13),
        tickfont=dict(size=13),
    )

    return fig


# ── WACC / Beta charts ────────────────────────────────────────────────────────

def rolling_beta_chart(
    rolling_beta: pd.Series,
    static_beta: float,
    ci_lower: float,
    ci_upper: float,
    ticker: str,
) -> go.Figure:
    """Rolling beta with static beta, CI band, and normal range."""
    clean = rolling_beta.dropna()

    fig = go.Figure()

    # Normal range band (0.8 – 1.2)
    fig.add_hrect(
        y0=0.8, y1=1.2,
        fillcolor="rgba(180,178,169,0.15)",
        line_width=0,
        annotation_text="Normal range (0.8 – 1.2)",
        annotation_position="top left",
        annotation_font=dict(size=12, color=COLOURS["reference_bar"]),
    )

    # CI band
    fig.add_trace(go.Scatter(
        x=list(clean.index) + list(clean.index[::-1]),
        y=[ci_upper] * len(clean) + [ci_lower] * len(clean),
        fill="toself",
        fillcolor="rgba(37, 99, 235, 0.15)",
        line=dict(color="rgba(255,255,255,0)"),
        name=f"95% CI: [{ci_lower:.2f}, {ci_upper:.2f}]",
        showlegend=True,
    ))

    # Rolling beta line
    fig.add_trace(go.Scatter(
        x=clean.index,
        y=clean.values,
        name="Rolling beta (90-day)",
        line=dict(color=COLOURS["base"], width=2),
    ))

    # Static beta line
    fig.add_hline(
        y=static_beta,
        line_dash="dash",
        line_color=COLOURS["primary"],
        annotation_text=f"Current β = {static_beta:.2f}",
        annotation_position="top right",
        annotation_font=dict(size=13),
    )

    # Market reference
    fig.add_hline(
        y=1.0,
        line_dash="dot",
        line_color=COLOURS["neutral"],
        annotation_text="Market β = 1.0",
        annotation_position="bottom left",
        annotation_font=dict(size=12),
    )

    layout = _base_layout(
        f"{ticker} — Rolling Beta",
        "β = Cov(r_stock, r_market) / Var(r_market)",
        height=300,
    )
    fig.update_layout(**layout)
    fig.update_yaxes(
        title_text="Beta",
        title_font=dict(size=13),
        tickfont=dict(size=13),
    )
    fig.update_xaxes(tickfont=dict(size=13))

    return fig


def capital_structure_chart(wacc_result) -> go.Figure:
    """Donut chart of equity vs debt weights with WACC annotation."""
    eq_w = wacc_result.equity_weight
    de_w = wacc_result.debt_weight
    # Pull the smaller slice
    pull = [0.05, 0] if eq_w < de_w else [0, 0.05]

    fig = go.Figure(go.Pie(
        labels=["Equity (E/V)", "Debt (D/V)"],
        values=[eq_w, de_w],
        marker=dict(colors=[COLOURS["base"], COLOURS["conservative"]]),
        textinfo="label+percent",
        hole=0.45,
        pull=pull,
        textfont=dict(size=13),
    ))

    # Bug #12: white text invisible in light mode — use dark text with semi-transparent bg
    fig.add_annotation(
        text=f"WACC<br><b>{wacc_result.wacc:.1%}</b>",
        x=0.5, y=0.5,
        font=dict(size=14, color="#1F2937"),
        showarrow=False,
        bgcolor="rgba(255,255,255,0.85)",
        borderpad=6,
    )

    layout = _base_layout(
        f"{wacc_result.ticker} — Capital Structure",
        "WACC = (E/V)×rE + (D/V)×rD×(1−T)",
    )
    fig.update_layout(**layout)

    return fig


# ── Reverse DCF chart ─────────────────────────────────────────────────────────

def reverse_dcf_comparison_chart(
    implied_growth: float,
    historical_median: float,
    historical_mean: float,
    revenue_cagr: Optional[float],
    gdp_growth: float = 0.03,
    ticker: str = "",
) -> go.Figure:
    """Bar chart comparing implied vs historical growth rates."""
    raw_labels = [
        "Market-Implied<br>FCF Growth",
        "Historical<br>Median FCF",
        "Historical<br>Mean FCF",
        "Revenue<br>CAGR (5yr)",
        "Long-run<br>GDP Growth",
    ]
    raw_values = [
        implied_growth,
        historical_median,
        historical_mean,
        revenue_cagr if revenue_cagr is not None else 0.0,
        gdp_growth,
    ]

    # Colour: implied bar red/green, all others neutral grey
    implied_color = (
        COLOURS["implied_positive"] if implied_growth >= historical_median
        else COLOURS["implied_negative"]
    )
    bar_colors = [implied_color] + [COLOURS["reference_bar"]] * (len(raw_values) - 1)

    pct_values = [v * 100 for v in raw_values]

    fig = go.Figure()
    for i, (label, value, color) in enumerate(zip(raw_labels, pct_values, bar_colors)):
        fig.add_trace(go.Bar(
            x=[label],
            y=[value],
            marker_color=color,
            text=[f"{raw_values[i]:.1%}"],
            textposition="inside" if abs(value) > 3 else "outside",
            textfont=dict(size=13, color="white" if abs(value) > 3 else "#1F2937"),
            width=0.5,
            showlegend=False,
            name=label,
        ))

    # Historical median reference line
    fig.add_hline(
        y=historical_median * 100,
        line_dash="dash",
        line_color=COLOURS["historical_line"],
        line_width=2,
        annotation_text=f"Historical median: {historical_median:.1%}",
        annotation_position="top right",
        annotation_font=dict(size=13, color=COLOURS["historical_line"]),
    )

    # Bug #10: remove redundant "←" — the Plotly arrowhead already points at the bar
    fig.add_annotation(
        x=raw_labels[0],
        y=pct_values[0],
        text="Market is betting this",
        showarrow=True,
        arrowhead=2,
        arrowcolor=implied_color,
        ax=80, ay=-30,
        font=dict(size=13, color=implied_color),
    )

    layout = _base_layout(
        f"{ticker} — What Is The Market Betting On?",
        "The red/green bar is what the market currently expects. All others are historical reference points.",
        height=320,
    )
    fig.update_layout(**layout)
    fig.update_yaxes(
        title_text="Annual Growth Rate (%)",
        title_font=dict(size=13),
        tickfont=dict(size=13),
    )
    fig.update_xaxes(tickfont=dict(size=13))

    return fig


# ── Revenue & FCF sparklines ──────────────────────────────────────────────────

def revenue_fcf_sparklines(
    revenue: pd.Series,
    fcf: pd.Series,
    company_name: str,
) -> go.Figure:
    """Dual-axis chart: revenue bars + FCF line with data labels."""
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    years = [str(d.year) for d in revenue.index]
    fcf_aligned = fcf.reindex(revenue.index)
    fcf_b = fcf_aligned.values / 1e9

    # Bug #11: removed dead textfont — no text= on this Bar trace
    fig.add_trace(go.Bar(
        x=years,
        y=revenue.values / 1e9,
        name="Revenue",
        marker_color="#D1D5DB",
        opacity=1.0,
    ), secondary_y=False)

    fig.add_trace(go.Scatter(
        x=years,
        y=fcf_b,
        name="FCF",
        mode="lines+markers+text",
        line=dict(color=COLOURS["base"], width=3),
        marker=dict(size=8),
        text=[f"{v:.1f}B" for v in fcf_b],
        textposition="top center",
        textfont=dict(size=12),
    ), secondary_y=True)

    layout = _base_layout(
        f"{company_name} — Revenue & FCF",
        height=280,
    )
    fig.update_layout(**layout)
    fig.update_yaxes(
        title_text="Revenue (USD Bn)",
        title_font=dict(size=13),
        tickfont=dict(size=13),
        secondary_y=False,
    )
    fig.update_yaxes(
        title_text="FCF (USD Bn)",
        title_font=dict(size=13),
        tickfont=dict(size=13),
        secondary_y=True,
    )
    fig.update_xaxes(tickfont=dict(size=13))

    return fig
