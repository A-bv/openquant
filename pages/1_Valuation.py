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
from ui.components.diagnostic import render_diagnostic, render_diagnostic_compact
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

    # ── Red flags — FIRST ────────────────────────────────────────────────────
    if rf_summary:
        render_red_flags(rf_summary)

    st.divider()

    # ── Suitability ──────────────────────────────────────────────────────────
    if suit and not suit.is_suitable:
        st.error(f"⛔ {suit.recommendation}")
        for alt in suit.alternative_methods:
            st.caption(f"Consider: {alt}")
        st.stop()

    # ── Assumption Diagnostic ────────────────────────────────────────────────
    if diag:
        render_diagnostic_compact(diag)

    st.divider()

    # ── Section 1: Company Overview ──────────────────────────────────────────
    st.subheader(f"📊 {company_name} ({ticker})")

    col1, col2 = st.columns([2, 1])
    with col1:
        if statements.revenue.dropna().shape[0] > 0:
            fig = revenue_fcf_sparklines(
                statements.revenue.dropna(),
                statements.free_cash_flow.dropna(),
                company_name,
            )
            st.plotly_chart(fig, use_container_width=True)
    with col2:
        if mult:
            st.metric("Current Price", f"${current_price:.2f}")
            if mult.ev_ebitda:
                st.metric("EV/EBITDA", f"{mult.ev_ebitda:.1f}x")
            if mult.fcf_yield:
                st.metric("FCF Yield", f"{mult.fcf_yield:.1%}")
            if mult.pe_ratio:
                st.metric("P/E Ratio", f"{mult.pe_ratio:.1f}x")

    st.divider()

    # ── Section 2: FCF Analysis ──────────────────────────────────────────────
    st.subheader("💵 Free Cash Flow")

    if fcf_a:
        st.caption(fcf_a.summary_text if hasattr(fcf_a, 'summary_text') else "")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Latest FCF", f"${fcf_a.latest_fcf/1e9:.2f}B")
        with col2:
            st.metric("Median Growth", f"{fcf_a.median_growth_rate:.1%}")
        with col3:
            st.metric("FCF Margin (median)", f"{float(fcf_a.fcf_margin.dropna().median()):.1%}")

        tab1, tab2 = st.tabs(["History", "Projections"])
        with tab1:
            fig = fcf_history_chart(
                statements.free_cash_flow.dropna(),
                statements.free_cash_flow.dropna() - statements.stock_based_compensation.dropna().fillna(0),
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

    st.divider()

    # ── Section 3: WACC ──────────────────────────────────────────────────────
    st.subheader("⚖️ Cost of Capital (WACC)")

    if wacc_r:
        render_wacc_metrics(wacc_r)
        capm_formula_panel(wacc_r.risk_free_rate, wacc_r.beta, wacc_r.market_risk_premium, wacc_r.cost_of_equity)
        wacc_formula_panel(wacc_r.equity_weight, wacc_r.cost_of_equity, wacc_r.debt_weight, wacc_r.cost_of_debt_pretax, wacc_r.tax_rate, wacc_r.wacc)

        col1, col2 = st.columns(2)
        with col1:
            if beta_r:
                fig = rolling_beta_chart(
                    beta_r.rolling_beta,
                    beta_r.beta,
                    beta_r.beta_ci_lower,
                    beta_r.beta_ci_upper,
                    ticker,
                )
                st.plotly_chart(fig, use_container_width=True)
                st.caption(beta_r.stability_note)
        with col2:
            fig = capital_structure_chart(wacc_r)
            st.plotly_chart(fig, use_container_width=True)
            st.caption(wacc_r.formula_trace)

    st.divider()

    # ── Section 4: Forward DCF ───────────────────────────────────────────────
    st.subheader("📐 Forward DCF Valuation")
    st.caption(
        "Three scenarios based on conservative / base / optimistic FCF growth assumptions. "
        "Current price shown for reference."
    )

    if dcf_r:
        st.metric("Current Price", f"${current_price:.2f}")
        render_dcf_metrics(dcf_r)

        terminal_value_formula_panel(
            dcf_r.base.terminal_fcf,
            dcf_r.terminal_growth_rate,
            wacc_r.wacc if wacc_r else 0.09,
            dcf_r.base.terminal_value,
        )

        tabs = st.tabs(["Conservative", "Base", "Optimistic"])
        for tab, scenario in zip(tabs, dcf_r.all_scenarios):
            with tab:
                col1, col2 = st.columns([2, 1])
                with col1:
                    fig = dcf_waterfall_chart(scenario, company_name)
                    st.plotly_chart(fig, use_container_width=True)
                with col2:
                    st.metric("Intrinsic Value", f"${scenario.intrinsic_value_per_share:.2f}")
                    st.metric("Margin of Safety", f"{scenario.margin_of_safety:.1%}")
                    st.metric("Terminal Value %", f"{scenario.terminal_value_pct:.0%}")
                    st.metric("FCF Growth", f"{scenario.growth_rate:.1%}")
                    st.metric("WACC Used", f"{scenario.wacc:.1%}")

    st.divider()

    # ── Section 5: Sensitivity ───────────────────────────────────────────────
    st.subheader("🎛️ Sensitivity Analysis")

    if gt and tt:
        col1, col2 = st.columns(2)
        with col1:
            fig = sensitivity_heatmap(
                gt.table, current_price,
                "Implied Share Price",
                "FCF Growth Rate", "WACC",
            )
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig = sensitivity_heatmap(
                tt.table, 70.0,
                "Terminal Value % of EV",
                "Terminal Growth", "WACC",
            )
            st.plotly_chart(fig, use_container_width=True)

        if gt and fcf_a and wacc_r:
            from core.sensitivity import SensitivityAnalyser
            plain = SensitivityAnalyser().generate_plain_language(
                gt, current_price, fcf_a.growth_base, wacc_r.wacc, fcf_a.median_growth_rate
            )
            st.caption(plain)

    st.divider()

    # ── Section 6: Reverse DCF ───────────────────────────────────────────────
    st.subheader("🔄 Reverse DCF — What Is The Market Betting On?")

    if rev_r:
        from core.reverse_dcf import ReverseDCFResult, ReverseDCFFailure

        if isinstance(rev_r, ReverseDCFFailure):
            st.warning(f"**{rev_r.reason}**")
            st.caption(rev_r.diagnostic)
            st.info(f"💡 {rev_r.suggestion}")
        else:
            st.info(f"📌 {rev_r.framing_note}")
            render_reverse_dcf_metrics(rev_r)

            fig = reverse_dcf_comparison_chart(
                rev_r.implied_growth_rate,
                rev_r.historical_median_growth,
                rev_r.historical_mean_growth,
                rev_r.revenue_cagr,
                ticker=ticker,
            )
            st.plotly_chart(fig, use_container_width=True)

            st.markdown(f"**Verdict:** {rev_r.verdict}")

    st.divider()

    # ── Section 7: Multiples Context ─────────────────────────────────────────
    if mult:
        st.subheader("📊 Market Multiples Context")
        st.caption("Not a primary valuation — context alongside DCF only.")
        st.caption(mult.interpretation)

    st.divider()

    # ── Section 8: Buffett's Questions ───────────────────────────────────────
    st.subheader("🤔 Qualitative Check — Buffett's Three Questions")
    st.caption(
        "The math is complete. These are the questions no model can answer for you."
    )
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("**1. Moat**\n\nDoes this company have a durable competitive advantage?")
    with col2:
        st.info("**2. Management**\n\nDo you trust and respect management?")
    with col3:
        st.info("**3. Durability**\n\nWill this business model look similar in 10 years?")

    st.divider()

    # ── Full Diagnostic ──────────────────────────────────────────────────────
    if diag:
        with st.expander("📋 Full Assumption Diagnostic", expanded=False):
            render_diagnostic(diag)

    # ── Audit Trail ──────────────────────────────────────────────────────────
    if trail:
        render_audit_trail(trail)
