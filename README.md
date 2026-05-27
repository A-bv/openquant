# OpenQuant

> **The corporate finance textbook, made interactive — and tested against reality.**

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-161%20passing-brightgreen.svg)]()
[![Textbook problems verified](https://img.shields.io/badge/textbook%20problems%20verified-44-blue.svg)](tests/test_epfl_exam1.py)
[![Backtest](https://img.shields.io/badge/backtest-published-yellow.svg)](docs/backtest_2014_2024.md)

---

Every finance student learns to value a company by hand: forecast cash flows,
compute WACC, build the DCF, solve the reverse. The method lives in **Berk
and DeMarzo's *Corporate Finance*** (Pearson, 2nd ed.), chapters 7 through 15.

But the textbook stops there. It never tells you whether the method
actually works on real stocks — and the professional tools that apply it
(Bloomberg, FactSet) are black boxes that won't show their work.

**OpenQuant fills that gap.**

It applies the exact textbook method to any US-listed stock, shows every
formula along the way, and lets you change any assumption live. Then it
does something no commercial tool does: **it ran itself on 50 real stocks
from 2014 to 2024 and openly published the results — including, especially,
the parts where the textbook method gets it wrong.**

*Theory you can verify. Predictions you can audit. A track record you can
challenge.*

---

## Demo

```bash
git clone https://github.com/A-bv/openquant
cd openquant
pip install -r requirements.txt

# Backend
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000

# Frontend (in another terminal)
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

## What makes it different

OpenQuant does three things no other tool does, in one place.

### 1. Live textbook
Berk-DeMarzo's valuation method, applied formula by formula to any US
stock. Each line on the page is traceable to a chapter — and to a
worked problem from the textbook's sample exams that proves we
implemented it correctly.

### 2. Self-evaluation
We didn't just compute. We applied the method to 50 real stocks in
2014 and compared what it said to what actually happened by 2024.
**R² = 0.04. Honest.** No retail tool publishes their track record.
We make ours the centerpiece.

### 3. A first in finance education
For the first time, a textbook's full valuation methodology is
systematically applied to the real market — with the model's track
record published, including its failures. Use it to learn. Use it to
test the theory. Use it to argue with our numbers.

---

## What you see when you analyse a stock

Section by section, in narrative order:

| What you see | What it tells you | Textbook chapter |
|---|---|:---:|
| **Hero verdict** in plain English | "Tesla at $426 is overvalued under our model — even the optimistic scenario implies $122." | — |
| **Confidence scorecard** (5 dots) | Value, implied growth, FCF track record, balance sheet, DCF suitability — green/amber/red. | — |
| **Honest disclosure banner** | "Math correctly implements the textbook (161 tests pass). Predictions on 50 real stocks 2014-2024 explain only 4% of realized returns (R² = 0.04). Read knowing this." | — |
| **What is the market's bet?** | The reverse DCF: at today's price, what FCF growth must the company deliver for the next 10 years? Compared to its historical median, mean, revenue CAGR, and GDP. | Ch. 9 |
| **Three scenarios** | Conservative / Base / Optimistic intrinsic value per share, each with growth rate and terminal value share. | Ch. 9 |
| **Try your own assumptions** | Three sliders (FCF growth, WACC, terminal growth). The intrinsic value recomputes live — you don't have to believe our β or our hurdle rate. | Ch. 9, 12 |
| **Why might X be worth buying anyway?** | Four cards naming exactly which assumptions you'd need to hold for the verdict to be wrong. | — |
| **Sanity check — multiples** | P/E, EV/EBITDA, FCF yield vs sector / S&P / Treasury benchmarks. | — |
| **Free cash flow history** | 10-year bar chart of actual FCF. Red bars = negative years. | Ch. 7 |
| **Sensitivity heatmap** | Intrinsic value at every combination of growth × WACC. | Ch. 9 |
| **Show your work — WACC** | Risk-free rate → β → market risk premium → cost of equity (CAPM) → cost of debt (after-tax) → WACC. Every line cited. | Ch. 12, 15 |

Every jargon term has a hover-tooltip. Every formula has a textbook
citation badge.

---

## What the tool does NOT do (by design)

OpenQuant covers the **equity-valuation** half of the textbook's
material. The other half — bonds, derivatives, full portfolio
optimisation — is **deliberately out of scope.** Here's the full map:

| Textbook chapter | Topic | In OpenQuant? |
|---|---|:---:|
| Ch. 3-4 | TVM — PV/FV, perpetuity, annuity, growing annuity | ✅ |
| Ch. 6 | Bond pricing & YTM | ❌ Out of scope |
| Ch. 8 | Rate conversions, spot/forward rates, duration | ❌ Out of scope |
| Ch. 10 | Stats — mean, variance, covariance, correlation | ✅ |
| Ch. 11 | Portfolio theory — variance, min-variance, efficient frontier | 🟡 Closed-form 2-asset weight only |
| Ch. 12 | CAPM, beta, idiosyncratic variance, Sharpe | ✅ |
| Ch. 14, 15 | WACC, Hamada unlevering, MM I/II | ✅ |
| Ch. 7, 8, 9 | FCF formula, DCF, NPV vs IRR, terminal value | ✅ |
| Ch. 15 | APV, PV of Tax Shield (PVTS) | 🟡 PVTS helper only |
| Ch. 15 | Bankruptcy costs (PVBC, default probabilities) | ❌ Out of scope |
| Ch. 20-22 | Options, put-call parity, binomial, Black-Scholes | ❌ Out of scope |

**Honest tally:** about half of the textbook's material is in the code,
roughly a third reaches the UI. The half we cover (equity valuation) is
covered comprehensively. The other half is **explicitly excluded** so
we can be excellent at one thing rather than mediocre at everything.

---

## Why this is different

There are dozens of free DCF calculators on the internet. None of them
combine all four of these:

| | OpenQuant | Typical DCF tool | Bloomberg | Simply Wall St |
|---|:---:|:---:|:---:|:---:|
| Every formula visible | ✅ | ❌ | ❌ | ❌ |
| Every formula cited to a textbook chapter | ✅ | ❌ | ❌ | ❌ |
| Unit-tested against textbook sample-exam answers | ✅ | ❌ | ❌ | ❌ |
| Reverse DCF as the centerpiece | ✅ | ❌ | ❌ | 🟡 |
| Live interactive assumption sliders | ✅ | 🟡 | ✅ | ❌ |
| **Published backtest of the tool's own predictions** | ✅ | ❌ | ❌ | ❌ |
| Open source, free, no account | ✅ | varies | $24K/yr | freemium |

The unique row is the bottom-second. Every other tool that gives you a
"fair value" has a track record. None of them publish it. We do —
even when it isn't flattering.

This isn't a Bloomberg competitor. It's a **different lens** on the
same question, more transparent and more pedagogical.

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

**Calibration regression: `R² = 0.04`, slope ≈ 0.**

In plain English: the model's verdicts barely predict realized returns.
The "undervalued" basket matched the index. The "overvalued" basket
slightly outperformed it. **As a stock picker, this model is essentially
a coin flip.**

We publish this because **a transparent tool that admits its limits is
more useful than a black box that doesn't**. The math is correct; the
predictive power isn't there yet. Tractable, documented root causes
(growth cap, terminal-value dominance, regime sensitivity) and concrete
next steps are in the full report:

[`docs/backtest_2014_2024.md`](docs/backtest_2014_2024.md)

---

## Architecture

```
openquant/
├── api/main.py                 ← FastAPI /analyse endpoint
├── core/                       ← Pure-Python finance. Zero web deps. 161 tests.
│   ├── data.py                 ← SEC EDGAR + yfinance + cache
│   ├── fcf.py                  ← FCF formula + projection (Ch. 7)
│   ├── wacc.py                 ← β, CAPM, Hamada, WACC (Ch. 12, 14, 15)
│   ├── dcf.py                  ← DCF, terminal value, NPV, IRR, PVTS (Ch. 7-9, 15)
│   ├── reverse_dcf.py          ← Solves: g | IV(g) = market_price
│   ├── sensitivity.py          ← Growth × WACC grid
│   ├── multiples.py            ← P/E, EV/EBITDA, FCF yield
│   ├── suitability.py          ← 8-check DCF gate
│   ├── assumption_diagnostic.py  ← 8-dimension risk scoring
│   ├── red_flags.py            ← Warning aggregator
│   ├── audit_trail.py          ← Reproducible formula trace
│   └── utils.py                ← log returns, Sharpe, capital gain rate
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
│       ├── App.jsx             ← Verdict → reverse DCF → sliders → math
│       └── components/         ← Hero, scorecard, sliders, calibration, charts
├── tests/                      ← 161 tests. Textbook exam answers as ground truth.
│   ├── test_epfl_exam1.py      ← 23 tests, sample exam 1 problems 2-3
│   ├── test_epfl_exam2.py      ← 21 tests, sample exam 2 problems 2-5
│   ├── test_regression_fixes.py  ← Guards round 1-4 review fixes
│   ├── test_dcf.py / test_fcf.py / test_utils.py / test_data.py
│   └── conftest.py             ← Ground-truth fixtures
└── docs/
    ├── backtest_plan.md            ← Scope doc
    ├── backtest_2014_2024.md       ← Honest calibration report
    ├── phase1_tsla_sketch_v3.md    ← v3 UI design
    └── blog_draft.md               ← Companion blog post
```

**Dependency rule:** `core/` imports nothing from `api/` or `frontend/`.
Tests import `core/` only. The math layer can be verified without
running the web stack.

---

## Test fixtures — textbook exam ground truth

Every implemented formula is pinned to a published sample-exam answer
key for Berk-DeMarzo *Corporate Finance*. Two examples:

```python
# tests/test_epfl_exam1.py — TestExam1Problem2_HamadaCAPM
# Two comparable firms:
#   Firm A: βE = 1.99, D/V = 33%  →  βU = 1.50
#   Firm B: βE = 2.48, D/V = 50%  →  βU = 1.50
#   Average βU = 1.50
#   rU = 8% + 1.50 × 8% = 20%  ✓ (textbook answer)

# tests/test_epfl_exam1.py — TestExam1Problem3_NPV_IRR
# Hungry Enterprises projects (mutually exclusive):
#   Project A: NPV@15% = $852.55,  IRR = 28.2%   ✓
#   Project B: NPV@15% = $7,296.79, IRR = 20.7%  ✓
#   Incremental IRR(B−A) = 20.289%               ✓
```

If a test passes, our implementation matches the textbook's worked
solution. If it fails, our code is wrong — period.

---

## Limitations (honest disclosure)

DCF on individual stocks has fundamental limits this tool inherits:

1. **No demonstrated predictive power.** Backtest R² = 0.04. We don't
   claim what we can't prove.
2. **Forecast risk.** Any projection beyond year 3 is largely guesswork.
3. **Terminal value dominance.** 50-70% of enterprise value comes from
   the post-year-10 period, which can't be observed.
4. **β instability.** Equity beta drifts; Hamada unlevering partly
   addresses this.
5. **Survivorship bias.** Backtest universe tilts toward survivors.
6. **Regime sensitivity.** Same model, different macro regime, different
   verdict. We hard-code per-period macro inputs to mitigate this.

These are limits every DCF tool inherits, including Bloomberg's.
The difference is we say so out loud.

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
scope-constrained** to equity valuation as taught in Berk-DeMarzo
*Corporate Finance*. Out-of-scope contributions (bond pricing,
derivatives, portfolio optimisation, AI predictions) will be declined.

**The highest-priority issue** is any case where our output disagrees
with a textbook worked-problem answer. Open it as a bug.

---

## Citation

```
OpenQuant: an interactive companion to Berk-DeMarzo Corporate Finance.
github.com/A-bv/openquant, 2025.
```

---

*Theory. Reality. You decide.*
