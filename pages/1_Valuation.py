"""
OpenQuant — Company Valuation page.

Thin wrapper: calls core/ for math, calls ui/ for display.
No business logic here.

Flow:
  Sidebar input → validate → fetch → analyse → display
"""

import streamlit as st

from ui.state import StateKeys, init_state, get, set_state, clear_analysis
from ui.components.sidebar import render_sidebar
from ui.components.metrics import (
    render_dcf_metrics,
    render_wacc_metrics,
    render_reverse_dcf_metrics,
)
from ui.components.charts import (
    fcf_history_chart,
    fcf_projection_chart,
    dcf_waterfall_chart,
    sensitivity_heatmap,
    rolling_beta_chart,
    capital_structure_chart,
    reverse_dcf_comparison_chart,
    revenue_fcf_sparklines,
)
from ui.components.diagnostic import render_diagnostic
from ui.components.red_flags import render_red_flags
from ui.components.audit_trail import render_audit_trail
from ui.components.formulas import (
    capm_formula_panel,
    wacc_formula_panel,
    terminal_value_formula_panel,
)

st.set_page_config(
    page_title="OpenQuant — Valuation",
    page_icon="🔍",
    layout="wide",
)

init_state()
render_sidebar()

# ── Page header ───────────────────────────────────────────────────────────────
st.title("🔍 Company Valuation")
st.caption(
    "OpenQuant does not tell you what a company is worth. "
    "It tells you what assumptions are required for the current price to make sense."
)
st.caption(
    "OpenQuant uses Discounted Cash Flow (DCF) analysis — a method that estimates what a business "
    "is worth based on the cash it will generate in the future, adjusted for the time value of money and risk."
)

ticker = get(StateKeys.TICKER, "")
is_valid = get(StateKeys.TICKER_VALID, False)

if not ticker:
    st.info("👈 Enter a ticker symbol in the sidebar to begin.")
    st.stop()

if not is_valid:
    st.warning(f"Validate '{ticker}' in the sidebar before running analysis.")
    st.stop()

# ── Run analysis button ───────────────────────────────────────────────────────
col_run, col_price = st.columns([2, 1])

with col_price:
    current_price = st.number_input(
        "Current share price ($)",
        min_value=0.01,
        value=float(get(StateKeys.CURRENT_PRICE, 100.0) or 100.0),
        step=0.01,
        format="%.2f",
    )
    set_state(StateKeys.CURRENT_PRICE, current_price)

with col_run:
    run_analysis = st.button(
        f"▶ Run Analysis — {ticker}",
        type="primary",
        use_container_width=True,
    )

# ── Run full analysis pipeline ────────────────────────────────────────────────
if run_analysis or get(StateKeys.DCF_RESULT) is not None:

    if run_analysis:
        clear_analysis()

        rf = get(StateKeys.RISK_FREE_RATE, 0.045)
        mrp = get(StateKeys.MARKET_RISK_PREMIUM, 0.055)
        tg = get(StateKeys.TERMINAL_GROWTH, 0.025)
        use_ex_sbc = get(StateKeys.USE_EX_SBC, False)

        progress = st.progress(0, text="Fetching financial data...")

        try:
            # Step 1 — Fetch data
            from core.data import DataFetcher
            fetcher = DataFetcher()
            statements = fetcher.get_financial_statements(ticker)
            price_data = fetcher.get_prices(ticker)
            set_state(StateKeys.FINANCIAL_STATEMENTS, statements)
            set_state(StateKeys.PRICE_DATA, price_data)
            set_state(StateKeys.DATA_SOURCE, f"SEC EDGAR · {statements.fetched_at.strftime('%Y-%m-%d')}")
            progress.progress(20, text="Running suitability check...")

            # Step 2 — Suitability
            from core.suitability import SuitabilityChecker
            checker = SuitabilityChecker()
            suit = checker.check(
                statements,
                trading_days=len(price_data.prices),
                sector=get(StateKeys.TICKER_VALIDATION).sector,
            )
            set_state(StateKeys.SUITABILITY_REPORT, suit)
            progress.progress(35, text="Computing WACC...")

            # Step 3 — FCF analysis
            from core.fcf import FCFAnalyser
            fcf_a = FCFAnalyser().analyse(statements)
            set_state(StateKeys.FCF_ANALYSIS, fcf_a)

            # Step 4 — Beta + WACC
            from core.wacc import BetaEstimator, WACCBuilder
            estimator = BetaEstimator()
            beta_r = estimator.estimate(price_data, statements)
            set_state(StateKeys.BETA_RESULT, beta_r)

            builder = WACCBuilder()
            wacc_r = builder.compute_wacc(
                statements, price_data, current_price,
                risk_free_rate=rf,
                market_risk_premium=mrp,
            )
            set_state(StateKeys.WACC_RESULT, wacc_r)
            progress.progress(55, text="Running DCF...")

            # Step 5 — Suitability recheck with WACC
            suit = checker.check(
                statements,
                trading_days=len(price_data.prices),
                sector=get(StateKeys.TICKER_VALIDATION).sector,
                wacc_estimate=wacc_r.wacc,
                terminal_growth=tg,
            )
            set_state(StateKeys.SUITABILITY_REPORT, suit)

            if not suit.is_suitable:
                progress.empty()
                st.stop()

            # Step 6 — Forward DCF
            from core.dcf import DCFEngine
            _debt_s  = statements.total_debt.dropna()
            _cash_s  = statements.cash_and_equivalents.dropna()
            _shares_s = statements.shares_outstanding.dropna()
            if _shares_s.empty:
                raise ValueError(
                    f"No shares outstanding data found in EDGAR for {ticker}. "
                    "Cannot compute per-share intrinsic value."
                )
            net_debt = (
                (_debt_s.iloc[-1] if not _debt_s.empty else 0.0)
                - (_cash_s.iloc[-1] if not _cash_s.empty else 0.0)
            )
            shares = _shares_s.iloc[-1]

            dcf_r = DCFEngine().value(
                fcf_analysis=fcf_a,
                wacc_result=wacc_r,
                current_price=current_price,
                shares_outstanding=shares,
                net_debt=net_debt,
                terminal_growth_rate=tg,
                use_ex_sbc=use_ex_sbc,
            )
            set_state(StateKeys.DCF_RESULT, dcf_r)
            progress.progress(70, text="Running reverse DCF...")

            # Step 7 — Reverse DCF
            from core.reverse_dcf import ReverseDCFSolver
            rev_r = ReverseDCFSolver().solve(
                fcf_analysis=fcf_a,
                wacc_result=wacc_r,
                current_price=current_price,
                shares_outstanding=shares,
                net_debt=net_debt,
                terminal_growth_rate=tg,
            )
            set_state(StateKeys.REVERSE_DCF_RESULT, rev_r)
            progress.progress(80, text="Building diagnostic...")

            # Step 8 — Sensitivity
            from core.sensitivity import SensitivityAnalyser
            sa = SensitivityAnalyser()
            gt = sa.build_growth_wacc_table(fcf_a, wacc_r, current_price, shares, net_debt, tg)
            tt = sa.build_terminal_growth_table(fcf_a, wacc_r, current_price, shares, net_debt, fcf_a.growth_base, n_steps=5)
            set_state(StateKeys.SENSITIVITY_GROWTH_TABLE, gt)
            set_state(StateKeys.SENSITIVITY_TV_TABLE, tt)

            # Step 9 — Diagnostic + Red flags
            from core.assumption_diagnostic import DiagnosticBuilder
            diag = DiagnosticBuilder().build(statements, dcf_r, beta_r, rev_r)
            set_state(StateKeys.ASSUMPTION_DIAGNOSTIC, diag)

            from core.red_flags import RedFlagBuilder
            rf_summary = RedFlagBuilder().build(ticker, diag, suit, dcf_r, rev_r)
            set_state(StateKeys.RED_FLAGS, rf_summary)

            # Step 10 — Multiples + Audit
            from core.multiples import MultiplesAnalyser
            _cash_s2 = statements.cash_and_equivalents.dropna()
            _debt_s2 = statements.total_debt.dropna()
            cash = float(_cash_s2.iloc[-1]) if not _cash_s2.empty else 0.0
            debt_for_mult = float(_debt_s2.iloc[-1]) if not _debt_s2.empty else 0.0
            mult = MultiplesAnalyser().compute(statements, current_price, debt_for_mult, cash, dcf_r)
            set_state(StateKeys.MULTIPLES_RESULT, mult)

            from core.audit_trail import AuditTrailBuilder
            trail = AuditTrailBuilder().build(statements, fcf_a, wacc_r, dcf_r, suit, diag, rev_r, tg)
            set_state(StateKeys.AUDIT_TRAIL, trail)

            progress.progress(100, text="Done.")
            progress.empty()

        except Exception as e:
            progress.empty()
            st.error(f"Analysis failed: {e}")
            st.exception(e)
            st.stop()

    # ── Display results ───────────────────────────────────────────────────────

    statements = get(StateKeys.FINANCIAL_STATEMENTS)
    dcf_r = get(StateKeys.DCF_RESULT)
    wacc_r = get(StateKeys.WACC_RESULT)
    beta_r = get(StateKeys.BETA_RESULT)
    fcf_a = get(StateKeys.FCF_ANALYSIS)
    rev_r = get(StateKeys.REVERSE_DCF_RESULT)
    suit = get(StateKeys.SUITABILITY_REPORT)
    diag = get(StateKeys.ASSUMPTION_DIAGNOSTIC)
    rf_summary = get(StateKeys.RED_FLAGS)
    mult = get(StateKeys.MULTIPLES_RESULT)
    trail = get(StateKeys.AUDIT_TRAIL)
    gt = get(StateKeys.SENSITIVITY_GROWTH_TABLE)
    tt = get(StateKeys.SENSITIVITY_TV_TABLE)

    if not all([statements, dcf_r, wacc_r]):
        st.info("Run analysis to see results.")
        st.stop()

    company_name = statements.company_name
    validation = get(StateKeys.TICKER_VALIDATION)
    sector = validation.sector if validation and hasattr(validation, "sector") else ""

    from core.reverse_dcf import ReverseDCFFailure
    rev_failed = isinstance(rev_r, ReverseDCFFailure)

    # ─────────────────────────────────────────────────────────────────────────
    # SECTION 1 — What is this company?
    # ─────────────────────────────────────────────────────────────────────────
    sector_label = f" · {sector}" if sector else ""
    st.header(f"1. What is {company_name}?")
    st.caption(f"**{company_name}** ({ticker}){sector_label}")

    rev_series = statements.revenue.dropna()
    fcf_series = statements.free_cash_flow.dropna()
    latest_rev = rev_series.iloc[-1] if not rev_series.empty else None
    latest_fcf = fcf_series.iloc[-1] if not fcf_series.empty else None

    _shares_s = statements.shares_outstanding.dropna()
    market_cap = current_price * _shares_s.iloc[-1] if not _shares_s.empty else None

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Current Price", f"${current_price:.2f}")
    with col2:
        if market_cap:
            st.metric("Market Cap", f"${market_cap/1e9:.0f}B")
    with col3:
        if latest_rev:
            st.metric("Revenue (latest yr)", f"${latest_rev/1e9:.1f}B")
    with col4:
        if latest_fcf:
            st.metric("Free Cash Flow (latest yr)", f"${latest_fcf/1e9:.1f}B")

    if fcf_a and latest_fcf is not None:
        g = fcf_a.median_growth_rate
        trend = "growing" if g > 0.05 else "roughly flat" if g > -0.05 else "declining"
        st.caption(
            f"{company_name} converts revenue into **${latest_fcf/1e9:.1f}B** of free cash flow per year, "
            f"with {trend} FCF at a median rate of **{g:.1%}** per year over the past five years."
        )

    st.divider()

    # ─────────────────────────────────────────────────────────────────────────
    # SECTION 2 — Can we value this with DCF?
    # ─────────────────────────────────────────────────────────────────────────
    st.header("2. Can we value this with DCF?")

    if suit:
        badge = {"green": "🟢", "amber": "🟡", "red": "🔴"}.get(suit.overall_rating.value, "⚪")
        st.markdown(f"### {badge} {suit.recommendation}")

        if not suit.is_suitable:
            if suit.alternative_methods:
                st.markdown("**Consider instead:**")
                for alt in suit.alternative_methods:
                    st.caption(f"• {alt}")
            st.stop()

        if suit.alternative_methods:
            with st.expander("What to watch for (amber flags)", expanded=False):
                for alt in suit.alternative_methods:
                    st.caption(f"• {alt}")

    st.divider()

    # ─────────────────────────────────────────────────────────────────────────
    # SECTION 3 — What is the market betting on? (HERO)
    # ─────────────────────────────────────────────────────────────────────────
    st.header("3. What is the market betting on?")

    if rev_r:
        if rev_failed:
            st.warning(f"**{rev_r.reason}**")
            st.caption(rev_r.diagnostic)
            st.info(f"Tip: {rev_r.suggestion}")
        else:
            st.markdown(
                f"To justify today's price of **${current_price:.2f}**, the market is implying "
                f"that **{company_name}** will grow free cash flow at:"
            )

            col_hero, col_chart = st.columns([1, 2])
            with col_hero:
                delta_vs_hist = rev_r.implied_growth_rate - rev_r.historical_median_growth
                st.metric(
                    "Implied FCF Growth Rate",
                    f"{rev_r.implied_growth_rate:.1%}",
                    delta=f"{delta_vs_hist:+.1%} vs historical median",
                    delta_color="inverse",
                )
                st.caption(f"Historical median: **{rev_r.historical_median_growth:.1%}**")
                st.caption(f"Historical mean: **{rev_r.historical_mean_growth:.1%}**")
                if rev_r.revenue_cagr:
                    st.caption(f"Revenue CAGR: **{rev_r.revenue_cagr:.1%}**")

            with col_chart:
                fig = reverse_dcf_comparison_chart(
                    rev_r.implied_growth_rate,
                    rev_r.historical_median_growth,
                    rev_r.historical_mean_growth,
                    rev_r.revenue_cagr,
                    ticker=ticker,
                )
                st.plotly_chart(fig, use_container_width=True)

            st.markdown(f"**What this means:** {rev_r.verdict}")

    st.divider()

    # ─────────────────────────────────────────────────────────────────────────
    # SECTION 4 — What does the math say?
    # ─────────────────────────────────────────────────────────────────────────
    st.header("4. What does the math say?")

    if dcf_r and fcf_a:
        if rev_r and not rev_failed:
            st.markdown(
                f"The market requires **{rev_r.implied_growth_rate:.1%}** annual FCF growth from "
                f"{company_name}. Historically it delivered **{rev_r.historical_median_growth:.1%}** "
                f"(median). Here is what three scenarios imply for fair value:"
            )
        else:
            st.markdown(
                f"Based on {company_name}'s FCF history, here are three scenarios for fair value:"
            )

        render_dcf_metrics(dcf_r)

        tabs = st.tabs(["Conservative", "Base", "Optimistic"])
        for tab, scenario in zip(tabs, dcf_r.all_scenarios):
            with tab:
                col1, col2 = st.columns([2, 1])
                with col1:
                    fig = dcf_waterfall_chart(scenario, company_name)
                    st.plotly_chart(fig, use_container_width=True)
                with col2:
                    st.metric("Intrinsic Value", f"${scenario.intrinsic_value_per_share:.2f}")
                    st.metric("Current Price", f"${current_price:.2f}")
                    mos = scenario.margin_of_safety
                    mos_sign = "undervalued" if mos > 0 else "overvalued"
                    st.metric(
                        "Margin of Safety" if mos > 0 else "Premium to Fair Value",
                        f"{abs(mos):.1%}",
                        delta=mos_sign,
                        delta_color="normal" if mos > 0 else "inverse",
                    )
                    st.metric("FCF Growth Assumed", f"{scenario.growth_rate:.1%}")
                    st.metric("WACC Used", f"{scenario.wacc:.1%}")

    st.divider()

    # ─────────────────────────────────────────────────────────────────────────
    # SECTION 5 — How sensitive is this?
    # ─────────────────────────────────────────────────────────────────────────
    st.header("5. How sensitive is this?")

    if gt:
        if fcf_a and wacc_r:
            from core.sensitivity import SensitivityAnalyser
            plain = SensitivityAnalyser().generate_plain_language(
                gt, current_price, fcf_a.growth_base, wacc_r.wacc, fcf_a.median_growth_rate
            )
            st.caption(plain)

        st.caption(
            "The highlighted cell shows the growth rate and WACC combination closest to today's price."
        )

        fig = sensitivity_heatmap(
            gt.table, current_price,
            "Implied Share Price",
            "FCF Growth Rate", "WACC",
        )
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ─────────────────────────────────────────────────────────────────────────
    # SECTION 6 — How was this computed? (collapsed by default)
    # ─────────────────────────────────────────────────────────────────────────
    st.header("6. How was this computed?")
    st.caption("All technical detail is here — expand any section to go deeper.")

    with st.expander("⚖️ WACC — Cost of Capital", expanded=False):
        if wacc_r:
            render_wacc_metrics(wacc_r)
            capm_formula_panel(
                wacc_r.risk_free_rate, wacc_r.beta,
                wacc_r.market_risk_premium, wacc_r.cost_of_equity,
            )
            wacc_formula_panel(
                wacc_r.equity_weight, wacc_r.cost_of_equity,
                wacc_r.debt_weight, wacc_r.cost_of_debt_pretax,
                wacc_r.tax_rate, wacc_r.wacc,
            )

    with st.expander("📈 Beta — Market Sensitivity", expanded=False):
        if beta_r and wacc_r:
            col1, col2 = st.columns(2)
            with col1:
                fig = rolling_beta_chart(
                    beta_r.rolling_beta,
                    beta_r.beta,
                    beta_r.beta_ci_lower,
                    beta_r.beta_ci_upper,
                    ticker,
                )
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                fig = capital_structure_chart(wacc_r)
                st.plotly_chart(fig, use_container_width=True)
            st.caption(beta_r.stability_note)
            st.caption(wacc_r.formula_trace)

    with st.expander("💵 FCF History & Projections", expanded=False):
        if fcf_a and statements:
            tab1, tab2 = st.tabs(["History", "Projections"])
            with tab1:
                fig = fcf_history_chart(
                    statements.free_cash_flow.dropna(),
                    statements.free_cash_flow.dropna()
                    - statements.stock_based_compensation.dropna().fillna(0),
                    company_name,
                )
                st.plotly_chart(fig, use_container_width=True)
            with tab2:
                from core.fcf import FCFAnalyser
                scenarios = FCFAnalyser().project_all_scenarios(fcf_a)
                fig = fcf_projection_chart(
                    statements.free_cash_flow.dropna(),
                    scenarios,
                    company_name,
                )
                st.plotly_chart(fig, use_container_width=True)

    with st.expander("📊 Revenue & FCF Overview", expanded=False):
        if not rev_series.empty:
            fig = revenue_fcf_sparklines(rev_series, fcf_series, company_name)
            st.plotly_chart(fig, use_container_width=True)

    with st.expander("📐 Terminal Value Formula", expanded=False):
        if dcf_r and wacc_r:
            terminal_value_formula_panel(
                dcf_r.base.terminal_fcf,
                dcf_r.terminal_growth_rate,
                wacc_r.wacc,
                dcf_r.base.terminal_value,
            )

    with st.expander("📋 Assumption Diagnostic", expanded=False):
        if diag:
            render_diagnostic(diag)

    if rf_summary:
        with st.expander("🚩 Red Flags", expanded=False):
            render_red_flags(rf_summary)

    if mult:
        with st.expander("📊 Market Multiples Context", expanded=False):
            st.caption("Not a primary valuation — context alongside DCF only.")
            col1, col2, col3 = st.columns(3)
            with col1:
                if mult.ev_ebitda:
                    st.metric("EV/EBITDA", f"{mult.ev_ebitda:.1f}x")
            with col2:
                if mult.fcf_yield:
                    st.metric("FCF Yield", f"{mult.fcf_yield:.1%}")
            with col3:
                if mult.pe_ratio:
                    st.metric("P/E Ratio", f"{mult.pe_ratio:.1f}x")
            st.caption(mult.interpretation)

    if trail:
        render_audit_trail(trail)

    # ─────────────────────────────────────────────────────────────────────────
    # LAYER 3 — Glossary (collapsed, on demand)
    # ─────────────────────────────────────────────────────────────────────────
    st.divider()
    with st.expander("📖 Key concepts — what do these terms mean?", expanded=False):
        st.caption("For anyone who hasn't taken a finance course — every term used on this page, explained in plain English.")
        st.markdown("""
| **Term** | **Plain English** |
|---|---|
| **Free Cash Flow (FCF)** | The actual cash a business generates after paying all its operating costs and investments. Unlike profit, it cannot be manipulated by accounting choices. |
| **WACC** | Weighted Average Cost of Capital — the minimum annual return the business must generate to satisfy both its shareholders and lenders. |
| **DCF Valuation** | Discounted Cash Flow — a method that estimates what future cash flows are worth in today's money, by applying a discount rate. |
| **Reverse DCF** | Instead of asking "what is this worth?", we ask "what growth rate is already baked into the current price?" More honest than predicting the future. |
| **Beta** | A measure of how much a stock moves relative to the overall market. Beta of 1.2 means the stock moves 20% more than the market index. |
| **Terminal Value** | The estimated value of all cash flows beyond the 10-year forecast horizon. Often the largest and most uncertain part of a DCF valuation. |
| **Margin of Safety** | The gap between the model's estimated fair value and today's market price. A large positive margin of safety means the stock appears undervalued. |
| **Intrinsic Value** | The estimated fair value of the business based purely on its fundamentals — what it should be worth, independent of what the market currently thinks. |
| **Sensitivity Analysis** | A table showing how the estimated fair value changes when you vary the key assumptions (growth rate and discount rate). |
| **Assumption Diagnostic** | OpenQuant's built-in honesty check — it scores 8 dimensions of the analysis before showing results, so you know how much to trust the output. |
""")
