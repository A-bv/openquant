# OpenQuant

**The EPFL Principles of Finance course, applied to real stocks — with every formula traceable, every assumption visible, and a published backtest of how well it works.**

> Most stock-valuation tools give you a number with no derivation.
> OpenQuant gives you the derivation, then tells you how often the number has been right.

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-161%20passing-brightgreen.svg)]()
[![EPFL exam ground truths](https://img.shields.io/badge/EPFL%20exam%20answers-44%20verified-blue.svg)](tests/test_epfl_exam1.py)
[![Backtest](https://img.shields.io/badge/backtest-R%C2%B2%20%3D%200.04%20%E2%80%94%20published-yellow.svg)](docs/backtest_2014_2024.md)

---

## What it is

**A pedagogical equity-valuation tool.** You type a US stock ticker.
OpenQuant runs the exact corporate-finance pipeline taught in the
[EPFL Principles of Finance](https://edu.epfl.ch/coursebook/en/principles-of-finance-FIN-401)
course (Berk & DeMarzo, *Corporate Finance*) on live SEC EDGAR filings:

```
EDGAR financials  →  Free Cash Flow  →  Beta + CAPM  →  WACC
                                                         ↓
   Reverse DCF  ←  Sensitivity grid  ←  3-scenario DCF + Terminal Value
   (what does today's price imply?)
```

Every formula is traceable to a named page of the EPFL formula sheet, a
chapter of Berk-DeMarzo, AND a unit test that pins our implementation to
a published exam answer key.

It is **not** Bloomberg, **not** Simply Wall St, **not** financial advice.
It is **the tool you wished you had when you were taking the course** —
when you wanted to see what these formulas actually say about a real
company you care about.

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

Open http://localhost:5173 and type `TSLA`, `AAPL`, `MSFT`, `ACN`,
or any US ticker.

Or call the API directly:
```bash
curl -X POST http://localhost:8000/analyse \
  -H 'Content-Type: application/json' \
  -d '{"ticker":"AAPL"}'
```

---

## What the tool does

Section by section, in the order you see them when you analyse a ticker:

| What you see | What it tells you | EPFL chapter |
|---|---|:---:|
| **Hero verdict** in plain English | "Tesla at $426 is overvalued under our model — even the optimistic scenario implies $122." | — |
| **Confidence scorecard** (5 dots) | Value, implied growth, FCF track record, balance sheet, DCF suitability — green/amber/red. | — |
| **Honest disclosure banner** | "Math is correct (161 tests pass). Predictions on 50 real stocks 2014-2024 explain only 4% of realized returns (R² = 0.04). Read knowing this." | — |
| **What is the market's bet?** | The reverse DCF: at today's price, what FCF growth must the company deliver for the next 10 years? Compared to its historical median, mean, revenue CAGR, and GDP. | H3b |
| **Three scenarios** | Conservative / Base / Optimistic intrinsic value per share, each with growth rate and terminal value share. | H3b |
| **Try your own assumptions** | Three sliders (FCF growth, WACC, terminal growth). The intrinsic value recomputes live in your browser — you don't have to believe our β or our hurdle rate. | H3b |
| **Why might X be worth buying anyway?** | Four cards naming exactly which assumptions you'd need to hold for the verdict to be wrong. | — |
| **Sanity check — multiples** | P/E, EV/EBITDA, FCF yield vs sector / S&P / Treasury benchmarks. | H3b |
| **Free cash flow history** | 10-year bar chart of actual FCF. Red bars = negative years. | H3b |
| **Sensitivity heatmap** | Intrinsic value at every combination of growth × WACC. | H3b |
| **Show your work — WACC** | Risk-free rate → β → market risk premium → cost of equity (CAPM) → cost of debt (after-tax) → WACC. Every line with EPFL citation. | H3a, H2c |

Every jargon term has a hover-tooltip. Every formula has an EPFL citation
badge that names the exam problem it was tested against.

---

## What the tool does NOT do (by design)

OpenQuant covers the **equity-valuation** half of the EPFL course.
The other half — bonds, derivatives, and full portfolio optimisation —
is **deliberately out of scope**. Here's the full map:

| EPFL chapter | Topic | In OpenQuant? |
|---|---|:---:|
| **H1** | TVM — PV/FV, perpetuity, annuity, growing annuity | ✅ |
| H1 | Bond pricing & YTM | ❌ Out of scope |
| H1+ | Rate conversions, spot/forward rates, duration, profitability index | ❌ Out of scope |
| **H2a** | Stats — mean, variance, covariance, correlation | ✅ |
| **H2b** | Portfolio theory — variance, min-variance, efficient frontier | 🟡 Closed-form 2-asset weight only |
| **H2c** | CAPM, beta from correlation, idiosyncratic variance, Sharpe | ✅ |
| **H3a** | WACC, Hamada unlevering, MM I/II | ✅ |
| **H3b** | DCF, FCF formula (full), NPV vs IRR, terminal value | ✅ |
| **H3+** | APV, PV of Tax Shield (PVTS) | 🟡 PVTS helper only |
| H3+ | Bankruptcy costs (PVBC, default probabilities) | ❌ Out of scope |
| H4 | Forwards, futures, swaps | ❌ Out of scope |
| H4 | Options, put-call parity, binomial, Black-Scholes | ❌ Out of scope |
| WB | Buffett intrinsic value via BVPS | ❌ Out of scope |

**Honest tally:** ~50% of the EPFL course implemented, ~30% reaches the UI.
The half we cover (equity valuation) is covered comprehensively. The
half we don't cover (bonds, derivatives, full portfolio construction) is
**explicitly excluded** so we can be excellent at one thing rather than
mediocre at everything.

If you're studying H1+ (yield curves), H4 (derivatives), or building a
robo-advisor portfolio engine, this is the wrong tool. We won't pretend
otherwise.

---

## Why this is different

There are dozens of free DCF calculators on the internet. None of them
combine all four of these:

| | OpenQuant | Typical DCF tool | Bloomberg | Simply Wall St |
|---|:---:|:---:|:---:|:---:|
| Every formula visible | ✅ | ❌ | ❌ | ❌ |
| Every formula cited to course material | ✅ | ❌ | ❌ | ❌ |
| Unit-tested against published exam answer keys | ✅ | ❌ | ❌ | ❌ |
| Reverse DCF as the centerpiece | ✅ | ❌ | ❌ | 🟡 |
| Live interactive assumption sliders | ✅ | 🟡 | ✅ | ❌ |
| **Backtest of the tool's own predictions published** | ✅ | ❌ | ❌ | ❌ |
| Open source, free, no account | ✅ | varies | $24K/yr | freemium |

The killer one is the bottom row. Every other tool that gives you a "fair
value" has a track record. None of them publish it. We do.

---

## The honest backtest

We ran the full pipeline "as of" January 31, 2014 on 50 S&P 500 stocks
chosen to span sectors and growth profiles. We used **period-appropriate
macro inputs** — 10-year Treasury at 2.65%, market risk premium 5.0%
(Damodaran's implied ERP for that month) — not today's values. Using
today's rates for a 2014 valuation would be hindsight cheating.

Then we waited until January 2024 and compared each verdict to the
realized 10-year total return.

| Model said | n | Realized 10-yr return (annualised) |
|---|:---:|---:|
| "Undervalued" (model says buy) | 25 | **+12.3%/yr** |
| "Fairly priced" | 2 | +9.4%/yr |
| "Overvalued" (model says avoid) | 6 | **+13.6%/yr** |
| S&P 500 baseline | — | +12.1%/yr |

**Calibration regression:** `R² = 0.04`, slope ≈ 0.

In English: the model's verdicts barely predict realized returns. The
"undervalued" basket matched the index. The "overvalued" basket
slightly outperformed it. **As a stock picker, this model is essentially
a coin flip.**

This is documented honestly because:

1. The tool is **pedagogical, not predictive.** Knowing the math is
   correct is different from knowing the model is calibrated.
2. The root causes are tractable and documented: the 35% growth cap
   compounded over 10 years is unrealistic; the 2014 low-rate regime
   makes terminal values dominate; survivor selection biases the
   universe. Each is a fixable design choice.
3. **No other retail tool publishes their backtest.** Treating this as a
   weakness is the wrong frame — it's the project's strongest
   credibility signal.

Full report with sector breakdown, failure-mode analysis, and proposed
fixes: [docs/backtest_2014_2024.md](docs/backtest_2014_2024.md).

---

## Architecture

```
openquant/
├── api/
│   └── main.py                 ← FastAPI /analyse endpoint
├── core/                       ← Pure-Python finance. Zero web deps. 161 tests.
│   ├── data.py                 ← SEC EDGAR + yfinance + cache
│   ├── fcf.py                  ← FCF formula + projection (H3b)
│   ├── wacc.py                 ← β, CAPM, Hamada, WACC (H2c + H3a)
│   ├── dcf.py                  ← Forward DCF, terminal value, NPV, IRR, PVTS (H3b + H3+)
│   ├── reverse_dcf.py          ← Solves: g | IV(g) = market_price
│   ├── sensitivity.py          ← Growth × WACC grid
│   ├── multiples.py            ← P/E, EV/EBITDA, FCF yield
│   ├── suitability.py          ← 8-check DCF gate
│   ├── assumption_diagnostic.py  ← 8-dimension risk scoring
│   ├── red_flags.py            ← Warning aggregator
│   ├── audit_trail.py          ← Reproducible formula trace
│   └── utils.py                ← log returns, Sharpe, capital gain rate,
│                                   min-variance 2-asset weight (used by EPFL Exam 2)
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
├── tests/                      ← 161 tests. EPFL exam answers as ground truth.
│   ├── test_epfl_exam1.py      ← 23 tests, Sample Exam 1 problems 2-3
│   ├── test_epfl_exam2.py      ← 21 tests, Sample Exam 2 problems 2-5
│   ├── test_regression_fixes.py  ← Tests guarding the round 1-4 review fixes
│   ├── test_dcf.py / test_fcf.py / test_utils.py / test_data.py
│   └── conftest.py             ← Ground-truth fixtures (Exam 1 P2, EPFL_H2)
└── docs/
    ├── backtest_plan.md            ← Scope doc
    ├── backtest_2014_2024.md       ← Honest calibration report
    ├── phase1_tsla_sketch.md       ← Original UI sketch
    ├── phase1_tsla_sketch_v3.md    ← v3 UI design (the one shipped)
    └── blog_draft.md               ← Companion blog post
```

**Dependency rule:** `core/` imports nothing from `api/` or `frontend/`.
Tests import `core/` only. The math layer can be verified without
running the web stack.

---

## Test fixtures — EPFL exam ground truth

Every implemented formula is pinned to a published EPFL Sample Exam
answer. Example tests:

```python
# tests/test_epfl_exam1.py — TestExam1Problem2_HamadaCAPM
# EPFL Final Exam 1, Problem 2-Q2:
#   Firm A: βE = 1.99, D/V = 33%  →  βU = 1.50
#   Firm B: βE = 2.48, D/V = 50%  →  βU = 1.50
#   Average βU = 1.50
#   rU = 8% + 1.50 × 8% = 20%   ✓

# tests/test_epfl_exam1.py — TestExam1Problem3_NPV_IRR
# Hungry Enterprises projects (mutually exclusive):
#   Project A: NPV@15% = $852.55,  IRR = 28.2%   ✓
#   Project B: NPV@15% = $7,296.79, IRR = 20.7%   ✓
#   Incremental IRR(B−A) = 20.289%               ✓
```

If the test passes, the math matches Professor Morellec's grading key.
If it fails, our implementation is wrong — period.

---

## Limitations (honest disclosure)

DCF on individual stocks has fundamental limits this tool inherits:

1. **No demonstrated predictive power** — backtest R² = 0.04. We don't
   claim what we can't prove.
2. **Forecast risk** — any projection beyond year 3 is largely guesswork.
3. **Terminal value dominance** — 50-70% of enterprise value comes from
   the post-year-10 period, which we can't observe.
4. **β instability** — equity beta drifts; Hamada unlevering partly
   addresses this.
5. **Survivorship bias** — backtest universe tilts toward survivors.
6. **Regime sensitivity** — same model, different macro regime,
   different verdict. We hard-code per-period macro inputs for that
   reason.

These are the limits every DCF tool has, including Bloomberg's. The
difference is we say so out loud.

---

## Built on

- [SEC EDGAR](https://www.sec.gov/edgar/sec-api-documentation) — XBRL filings (free, unlimited)
- [yfinance](https://github.com/ranaroussi/yfinance) — daily prices
- [Damodaran NYU](https://pages.stern.nyu.edu/~adamodar/) — historical macro snapshots
- FastAPI + React + Recharts + scipy + pandas

Inspired by Aswath Damodaran's open spreadsheets — same philosophy
(*show your work, admit your limits*), automated and tested.

---

## License & contribution

MIT licensed. PRs are welcome but the project is **deliberately
scope-constrained** to equity valuation taught in EPFL Principles of
Finance. Out-of-scope contributions (bond pricing, derivatives,
portfolio optimisation, AI predictions) will be declined.

**The highest-priority issue** is any case where our output disagrees
with an EPFL Sample Exam answer key. Open it as a bug.

---

## Citation

If this helped you, a star is appreciated. For academic citation:

```
OpenQuant: a transparent companion to EPFL Principles of Finance.
github.com/A-bv/openquant, 2025.
```

---

*OpenQuant — academic equity valuation applied to real markets.
Every formula traceable. Every prediction backtested. Honest about both.*
