# OpenQuant

**A transparent companion to the EPFL Principles of Finance course — applied to real US market data.**

> OpenQuant doesn't claim to predict the future. It applies the academic
> valuation framework you learned in finance class to today's market data,
> shows every formula it used, and openly publishes how well it has
> performed against history.

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-163%20passing-brightgreen.svg)]()
[![Backtest](https://img.shields.io/badge/backtest-published-yellow.svg)](docs/backtest_2014_2024.md)

---

## What it is

OpenQuant is a **pedagogical** equity valuation tool. It takes any US-listed
stock ticker and runs the complete corporate-finance pipeline taught in the
[EPFL Principles of Finance](https://edu.epfl.ch/coursebook/en/principles-of-finance-FIN-401)
curriculum (Berk & DeMarzo, *Corporate Finance*):

```
SEC EDGAR financials  →  Free Cash Flow  →  Beta + CAPM  →  WACC
                                                              ↓
   Reverse DCF  ←  Sensitivity grid  ←  3-scenario DCF + Terminal Value
   (what does today's price imply?)
```

Every formula on the page is traceable to a named EPFL formula-sheet entry
or textbook chapter. Every number can be reproduced from public data.

It is **not** a Bloomberg replacement. It is **not** financial advice.
It is the tool that should have existed during the course — when you needed
to see "what does this theory actually say about a real company?"

---

## Why this exists

The EPFL course teaches the formulas. The textbook works through cases.
But there's a gap between *learning* DCF and *applying* it to a stock you
care about — and the proprietary tools that fill that gap (Bloomberg,
FactSet) cost more than tuition and never show their work.

OpenQuant fills that gap. It applies the same formulas you'd write on an
exam to real EDGAR filings, and prints every step.

It also does something most retail tools don't: it **validates itself
honestly against history** and publishes the result, even when the result
is unflattering.

---

## Demo

```bash
git clone https://github.com/A-bv/openquant
cd openquant
pip install -r requirements.txt

# Backend (FastAPI)
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000

# Frontend (React + Vite)
cd frontend && npm install && npm run dev
```

Open http://localhost:5173 and type `TSLA`, `AAPL`, `MSFT`, or any US ticker.

Or hit the API directly:
```bash
curl -X POST http://localhost:8000/analyse \
  -H 'Content-Type: application/json' \
  -d '{"ticker":"AAPL"}'
```

---

## What you see

**Top of page** — a Buffett-style verdict in plain English: *"Tesla at $426 is
priced as if FCF will grow 57%/yr for the next decade. The model says
overvalued."*

**Below that** — an honest disclosure: *"Math is correct (163 EPFL tests
pass), but our predictions on 50 real stocks 2014-2024 did NOT reliably
predict actual returns (R² = 0.04). Read the page knowing this."*

**Then the math, in narrative order:**

1. **Market's bet** — reverse DCF panel showing the implied growth rate today's
   price requires, vs the company's historical track record
2. **Three scenarios** (conservative / base / optimistic) with sliders to
   override every assumption live
3. **"Why might X be worth buying anyway?"** — four cards explaining
   exactly what you'd need to believe for the model to be wrong
4. **Multiples cross-check** — P/E, EV/EBITDA, FCF yield vs sector
5. **FCF history** — actual cash generated, year by year
6. **Sensitivity heatmap** — IV at every combination of growth × WACC
7. **Show your work** — full WACC derivation, every component sourced

Every jargon term is hover-explainable (dotted-underline). Every formula
has an EPFL citation badge.

---

## EPFL course coverage

| Chapter | Topic | Coverage |
|---|---|:---:|
| **H1** | Time value of money — PV/FV, perpetuity, annuity, growing annuity | ✅ |
| H1 | Bond pricing + YTM | ❌ Out of scope |
| H1+ | Rate conversions, spot/forward rates, duration, PI | ❌ Out of scope |
| **H2a** | Stats — mean, variance, covariance, correlation | ✅ (via numpy/pandas) |
| **H2b** | Portfolio theory — variance, min-variance, efficient frontier | 🟡 Code complete, UI orphaned |
| **H2c** | CAPM, beta from correlation, idiosyncratic variance, Sharpe | ✅ |
| **H3a** | WACC, Hamada unlevering, MM I/II | ✅ |
| **H3b** | DCF, FCF formula (full), NPV vs IRR, terminal value | ✅ |
| **H3+** | APV, PV of Tax Shield (PVTS) | 🟡 PVTS helper exists; full APV not assembled |
| H3+ | Bankruptcy costs (PVBC, default probabilities) | ❌ |
| **WB** | Buffett intrinsic value via BVPS | ❌ |
| **H4** | Derivatives — forwards, futures, swaps, options, Black-Scholes | ❌ Out of scope |

Honest score: **~50% of the EPFL course is in the codebase, ~30% reaches
the UI.** Equity valuation is fully covered; bonds and derivatives are
intentionally out of scope.

**Every implemented formula is pinned to the actual EPFL Sample Exam answer keys** —
see [`tests/test_epfl_exam1.py`](tests/test_epfl_exam1.py) and
[`tests/test_epfl_exam2.py`](tests/test_epfl_exam2.py). If the test passes,
the math is right.

---

## The honest backtest

We ran the model "as of" January 2014 on 50 S&P 500 stocks (period-appropriate
risk-free rate of 2.65%, MRP of 5.0% — not today's values) and compared each
verdict to the realized 10-year total return through January 2024.

| Model verdict | n | Mean realized 10-yr return |
|---|:---:|---:|
| Stocks called "undervalued" | 25 | **+12.3%/yr** |
| Stocks called "fairly priced" | 2 | +9.4%/yr |
| Stocks called "overvalued" | 6 | +13.6%/yr |
| S&P 500 baseline | — | +12.1%/yr |

**Calibration regression:** `R² = 0.04`, slope ≈ 0. The model's verdicts
explain ~4% of cross-sectional return variance — essentially zero
predictive power on this universe.

This is the kind of finding most retail tools never publish. We make it
the centerpiece of the trust story because **a transparent model that admits
its limits is more useful than a black box that doesn't**.

Full report: [docs/backtest_2014_2024.md](docs/backtest_2014_2024.md).

Why the calibration is weak (all documented in the report):
- 35% FCF growth cap compounded over 10 years inflates year-10 cash flows ~20×
- 2014 low-rate regime produces WACC ≈ 5-7%, making terminal value dominate
- Universe selection biases toward mature firms

These are tractable model-design issues, not implementation bugs. Future
work would fix them and re-publish.

---

## Architecture

```
openquant/
├── api/
│   └── main.py                 ← FastAPI /analyse endpoint, ~300 lines
├── core/                       ← Pure Python finance. Zero web deps. 163 tests.
│   ├── data.py                 ← SEC EDGAR + yfinance + cache
│   ├── fcf.py                  ← FCF formula + projection
│   ├── wacc.py                 ← Beta, CAPM, Hamada, WACC
│   ├── dcf.py                  ← Forward DCF, terminal value, NPV, IRR, PVTS
│   ├── reverse_dcf.py          ← Solves: g | IV(g) = price
│   ├── sensitivity.py          ← Growth × WACC grid
│   ├── multiples.py            ← P/E, EV/EBITDA, FCF yield
│   ├── suitability.py          ← 8-check DCF gate
│   ├── assumption_diagnostic.py  ← 8-dimension risk scoring
│   ├── red_flags.py            ← Warning aggregator
│   ├── audit_trail.py          ← Reproducible formula trace
│   └── portfolio.py            ← V = DCD', min-variance weights (no UI yet)
├── backtest/                   ← Historical validation pipeline
│   ├── universe.py             ← 50-stock S&P 500 cohort
│   ├── macro.py                ← Period-appropriate rf, MRP
│   ├── edgar_historical.py     ← XBRL extractor with `filed ≤ as_of` filter
│   ├── run.py                  ← Single-ticker pipeline
│   ├── batch.py                ← All-tickers runner
│   ├── analyse.py              ← Calibration metrics
│   └── results/                ← CSV + JSON outputs
├── frontend/
│   └── src/
│       ├── App.jsx             ← v3 flow: verdict → reverse DCF → sliders → math
│       └── components/         ← Hero, scorecard, sliders, calibration, charts
├── tests/                      ← 163 tests. EPFL exam answer keys as fixtures.
│   ├── test_epfl_exam1.py      ← 23 tests, Sample Exam 1 problems 2-3
│   ├── test_epfl_exam2.py      ← 21 tests, Sample Exam 2 problems 2-5
│   ├── test_regression_fixes.py  ← 21 tests guarding round 1-4 review fixes
│   ├── test_dcf.py, test_fcf.py, test_utils.py, test_data.py
│   └── conftest.py             ← Ground-truth fixtures (Exam 1 P2, EPFL_H2)
└── docs/
    ├── backtest_plan.md            ← Scope doc
    ├── backtest_2014_2024.md       ← Honest calibration report
    ├── phase1_tsla_sketch.md       ← Original UI sketch
    └── phase1_tsla_sketch_v3.md    ← Current v3 UI design
```

**Dependency rule:** `core/` imports nothing from `api/` or `frontend/`.
Tests import `core/` only. This means the entire math layer can be
verified without running the web stack.

---

## What's deliberately not here

This isn't a feature list of things "coming soon." These are scope decisions:

- **Bond pricing & yield curves (H1+ in EPFL)** — different mental model;
  would dilute the equity focus
- **Derivatives (H4)** — separate product, different audience
- **Buffett BVPS method (WB section)** — covered philosophically in the
  Buffett note at page bottom; not implemented as a numeric method
- **Portfolio module UI** — code in `core/portfolio.py` is tested against
  EPFL Exam 2 ground truths but the React UI doesn't expose it.
  Restoration is feasible (~1 day) if there's demand.
- **PVBC / full APV** — partial coverage (PVTS helper); not the centerpiece
- **Cross-stock comparison / peer analysis** — single-stock focus by design
- **Saved watchlist / user accounts** — explicitly not in scope

---

## Limits of the model (honest disclosure)

DCF on individual stocks has fundamental limits this tool inherits:

1. **Forecast risk** — projections beyond year 3 are guesses
2. **Terminal value dominance** — 50-70% of EV comes from the post-year-10
   period, which we can't observe
3. **β instability** — equity beta drifts; Hamada unlevering only partly
   addresses this
4. **Survivorship bias** — universe selection (S&P, EDGAR coverage) tilts
   toward survivors
5. **Regime sensitivity** — same model, different macro regime, different
   verdict. We hard-code the macro snapshot per backtest "as of" date
   for that reason.
6. **No predictive power demonstrated** — our backtest R² = 0.04. We don't
   claim what we can't prove.

These are the same limits every DCF tool has, including Bloomberg's.
The difference is we tell you.

---

## Built on

- [SEC EDGAR](https://www.sec.gov/edgar/sec-api-documentation) — XBRL filings
- [yfinance](https://github.com/ranaroussi/yfinance) — daily prices
- [Damodaran NYU](https://pages.stern.nyu.edu/~adamodar/) — historical macro
- FastAPI + React + Recharts + scipy

Inspired by Aswath Damodaran's open spreadsheets — same philosophy
(show your work, admit your limits), but automated.

---

## License & contribution

MIT licensed. PRs welcome but the project is **deliberately scope-constrained**
to "EPFL Principles of Finance applied transparently to equity." Features
outside that scope (bonds, derivatives, AI predictions) will likely be
declined.

If you find a math bug or an EPFL exam case where our answer disagrees
with the answer key, that's the highest priority issue.

---

## Citation

If this helped you, a star is appreciated. If you use OpenQuant for academic
work, cite it as:

```
OpenQuant: a transparent companion to EPFL Principles of Finance.
github.com/A-bv/openquant, 2025.
```

---

*OpenQuant — transparent academic valuation applied to real markets. Tested.
Backtested. Honest about both.*
