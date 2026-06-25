# OpenQuant — Historical backtest plan

> Scope and design for the walk-forward validation that closes §9 of the
> Phase 1 sketch. This is what turns "validated against academic answer keys"
> into "validated against actual market outcomes."

---

## Why this is the highest-leverage thing to build

Today the page says: *"The model is correct per EPFL. We haven't yet shown
its predictions match reality."*

That's a confession every other DCF tool quietly avoids. Closing it gives
OpenQuant something genuinely unique: **a free retail tool whose predictions
have been calibrated against 10 years of US equity history, with the
calibration figures shown to the user.**

The work is meaningful but bounded — ~3-5 focused days. Below is the design.

---

## 1. Ticker universe

**Pick 50 S&P 500 stocks** balanced across:

| Dimension | Buckets |
|---|---|
| Size | 10 mega-cap (>$500B), 20 large-cap ($100B–500B), 20 mid-cap ($10B–100B) |
| Sector | 8 sectors × ~6 stocks each (Tech, Health, Financials, Cons. Disc, Cons. Staples, Industrials, Energy, Utilities) |
| Growth profile | 25 growth (rev CAGR ≥ 10% historically), 25 value (rev CAGR < 10%) |
| Quality | Mix of high-margin and low-margin businesses |

**Survivorship correction.** Pick the universe **as of January 2014** — companies that existed then, not today's S&P. This avoids survivorship bias (e.g., not picking only companies that survived 10 years).

**Excluded from start:**
- Financials with deposit-driven balance sheets (DCF inappropriate)
- REITs (different cash-flow definition)
- Companies that IPO'd after 2010 (insufficient pre-period history)

The 50 names are implemented in `backtest/universe.py`.

---

## 2. Time setup

| Decision | Choice |
|---|---|
| "As of" snapshot date | **January 31, 2014** — uses only filings available by then |
| Forecast horizon under test | 10-year realized return through January 31, 2024 |
| Walk-forward variant | Single point-in-time for v1; rolling annual snapshots optional for v2 |
| Total return definition | Price + dividends (TSR), annualised |

Why 2014? Far enough back to test the 10-year horizon (which the model uses);
recent enough that EDGAR coverage is reliable and macro conditions
aren't ancient history.

---

## 3. Historical data — the hard problem

### Financial statements
EDGAR's `companyconcept` API returns *all* historical filings. We filter to
"reported on or before Jan 31, 2014." This gives us point-in-time
financials — what an investor would have seen then.

**Concern:** EDGAR restatements. Filings restated after 2014 might overwrite
the 2014-era numbers. Mitigation: use the `accn` (accession number) and
`filed` date fields to pick the *first* filing of each fiscal year, not
the latest revision.

### Prices
yfinance covers historical data. Pull adjusted closes from 2009-01-01
(5-yr lookback for β) through 2024-01-31.

### Macro inputs (period-appropriate, NOT current)
This is critical. We currently use 4.5% risk-free rate. In January 2014
the 10-yr Treasury yielded **2.8%**.

| Input | Jan 2014 value | Source |
|---|---:|---|
| Risk-free rate | 2.80% | FRED `DGS10` |
| Market risk premium | 6.0% | Damodaran's "implied ERP" history |
| Terminal growth | 2.5% | Same default (no reason to change) |

If we use today's inputs for a 2014 valuation, we systematically
under-discount and over-value. Period-appropriate macro is non-negotiable.

---

## 4. What we record for each stock

For each of the 50 names, "as of" January 2014, run the full OpenQuant
pipeline and record:

| Field | Type | What it captures |
|---|---|---|
| `ticker` | string | |
| `as_of_date` | date | Jan 31, 2014 |
| `model_iv_conservative` | float | $/share |
| `model_iv_base` | float | $/share |
| `model_iv_optimistic` | float | $/share |
| `market_price_as_of` | float | $/share |
| `model_verdict` | enum | overvalued / fairly priced / undervalued (vs base case ±10%) |
| `suitability_rating` | enum | green / amber / red |
| `reverse_dcf_implied_growth` | float | %/yr |
| `historical_median_growth` | float | %/yr at time of analysis |
| `realized_10yr_tsr` | float | actual %/yr from Jan 2014 → Jan 2024 |
| `realized_10yr_fcf_growth` | float | actual %/yr |
| `survived` | bool | did the company still exist as a public stock in 2024 |
| `failure_mode` | string | acquisition / bankruptcy / delisting / merger |

**Output:** `backtest/results/backtest_2014_2024.csv` — single row per ticker.

---

## 5. Metrics — how we judge the model

### Verdict accuracy (binary)
- Of stocks the model said were **overvalued** (IV base case < market price by 20%+),
  what fraction had realized TSR below the S&P 500?
- Of stocks the model said were **undervalued** (IV base case > market price by 20%+),
  what fraction outperformed the S&P 500?
- Of stocks the model said were **fairly priced** (within ±20% of market),
  what was the average TSR vs market?

### Calibration (continuous)
- Plot model's predicted "upside %" (IV / price - 1) on x-axis
- Realised 10-yr TSR on y-axis
- A well-calibrated model has positive slope. A useless model is a horizontal line.
- Report: slope, R², and whether the regression is significant.

### Suitability check
- Did AMBER/RED suitability ratings actually correlate with larger model
  errors? If our model self-flags as unreliable for the same stocks where
  it later turns out to be wrong, the suitability check works.
- If green-rated stocks have similar error distributions to amber-rated, the
  suitability check is decoration.

### Failure-mode analysis
- Where does the model systematically fail? Tech? Energy? Mega-caps?
- For each sector, compute mean absolute error in predicted vs realized
  fair value.

---

## 6. Product output

The backtest should produce implemented artifacts, not a long interpretive
Markdown report:

- raw historical results in `backtest/results/backtest_2014_2024.csv`
- machine-readable summary in `backtest/results/calibration_summary.json`
- automated tests locking the main metrics
- a concise reliability panel in the app

The product should show only the main result. If the result is weak, it still
appears in the product because hiding failure is worse than showing it.

---

## 7. Engineering notes

### Pipeline
```python
# pseudocode
for ticker in UNIVERSE:
    statements = edgar.fetch_as_of(ticker, AS_OF_DATE)
    prices = yfinance.history(ticker, AS_OF_DATE - 5yr, AS_OF_DATE)
    macro = HISTORICAL_MACRO[AS_OF_DATE]
    
    model_output = analyse(statements, prices, macro)
    
    realized_prices = yfinance.history(ticker, AS_OF_DATE, AS_OF_DATE + 10yr)
    realized_fcf = edgar.fetch_period(ticker, AS_OF_DATE, AS_OF_DATE + 10yr)
    
    record_row(model_output, realized_prices, realized_fcf)
```

### Caching
Each stock's EDGAR fetch can be slow (~1-2s). Cache the raw responses to disk.
50 stocks × ~5 EDGAR endpoints × ~2 seconds = ~10 minutes from cold. Worth
caching aggressively.

### Reproducibility
The backtest must be deterministic. No random sampling, no time-varying
external state. Anyone can rerun the script and get identical numbers.
Output the universe selection AND the raw inputs to disk so the analysis
is reproducible from raw data.

### Honest reporting
- **No cherry-picking.** Report all 50 stocks. Don't filter to make the
  numbers look better.
- **No survivorship correction.** If a company went bankrupt and lost 100%,
  that's a real outcome and counts as a -100% realized return.
- **Confidence intervals.** Bootstrap CIs on the headline numbers. With N=50
  the error bars are wide; show them.

---

## 8. Effort estimate

| Day | Work |
|---|---|
| 1 | Universe selection + data pipeline (EDGAR `as_of` filtering, yfinance historical, macro snapshots) |
| 2 | Run pipeline on all 50 tickers, save raw data, hand-spot-check 3 stocks for correctness |
| 3 | Compute metrics, write `backtest/results/backtest_2014_2024.csv`, produce `calibration_summary.json` |
| 4 | Add automated tests for the headline metrics |
| 5 | Wire the headline into the per-ticker reliability panel |

Total: **5 focused days**.

---

## 9. What could go wrong

Honest pre-mortem:

| Risk | Probability | Mitigation |
|---|---|---|
| EDGAR's `as_of_date` filtering misses restatements and gives lookahead data | Medium | Use `accn` + `filed` date, not period-end date; spot-check 5 stocks manually |
| Model produces nonsensical IVs in 2014 because we miss period-appropriate macro | High | Hard-code period-appropriate `rf`, `mrp`; document explicitly |
| 10-year horizon includes one regime shift (2014-2024 covers COVID) that's atypical | Inherent | Use multiple "as of" dates (2010, 2014, 2018) in v2 to triangulate |
| Realized TSR is unfair benchmark — depends on entry timing, taxes, etc. | Inherent | Report TSR consistently; note caveat in interpretive report |
| Calibration plot looks bad (model is mostly wrong) | Possible | **This is fine.** Honest negative results are still results. Better to know. |

The last row is the important one. **The backtest must be allowed to fail.**
If the model turns out to be poorly calibrated, that's information OpenQuant
needs to absorb — either by improving the model or by being honest about its
limits. Either way, the product is more credible after the backtest than
before.

---

## 10. Next step

Awaiting green-light on:
1. **Universe size.** 50 stocks is reasonable but defensible vs 30 or 100?
2. **Time period.** 2014-2024 is the chosen window; backup is 2010-2020 (avoids COVID).
3. **Macro inputs.** Period-appropriate (FRED) — confirm this is required, not nice-to-have.

Once those three are confirmed, day 1 (universe selection + data pipeline)
can start.
