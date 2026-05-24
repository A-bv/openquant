"""
OpenQuant — FastAPI backend.

Thin wrapper around core/. Zero business logic here.
All computation lives in core/.
"""

from __future__ import annotations

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import numpy as np

app = FastAPI(title="OpenQuant API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "https://*.vercel.app"],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyseRequest(BaseModel):
    ticker: str
    risk_free_rate: float = Field(default=0.045)
    market_risk_premium: float = Field(default=0.055)
    terminal_growth: float = Field(default=0.025)


# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "version": "1.0.0"}


# ── Analyse ───────────────────────────────────────────────────────────────────

@app.post("/analyse")
def analyse(req: AnalyseRequest):
    ticker = req.ticker.upper().strip()
    rf = req.risk_free_rate
    mrp = req.market_risk_premium
    tg = req.terminal_growth

    try:
        # 1 — Validate ticker
        from core.data import DataFetcher
        fetcher = DataFetcher()
        validation = fetcher.validate_ticker(ticker)
        if not validation.is_valid:
            raise HTTPException(status_code=400, detail={
                "error": validation.message,
                "ticker": ticker,
            })

        # 2 — Fetch data
        statements = fetcher.get_financial_statements(ticker)
        price_data = fetcher.get_prices(ticker)
        current_price = fetcher.get_current_price(ticker) or 0.0

        # 3 — FCF analysis
        from core.fcf import FCFAnalyser
        fcf_a = FCFAnalyser().analyse(statements)

        # 4 — Beta + WACC
        from core.wacc import BetaEstimator, WACCBuilder
        beta_r = BetaEstimator().estimate(price_data, statements)
        wacc_r = WACCBuilder().compute_wacc(
            statements, price_data, current_price,
            risk_free_rate=rf,
            market_risk_premium=mrp,
        )

        # 5 — Suitability (with WACC)
        from core.suitability import SuitabilityChecker
        suit = SuitabilityChecker().check(
            statements,
            trading_days=len(price_data.prices),
            sector=validation.sector,
            wacc_estimate=wacc_r.wacc,
            terminal_growth=tg,
        )

        # 6 — Compute net_debt and shares
        _debt_s = statements.total_debt.dropna()
        _cash_s = statements.cash_and_equivalents.dropna()
        _shares_s = statements.shares_outstanding.dropna()

        if _shares_s.empty:
            raise HTTPException(status_code=400, detail={
                "error": f"No shares outstanding data found in EDGAR for {ticker}.",
                "ticker": ticker,
            })

        net_debt = float(
            (_debt_s.iloc[-1] if not _debt_s.empty else 0.0)
            - (_cash_s.iloc[-1] if not _cash_s.empty else 0.0)
        )
        shares = float(_shares_s.iloc[-1])
        cash = float(_cash_s.iloc[-1]) if not _cash_s.empty else 0.0
        total_debt = float(_debt_s.iloc[-1]) if not _debt_s.empty else 0.0

        # Market cap
        market_cap = current_price * shares

        # Build FCF history
        fcf_series = statements.free_cash_flow.dropna()
        fcf_history = [
            {"year": int(d.year), "fcf": float(v)}
            for d, v in zip(fcf_series.index, fcf_series.values)
        ]

        # FCF margin (latest)
        fcf_margin_series = fcf_a.fcf_margin.dropna()
        fcf_margin_latest = float(fcf_margin_series.iloc[-1]) if not fcf_margin_series.empty else 0.0

        # Revenue latest
        rev_series = statements.revenue.dropna()
        rev_latest = float(rev_series.iloc[-1]) if not rev_series.empty else 0.0

        # Early return if not suitable
        if not suit.is_suitable:
            return {
                "ticker": ticker,
                "company_name": statements.company_name,
                "sector": validation.sector,
                "current_price": current_price,
                "market_cap": market_cap,
                "is_suitable": False,
                "suitability_rating": suit.overall_rating.value,
                "suitability_message": suit.recommendation,
                "alternative_methods": suit.alternative_methods,
                "fcf": {
                    "latest": float(fcf_series.iloc[-1]) if not fcf_series.empty else 0.0,
                    "median_growth": fcf_a.median_growth_rate,
                    "mean_growth": fcf_a.mean_growth_rate,
                    "revenue_cagr": fcf_a.revenue_cagr_5yr,
                    "fcf_margin": fcf_margin_latest,
                    "revenue_latest": rev_latest,
                    "history": fcf_history,
                },
                "warnings": [],
            }

        # 7 — Forward DCF
        from core.dcf import DCFEngine
        dcf_r = DCFEngine().value(
            fcf_analysis=fcf_a,
            wacc_result=wacc_r,
            current_price=current_price,
            shares_outstanding=shares,
            net_debt=net_debt,
            terminal_growth_rate=tg,
        )

        # 8 — Reverse DCF
        from core.reverse_dcf import ReverseDCFSolver, ReverseDCFResult
        rev_r = ReverseDCFSolver().solve(
            fcf_analysis=fcf_a,
            wacc_result=wacc_r,
            current_price=current_price,
            shares_outstanding=shares,
            net_debt=net_debt,
            terminal_growth_rate=tg,
        )

        rev_failed = not isinstance(rev_r, ReverseDCFResult)

        # 9 — Sensitivity
        from core.sensitivity import SensitivityAnalyser
        sa = SensitivityAnalyser()
        gt = sa.build_growth_wacc_table(fcf_a, wacc_r, current_price, shares, net_debt, tg)

        # Build sensitivity grid
        sens_values = gt.table.values.astype(float)
        # Replace NaN with None for JSON
        sens_json = [
            [None if np.isnan(v) else round(float(v), 2) for v in row]
            for row in sens_values
        ]
        # Find closest cell
        masked = np.where(np.isnan(sens_values), np.inf, np.abs(sens_values - current_price))
        min_row, min_col = np.unravel_index(np.argmin(masked), masked.shape)

        def _fmt_pct(v) -> str:
            try:
                return f"{float(str(v).rstrip('%')) / 100:.0%}"
            except Exception:
                return str(v)

        sens_rows = [_fmt_pct(r) for r in gt.table.index]
        sens_cols = [_fmt_pct(c) for c in gt.table.columns]

        # 10 — Multiples
        from core.multiples import MultiplesAnalyser
        mult = MultiplesAnalyser().compute(statements, current_price, total_debt, cash, dcf_r)

        # Build response
        response = {
            "ticker": ticker,
            "company_name": statements.company_name,
            "sector": validation.sector,
            "current_price": current_price,
            "market_cap": market_cap,
            "is_suitable": True,
            "suitability_rating": suit.overall_rating.value,
            "suitability_message": suit.recommendation,
            "alternative_methods": suit.alternative_methods,

            "fcf": {
                "latest": float(fcf_series.iloc[-1]) if not fcf_series.empty else 0.0,
                "median_growth": fcf_a.median_growth_rate,
                "mean_growth": fcf_a.mean_growth_rate,
                "revenue_cagr": fcf_a.revenue_cagr_5yr,
                "fcf_margin": fcf_margin_latest,
                "revenue_latest": rev_latest,
                "history": fcf_history,
            },

            "wacc": {
                "wacc": wacc_r.wacc,
                "beta": wacc_r.beta,
                "cost_of_equity": wacc_r.cost_of_equity,
                "cost_of_debt_pretax": wacc_r.cost_of_debt_pretax,
                "cost_of_debt_aftertax": wacc_r.cost_of_debt_pretax * (1 - wacc_r.tax_rate),
                "risk_free_rate": wacc_r.risk_free_rate,
                "market_risk_premium": wacc_r.market_risk_premium,
                "tax_rate": wacc_r.tax_rate,
                "equity_weight": wacc_r.equity_weight,
                "debt_weight": wacc_r.debt_weight,
                "formula_trace": wacc_r.formula_trace,
            },

            "reverse_dcf": {
                "implied_growth": rev_r.implied_growth_rate if not rev_failed else None,
                "historical_median": rev_r.historical_median_growth if not rev_failed else fcf_a.median_growth_rate,
                "historical_mean": rev_r.historical_mean_growth if not rev_failed else fcf_a.mean_growth_rate,
                "revenue_cagr": rev_r.revenue_cagr if not rev_failed else fcf_a.revenue_cagr_5yr,
                "gap_vs_historical": rev_r.growth_vs_history if not rev_failed else None,
                "verdict": rev_r.verdict if not rev_failed else getattr(rev_r, "reason", "Reverse DCF failed."),
                "gdp_growth": 0.030,
                "failed": rev_failed,
            },

            "dcf": {
                "conservative": {
                    "iv": dcf_r.conservative.intrinsic_value_per_share,
                    "growth": dcf_r.conservative.growth_rate,
                    "upside": dcf_r.conservative.upside_downside,
                    "tv_pct": dcf_r.conservative.terminal_value_pct,
                    "pv_fcfs": dcf_r.conservative.pv_fcfs_total,
                    "pv_tv": dcf_r.conservative.pv_terminal_value,
                },
                "base": {
                    "iv": dcf_r.base.intrinsic_value_per_share,
                    "growth": dcf_r.base.growth_rate,
                    "upside": dcf_r.base.upside_downside,
                    "tv_pct": dcf_r.base.terminal_value_pct,
                    "pv_fcfs": dcf_r.base.pv_fcfs_total,
                    "pv_tv": dcf_r.base.pv_terminal_value,
                },
                "optimistic": {
                    "iv": dcf_r.optimistic.intrinsic_value_per_share,
                    "growth": dcf_r.optimistic.growth_rate,
                    "upside": dcf_r.optimistic.upside_downside,
                    "tv_pct": dcf_r.optimistic.terminal_value_pct,
                    "pv_fcfs": dcf_r.optimistic.pv_fcfs_total,
                    "pv_tv": dcf_r.optimistic.pv_terminal_value,
                },
                "net_debt": net_debt,
            },

            "sensitivity": {
                "rows": sens_rows,
                "cols": sens_cols,
                "values": sens_json,
                "closest_row": int(min_row),
                "closest_col": int(min_col),
            },

            "multiples": {
                "ev_ebitda": mult.ev_ebitda,
                "pe_ratio": mult.pe_ratio,
                "fcf_yield": mult.fcf_yield,
            },

            "warnings": suit.red_flags and [c.message for c in suit.red_flags] or [],
        }

        return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e), "ticker": ticker})
