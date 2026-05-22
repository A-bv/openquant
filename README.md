# OpenQuant

**Transparent educational investment analysis. Every formula. Real data. Free.**

> OpenQuant does not tell you what a company is worth.  
> It tells you what assumptions are required for the current price to make sense.

---

## What it is

OpenQuant is a free, open-source investment analysis tool that applies the exact methodology used by professional analysts — DCF valuation, WACC, CAPM, covariance matrix, portfolio construction — to real company data, with every formula shown and every limitation honestly disclosed.

Built on the theory taught in university finance courses (EPFL Introduction to Finance). Every formula is traceable to the academic source. Every output comes with an honest assessment of how much to trust it.

**Two modules:**
- **Company Valuation** — reverse DCF showing what the market currently believes about a company's future
- **Portfolio Construction** — covariance matrix (DCD'), efficient frontier, five portfolio comparisons

---

## Quickstart

```bash
git clone https://github.com/a-bv/openquant
cd openquant
pip install -r requirements.txt
streamlit run app.py
```

Works immediately for US-listed companies — no API key required.  
SEC EDGAR provides financial statements free and unlimited.

**Optional:** Get a free [Financial Modeling Prep API key](https://financialmodelingprep.com/developer/docs) for enhanced data quality. Enter it in the sidebar.

---

## The gap this fills

| Tool | Problem |
|------|---------|
| Bloomberg | $24,000/year. Black box. No explanations. |
| Simply Wall St | Black box. No formulas shown. |
| PyPortfolioOpt | No UI. No valuation. Library only. |
| OpenBB | Practitioner terminal. Not educational. |
| ChatGPT / Claude | Reasons about finance. Cannot automate reproducibly. |

OpenQuant combines full WACC construction + reverse DCF + Assumption Diagnostic + portfolio construction in one free tool. That combination does not exist anywhere else.

---

## Module 1 — Company Valuation

Enter a ticker. The tool runs a complete professional valuation:

```
Suitability check (is DCF appropriate for this company?)
        ↓
Free Cash Flow computation — EBIT(1-T) + D&A − CapEx − ΔNWC
        ↓
Beta estimation — Cov(r,rm)/Var(rm), rolling 90-day, Newey-West SE
        ↓
Cost of equity — CAPM: rf + β(rm−rf)
        ↓
WACC — (E/V)×rE + (D/V)×rD×(1−T)
        ↓
Assumption Diagnostic — 8 dimensions, shown before any numbers
        ↓
Forward DCF — 3 scenarios, 10-year horizon
        ↓
Sensitivity analysis — growth × WACC grid
        ↓
Reverse DCF — what FCF growth does the current price imply?
        ↓
Multiples context — EV/EBITDA, P/E, FCF yield
        ↓
Buffett's 3 qualitative questions
        ↓
Model audit trail — every assumption, every formula, every warning
```

### Why reverse DCF is the primary output

Most DCF tools ask: *"What is this company worth?"*  
That question requires predicting the future — which nobody can do reliably.

OpenQuant asks instead: *"What does the current stock price imply about the company's future?"*

This reframing — used by Warren Buffett — turns an impossible prediction problem into a judgment problem. You don't need to know the future. You only need to judge whether the market's implicit bet is reasonable.

---

## Module 2 — Portfolio Construction

Enter tickers and weights. The tool computes:

- **Covariance matrix** — V = D × C × D' (EPFL formula sheet)
- **Portfolio variance** — σ²_p = w · V · w'
- **Five portfolio comparisons** ordered by robustness:

| Portfolio | Uses correlations | Uses expected returns | Robustness |
|-----------|:-----------------:|:---------------------:|:----------:|
| Current (your weights) | Yes | No | Reference |
| Equal weight | No | No | ★★★★★ Highest |
| Inverse-volatility | No | No | ★★★★☆ High |
| **Minimum variance** | **Yes** | **No** | **★★★★☆ High — primary** |
| Max Sharpe | Yes | Yes | ★★☆☆☆ Least reliable |

**Minimum variance** is promoted as the primary robust alternative because it uses only the covariance matrix — no expected return estimates required. Expected return estimates from historical data are noisy; small changes produce dramatically different "optimal" weights.

---

## What makes it different

### 1. Assumption Diagnostic shown before results

8 dimensions scored before you see a single number:

| Dimension | What it measures |
|-----------|-----------------|
| FCF Stability | Consistently positive and predictable? |
| FCF Margin Stability | Margins stable or swinging? |
| Revenue Cyclicality | Smooth or highly volatile? |
| Terminal Value Dominance | % of EV from terminal value |
| Beta Reliability | Rolling beta stable enough to trust WACC? |
| Data Completeness | All fields available and consistent? |
| Growth Reasonableness | Implied growth plausible vs history and GDP? |
| Reinvestment Support | Does capex + ΔNWC support implied FCF growth? |

Severity-weighted: 0 = no issue, 1 = mild, 2 = severe. 4+ total = Red.

**Disclaimer always shown:** *"A Green rating means assumptions appear internally consistent — not that the valuation is reliable. All DCF valuations carry fundamental uncertainty about the future."*

### 2. Every formula traceable to its source

Every formula links to the EPFL course materials:
- Beta: `β = Cov(r,rm) / Var(rm)` — EPFL Formula Sheet
- CAPM: `E(R) = rf + β(rm−rf)` — EPFL Formula Sheet  
- WACC: `(E/V)×rE + (D/V)×rD×(1−T)` — EPFL Formula Sheet
- Terminal Value: `TV = FCF_n×(1+g)/(WACC−g)` — Growing Perpetuity
- Portfolio Variance: `σ²_p = w·V·w'` — EPFL Formula Sheet

Toggle **"Show formulas"** in the sidebar to see them inline.

### 3. Honest about limitations

12 limitations disclosed prominently — not in footnotes:

- **Survivorship bias** — free data excludes delisted companies
- **Terminal value dominance** — 60-80% of value from least reliable assumption
- **Cost of debt approximation** — historical effective rate, not current marginal cost
- **Backward-looking inputs** — beta and growth from history
- **Expected return estimation error** — efficient frontier weights are sensitive to noisy inputs
- **DCF suitability** — only works for FCF-positive stable companies (suitability checker enforces this)
- And 6 more — see the full list in the app

---

## Case studies

### Apple (AAPL) — stable FCF company
Suitability: ✅ Green. Consistent positive FCF, stable margins, 5+ years of data.  
Expect: Full valuation with all 8 diagnostic dimensions likely Green or Amber.

### Tesla (TSLA) — high-growth warning
Suitability: ⚠️ Amber/Red depending on FCF history.  
Reverse DCF will likely show: market implies very high growth vs historical FCF.

### JPMorgan (JPM) — financial company
Suitability: 🚫 Red. *"DCF not recommended for financial companies. Banks require different valuation methodology."*  
Alternatives shown: P/B ratio, ROE analysis, Dividend Discount Model.

### Pre-revenue startup — no FCF history
Suitability: 🚫 Red. *"Insufficient positive FCF history."*  
Alternatives: EV/Revenue, comparable transactions.

### AAPL + MSFT + XOM + BND — portfolio demo
Portfolio module: full DCD' matrix, 5 comparisons, efficient frontier, risk decomposition.

---

## Architecture

```
openquant/
├── core/                  ← Pure Python. Zero Streamlit. 183 tests.
│   ├── data.py            ← SEC EDGAR + yfinance + cache
│   ├── suitability.py     ← 8-check DCF gate
│   ├── fcf.py             ← FCF computation and projections
│   ├── wacc.py            ← Beta, CAPM, cost of debt, WACC
│   ├── dcf.py             ← Forward DCF, terminal value
│   ├── reverse_dcf.py     ← Primary output: implied growth solver
│   ├── sensitivity.py     ← Growth × WACC sensitivity tables
│   ├── assumption_diagnostic.py  ← 8-dimension diagnostic
│   ├── red_flags.py       ← Top-of-page flag generator
│   ├── multiples.py       ← EV/EBITDA, P/E, FCF yield
│   ├── audit_trail.py     ← Reproducible model audit
│   └── portfolio.py       ← DCD' matrix, frontier, 5 comparisons
├── ui/                    ← Streamlit only. Calls core/. No math.
│   ├── components/        ← Charts, metrics, sidebar, formulas
│   └── state.py           ← Session state schema
├── pages/
│   ├── 1_Valuation.py     ← Company valuation flow
│   └── 2_Portfolio.py     ← Portfolio construction
├── tests/                 ← 183 tests. EPFL exam numbers as fixtures.
├── app.py                 ← Entry point
└── config.py              ← All constants. Zero magic numbers.
```

**Dependency rule:** `core/` imports nothing from the project. `ui/` imports `core/` and Streamlit. Tests import `core/` only — never UI. This means the entire math layer can be tested without Streamlit installed.

---

## Test fixtures — EPFL exam ground truth

The math is verified against the professor's own numbers:

```python
# EPFL Exam 1, Problem 2
# β=1.50, rf=8%, MRP=8% → E(RU) = 8% + 1.50×8% = 20.0% ✓
# NPV at 20% discount rate = 2,939,236 ✓

# EPFL_H2_exemple_Portfolio_volatility.xlsx
# Portfolio SD = 0.050794 at w=[0, 0.5, 0.5] ✓
# Cov(NorthAir, WestAir) correlation = 0.62 ✓
```

If the code passes these tests, the math is correct.

---

## Data sources

| Source | Data | Cost | Limit |
|--------|------|------|-------|
| **SEC EDGAR** | Financial statements | Free | Unlimited |
| yfinance | Daily prices for beta | Free | Unofficial |
| Damodaran (NYU) | Industry benchmarks | Free | Static |
| Local CSV cache | All fetched data | Free | Unlimited |
| FMP (optional) | Enhanced financials | Free tier | 250/day |

All analysis runs without any API key. US companies only in v1.  
International coverage planned for v2 — [open an issue](https://github.com/a-bv/openquant/issues) if you need it.

---

## Known limitations

This project is honest about what it cannot do:

1. **Survivorship bias** — free APIs exclude delisted companies. Risk metrics may be understated.
2. **Terminal value dominance** — 60-80% of valuation driven by the least certain assumption.
3. **Backward-looking** — all inputs computed from historical data. Past ≠ future.
4. **DCF suitability** — inappropriate for banks, insurers, pre-revenue companies.
5. **Cost of debt** — historical effective rate, not current marginal cost.
6. **Markowitz is fragile** — efficient frontier weights highly sensitive to return estimates.
7. **Not financial advice** — educational outputs of mathematical models only.

These limitations exist in Bloomberg, Simply Wall St, and every other valuation tool.  
The difference is we tell you.

---

## Contributing

OpenQuant is open source. Contributions welcome.

**Planned for v2:**
- International company support (FMP API)
- True risk parity (equal risk contribution)
- Black-Litterman return estimation
- Sector delisting rate context (SEC EDGAR public filings)

---

## Origin

Built on EPFL Introduction to Finance coursework — the formulas in the app are the same ones taught in the course. The Excel VBA prototypes that preceded this project are preserved in the repository history.

The project exists because there is a gap between learning finance theory and being able to apply it to real data. This is the tool that should have existed during the course.

---

*OpenQuant: Transparent educational investment analysis. Every formula. Real data. Free.*  
*Not a Bloomberg replacement. Not financial advice. Honest about what the math can and cannot do.*
