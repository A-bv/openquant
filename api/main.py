"""
OpenQuant — FastAPI backend.

Thin wrapper around core/. Zero business logic here.
All computation lives in core/.
"""

from __future__ import annotations

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
import math
import os
import re
import uuid
import json
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
import numpy as np

logger = logging.getLogger("openquant.api")
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))


def _sanitize(obj: Any) -> Any:
    """Recursively replace NaN/Inf floats with None so the response is valid JSON."""
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    if isinstance(obj, dict):
        return {k: _sanitize(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_sanitize(v) for v in obj]
    return obj


def _diagnostic_payload(diagnostic: Any) -> dict:
    return {
        "rating": diagnostic.overall_rating.value,
        "total_severity": diagnostic.total_severity,
        "summary": diagnostic.summary_text,
        "disclaimer": diagnostic.disclaimer,
        "dimensions": [
            {
                "name": d.name,
                "rating": d.rating.value,
                "severity": d.severity,
                "message": d.message,
                "detail": d.detail,
            }
            for d in diagnostic.dimensions
        ],
    }


def _red_flags_payload(summary: Any) -> dict:
    return {
        "flags": summary.flags,
        "has_blocking_issues": summary.has_blocking_issues,
        "overall_confidence": summary.overall_confidence,
    }


def _audit_payload(audit: Any) -> dict:
    return {
        "summary": audit.to_display_dict(),
        "formula_references": audit.formula_references,
        "warnings": audit.all_warnings,
    }

app = FastAPI(title="OpenQuant API", version="1.0.0")
CALIBRATION_SUMMARY_PATH = (
    Path(__file__).resolve().parents[1]
    / "backtest"
    / "results"
    / "calibration_summary.json"
)

# CORS — explicit local dev origins plus an anchored regex for this project's
# Vercel deployments. The previous regex `https://.*\.vercel\.app` was both
# unanchored AND combined with allow_credentials=True, letting any attacker
# register e.g. `attacker.vercel.app` and read authenticated responses.
# Override via ALLOWED_ORIGIN_REGEX env var for non-Vercel deploys.
_ALLOWED_ORIGIN_REGEX = os.getenv(
    "ALLOWED_ORIGIN_REGEX",
    r"^https://openquant(-[a-z0-9]+)?(-[a-z0-9-]+)?\.vercel\.app$",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_origin_regex=_ALLOWED_ORIGIN_REGEX,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)


class AnalyseRequest(BaseModel):
    ticker: str = Field(min_length=1, max_length=10, pattern=r"^[A-Za-z][A-Za-z0-9.\-]{0,9}$")
    risk_free_rate: float = Field(default=0.045, ge=0.0, le=0.20)
    market_risk_premium: float = Field(default=0.055, ge=0.0, le=0.20)
    terminal_growth: float = Field(default=0.025, ge=-0.05, le=0.05)

    @field_validator("risk_free_rate", "market_risk_premium", "terminal_growth")
    @classmethod
    def _finite(cls, v: float) -> float:
        if not math.isfinite(v):
            raise ValueError("must be a finite number")
        return v


_TICKER_RE = re.compile(r"^[A-Za-z][A-Za-z0-9.\-^]{0,9}$")


class DiversificationRequest(BaseModel):
    tickers: list[str] = Field(min_length=2, max_length=15)
    years: int = Field(default=3, ge=1, le=10)
    risk_free_rate: float = Field(default=0.045, ge=0.0, le=0.20)

    @field_validator("tickers")
    @classmethod
    def _valid_tickers(cls, v: list[str]) -> list[str]:
        cleaned: list[str] = []
        for raw in v:
            t = raw.upper().strip()
            if not _TICKER_RE.match(t):
                raise ValueError(f"invalid ticker: {raw!r}")
            if t not in cleaned:
                cleaned.append(t)
        if len(cleaned) < 2:
            raise ValueError("need at least 2 distinct tickers")
        return cleaned


class NowOrLaterRequest(BaseModel):
    lump_sum: float = Field(ge=0)
    payment: float = Field(ge=0)
    n_payments: int = Field(ge=1, le=600)
    rate: float = Field(gt=-1.0, le=2.0)   # per-period discount rate
    growth: float = Field(default=0.0, ge=-0.5, le=1.0)
    first_payment_today: bool = True
    kind: str = Field(default="receive")
    currency: str = Field(default="$", max_length=3)

    @field_validator("kind")
    @classmethod
    def _valid_kind(cls, v: str) -> str:
        if v not in ("receive", "pay"):
            raise ValueError("kind must be 'receive' or 'pay'")
        return v

    @field_validator("lump_sum", "payment", "rate", "growth")
    @classmethod
    def _finite(cls, v: float) -> float:
        if not math.isfinite(v):
            raise ValueError("must be a finite number")
        return v


# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "version": "1.0.0"}


@app.get("/calibration")
def calibration():
    """Return the main historical backtest reliability results used by the app."""
    try:
        return _sanitize(json.loads(CALIBRATION_SUMMARY_PATH.read_text()))
    except FileNotFoundError:
        raise HTTPException(
            status_code=503,
            detail={"error": "Calibration summary has not been generated."},
        )
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail={"error": "Calibration summary is not valid JSON."},
        )


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
        current_price = fetcher.get_current_price(ticker)
        if current_price is None or not math.isfinite(current_price) or current_price <= 0:
            raise HTTPException(status_code=502, detail={
                "error": f"Could not fetch a valid current price for {ticker}.",
                "ticker": ticker,
            })
        current_price = float(current_price)

        # 3 — FCF analysis
        from core.valuation.fcf import FCFAnalyser
        fcf_a = FCFAnalyser().analyse(statements)

        # 4 — Beta + WACC
        from core.valuation.wacc import BetaEstimator, WACCBuilder
        beta_r = BetaEstimator().estimate(price_data, statements)
        wacc_r = WACCBuilder().compute_wacc(
            statements, price_data, current_price,
            risk_free_rate=rf,
            market_risk_premium=mrp,
        )

        # 5 — Suitability (with WACC)
        from core.valuation.suitability import SuitabilityChecker
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
        if not math.isfinite(shares) or shares <= 0:
            raise HTTPException(status_code=400, detail={
                "error": f"Latest shares outstanding for {ticker} is {shares}; cannot value.",
                "ticker": ticker,
            })
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
            return _sanitize({
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
            })

        # 7 — Forward DCF
        from core.valuation.dcf import DCFEngine
        dcf_r = DCFEngine().value(
            fcf_analysis=fcf_a,
            wacc_result=wacc_r,
            current_price=current_price,
            shares_outstanding=shares,
            net_debt=net_debt,
            terminal_growth_rate=tg,
        )

        # 8 — Reverse DCF
        from core.valuation.reverse_dcf import ReverseDCFSolver, ReverseDCFResult
        rev_r = ReverseDCFSolver().solve(
            fcf_analysis=fcf_a,
            wacc_result=wacc_r,
            current_price=current_price,
            shares_outstanding=shares,
            net_debt=net_debt,
            terminal_growth_rate=tg,
        )

        rev_failed = not isinstance(rev_r, ReverseDCFResult)

        # 8b — Assumption diagnostic, red flags, and audit trail.
        from core.valuation.assumption_diagnostic import DiagnosticBuilder
        from core.valuation.red_flags import RedFlagBuilder
        from core.valuation.audit_trail import AuditTrailBuilder

        rev_for_context = rev_r if not rev_failed else None
        diagnostic = DiagnosticBuilder().build(
            statements=statements,
            dcf_result=dcf_r,
            beta_result=beta_r,
            reverse_result=rev_for_context,
        )
        red_flags = RedFlagBuilder().build(
            ticker=ticker,
            diagnostic=diagnostic,
            suitability=suit,
            dcf_result=dcf_r,
            reverse_result=rev_for_context,
        )
        audit = AuditTrailBuilder().build(
            statements=statements,
            fcf_analysis=fcf_a,
            wacc_result=wacc_r,
            dcf_result=dcf_r,
            suitability=suit,
            diagnostic=diagnostic,
            reverse_result=rev_for_context,
            terminal_growth_rate=tg,
        )

        # 9 — Sensitivity
        from core.valuation.sensitivity import SensitivityAnalyser
        sa = SensitivityAnalyser()
        gt = sa.build_growth_wacc_table(fcf_a, wacc_r, current_price, shares, net_debt, tg)

        # Build sensitivity grid
        sens_values = gt.table.values.astype(float)
        # Replace NaN with None for JSON
        sens_json = [
            [None if np.isnan(v) else round(float(v), 2) for v in row]
            for row in sens_values
        ]
        # Find closest cell. If the grid is empty or every cell is NaN,
        # fall back to (0, 0) rather than crashing on argmin.
        if sens_values.size == 0 or np.all(np.isnan(sens_values)):
            min_row, min_col = 0, 0
        else:
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
        from core.valuation.multiples import MultiplesAnalyser
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
                "conclusion": rev_r.verdict if not rev_failed else getattr(rev_r, "reason", "Reverse DCF failed."),
                "gdp_growth": 0.030,
                "failed": rev_failed,
            },

            # Inputs needed for client-side slider recomputation.
            "dcf_inputs": {
                "base_fcf": float(dcf_r.base_fcf) if dcf_r.base_fcf is not None else None,
                "shares_outstanding": shares,
                "net_debt": net_debt,
                "horizon": dcf_r.forecast_horizon,
                "terminal_growth": tg,
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

            "diagnostic": _diagnostic_payload(diagnostic),
            "red_flags": _red_flags_payload(red_flags),
            "audit": _audit_payload(audit),

            "warnings": red_flags.flags or (suit.red_flags and [c.message for c in suit.red_flags]) or [],
        }

        return _sanitize(response)

    except HTTPException:
        raise
    except Exception as e:
        # Log the full exception server-side; do not leak internal details
        # (file paths, library tracebacks, env-influenced messages) to the
        # client. Return a request id the user can quote for support.
        request_id = uuid.uuid4().hex[:12]
        logger.exception(
            "analyse failed (request_id=%s ticker=%s): %s",
            request_id, ticker, e,
        )
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal error while analysing this ticker.",
                "ticker": ticker,
                "request_id": request_id,
            },
        )


# ── Diversification (Risk & Portfolio block) ────────────────────────────────────

@app.post("/diversification")
def diversification(req: DiversificationRequest):
    """
    Turn the EPFL Risk & Return block into a concrete, real-data deliverable:
    "you hold N positions — in risk terms, X independent bets."

    Equal-weighted. Pure orchestration here; the maths lives in core.portfolio
    (pinned against EPFL Sample Exam 2 P4 in tests/test_portfolio.py).
    """
    import pandas as pd
    from core.data import DataFetcher, DataFetchError
    from core.common import log_returns
    from core.portfolio import analyse_diversification

    tickers = req.tickers  # already cleaned/validated/deduped
    fetcher = DataFetcher()

    price_map: dict[str, Any] = {}
    failed: list[str] = []
    for t in tickers:
        try:
            series = fetcher.price_fetcher.fetch(t, years=req.years)
            if series is not None and len(series) > 0:
                price_map[t] = series
            else:
                failed.append(t)
        except DataFetchError:
            failed.append(t)
        except Exception:
            failed.append(t)

    if len(price_map) < 2:
        raise HTTPException(status_code=400, detail={
            "error": "Need at least 2 tickers with valid price data.",
            "failed": failed,
        })

    prices = pd.DataFrame(price_map).dropna(how="any")
    if len(prices) < 60:
        raise HTTPException(status_code=422, detail={
            "error": "Not enough overlapping trading days for these tickers.",
            "overlapping_days": int(len(prices)),
        })

    returns = pd.DataFrame(
        {col: log_returns(prices[col]) for col in prices.columns}
    ).dropna()

    try:
        report = analyse_diversification(returns, risk_free_rate=req.risk_free_rate)
    except ValueError as e:
        raise HTTPException(status_code=422, detail={"error": str(e)})

    payload = report.to_dict()
    payload.update({
        "summary_lines": report.summary_lines(),
        "detail_lines": report.detail_lines(),
        "years": req.years,
        "trading_days": int(len(returns)),
        "failed_tickers": failed,
    })
    return _sanitize(payload)


# ── Now or later? (everyday-money / time value of money) ─────────────────────────

@app.post("/now-or-later")
def now_or_later(req: NowOrLaterRequest):
    """
    The everyday-money front door: "take the money now, or spread over time?"

    No market data, cannot fail on a ticker. Pure orchestration; the maths
    lives in core.money (pinned against the PFEM lottery in tests/test_money.py).
    """
    from core.money import compare_now_vs_later

    try:
        result = compare_now_vs_later(
            lump_sum=req.lump_sum,
            payment=req.payment,
            n_payments=req.n_payments,
            rate=req.rate,
            growth=req.growth,
            first_payment_today=req.first_payment_today,
            kind=req.kind,
            currency=req.currency,
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail={"error": str(e)})

    payload = result.to_dict()
    payload.update({
        "summary_lines": result.summary_lines(),
        "detail_lines": result.detail_lines(),
    })
    return _sanitize(payload)
