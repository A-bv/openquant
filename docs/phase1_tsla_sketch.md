# OpenQuant — Phase 1 redesign (TSLA) — v2

> Rebuilt with three changes: tighter narrative arc (verdict first, math at the
> end), visual scorecard at the top (Simply Wall St-inspired), Buffett demoted
> to a single footer note. Visual elements are described in `[brackets]` for the
> React translation later.

---

# 🚗  Tesla, Inc. (TSLA)

**Motor Vehicles & Passenger Car Bodies · NASDAQ · Last updated 2025-11-24**

---

## 1. Should you buy Tesla at $426?

> ### Probably not, at this price.
> Under the academic DCF model (EPFL Principles of Finance), Tesla's
> intrinsic value is **$108 per share** — **74% below today's market price**.
> Even the most optimistic scenario gives $122.

**`[Visual: price gauge]`**
```
                            You are here
                                  ▼
$0 ─────●─────●─────●─────────────●──────────
       $96   $108  $122          $426
       conservative  optimistic  market
                base
```

### Confidence scorecard

`[Visual: 5 dots in a horizontal row, colored green/amber/red, with labels below]`

| Dimension | Rating | Why |
|---|:---:|---|
| **Value** vs intrinsic value | 🔴 | Trading 74% above the model's base case |
| **Growth needed** to justify price | 🟡 | Market implies 57%/yr — slightly below Tesla's own historical 62% |
| **Track record** of cash flow | 🟡 | Positive in 7 of last 10 years; volatile |
| **Balance sheet** strength | 🟢 | Net cash position ($10B more cash than debt) |
| **DCF suitability** | 🟡 | Three negative-FCF years make the model less reliable |

---

## 2. The question that matters — what does today's price assume?

This is OpenQuant's central question. Instead of asking *"what is Tesla worth?"*
we run the math backwards: **"What future growth rate would Tesla need to
deliver for $426 to be the right price?"**

### The market's implied bet

`[Visual: horizontal bar chart, large numeric callouts]`

```
                                          historical FCF growth: 62%/yr ⌐
Market-implied growth   ████████████████░░░░  57.5%/yr                   │
Tesla's actual median   █████████████████░░░  62.3%/yr  ← past 10 years ─┘
Revenue CAGR            ███████████░░░░░░░░░  33.6%/yr  ← steadier anchor
GDP (long run)          █░░░░░░░░░░░░░░░░░░░   3.0%/yr  ← reality check
```

**Read this:** the market is pricing Tesla as if it will grow free cash flow at
**57% per year for ten consecutive years**. That's actually *slightly below*
Tesla's historical median (62%). So the price doesn't require something
unprecedented — it requires Tesla to **keep doing what it has done**, for a
full decade more, **without slowing down**.

That's the actual investment question. Not "is Tesla worth $426?" but
"do you believe Tesla can sustain near-historical growth for another 10 years?"

---

## 3. The verdict in three numbers

`[Visual: 3 large cards, big numbers, color-coded by upside/downside]`

```
┌─────────────────────┬─────────────────────┬─────────────────────┐
│  Conservative       │  Base case          │  Optimistic         │
│                     │                     │                     │
│      $96.74         │      $108.45        │      $122.46        │
│      ▼ −77%         │      ▼ −75%         │      ▼ −71%         │
│                     │                     │                     │
│  35% growth · 12%   │  35% growth · 11%   │  35% growth · 10%   │
│  WACC               │  WACC               │  WACC               │
└─────────────────────┴─────────────────────┴─────────────────────┘
```

All three scenarios land far below the current price. **There is no
combination of "moderate" assumptions in this model that justifies $426.**

⚠ **Caveat:** the scenario growth rates all collapse to the same 35% cap
because Tesla's historical growth is already very high. The optimistic case
does not provide meaningful upside over base — the cap is binding. Treat the
three numbers as a tight cluster, not a true range.

---

## 4. What you'd have to believe to disagree

The model says $108. The market says $426. For the market to be right, you
have to believe at least one of these:

| Belief | What it means |
|---|---|
| 1. **Tesla will grow FCF >60%/yr for a decade** | Slightly above the historical median, with no slowdown. Requires winning autonomous driving, robotaxi, or another mass-market product. |
| 2. **The discount rate (WACC 15.5%) is too high** | You don't accept that β=2.0 reflects real risk. You think Tesla is structurally less risky than its stock price volatility implies. |
| 3. **The terminal value matters more than the model assumes** | We discount cash flows after year 10 at 2.5% perpetual growth. If Robotaxi/FSD/Optimus pay off, the post-2034 cash flows are enormous and the 2.5% assumption is wildly conservative. |
| 4. **DCF is the wrong framework for Tesla** | Tesla is still in capex-heavy growth mode. Mature-firm DCF systematically understates such companies. Compare instead with revenue multiples and option-value approaches. |

Each is defensible. The model can't tell you which belief is right — it
gives you the framework to be precise about *what you're actually betting on*.

---

## 5. Sanity check — multiples vs the market

`[Visual: 3 mini-cards in a row, each with current value and "vs benchmark"]`

| Multiple | Tesla | Benchmark | Read |
|---|---:|---:|---|
| **P/E** (Price / Earnings) | 421× | 22× S&P average | Tesla priced as if earnings will multiply many times over |
| **EV / EBITDA** | 169× | 12× auto industry | Tesla priced like software, not like cars |
| **FCF yield** | 0.39% | 4.5% 10-yr Treasury | A bond yields 11× more than Tesla's current cash flow |

Three independent metrics, three "premium" verdicts. None of them prove Tesla
wrong — they cross-validate that the DCF model isn't an outlier. Every
framework says Tesla is priced for exceptional future performance.

---

## 6. The company in 30 seconds

Tesla makes electric vehicles, battery storage, and solar products. Its
business is split:
- **Automotive (80%)** — Model 3, Y, S, X, Cybertruck, plus regulatory credits
- **Energy storage (10%)** — Megapack, Powerwall
- **Services & other (10%)** — supercharging, software, FSD subscriptions

Speculative future businesses (Robotaxi, Optimus humanoid robot, full FSD
autonomy) **don't appear in our valuation** because they don't yet generate
reported cash flow. If you believe in them, the market price is the answer to
"what are they worth?" — the model says they need to be worth ~$330/share
to justify the gap.

### 10 years of free cash flow

`[Visual: bar chart, negative bars in red, positive in blue]`

```
$8B ┤              ███
$6B ┤         ███  ███      ███      ███
$4B ┤              ███      ███ ███  ███
$2B ┤   ███   ███  ███ ███  ███ ███  ███
$0B ┤───────────────────────────────────────
−2B ┤███
−4B ┤    ███
    └─────────────────────────────────────────
    '15  16   17   18   19   20  21   22  23  24
```

Tesla burned cash through 2017 during the Model 3 ramp. Turned positive in
2019 ($1.1B) and stayed positive since, peaking at $7.8B in 2022.
**Three of the ten years are negative** — the source of our AMBER suitability
rating.

---

## 7. How sensitive is the answer? (Try different assumptions)

`[Visual: heatmap grid. Cells colored green if above $426, red if below, with the closest-match cell highlighted with an amber border.]`

What intrinsic value comes out of the model for different
(growth × discount rate) combinations:

|  | WACC 6% | 7% | 9% | 10% | 11% | 13% | 14% |
|---|---:|---:|---:|---:|---:|---:|---:|
| g = −5% | $28 | $22 | $18 | $16 | $14 | $13 | $12 |
| g = 5% | $63 | $46 | $36 | $30 | $26 | $22 | $20 |
| g = 15% | $139 | $97 | $74 | $59 | $49 | $36 | $36 |
| g = 25% | **$301** | $206 | $153 | $120 | $97 | $81 | $68 |

The amber cell ($301 at 25% growth, 6% WACC) is the combination *closest* to
today's $426 — and it's still **$125 short**. **No realistic combination of
inputs in this grid produces the current price.** To match $426 you'd need
growth >25% AND WACC <6% simultaneously — both are extreme by historical
standards.

`[Interactive enhancement (future): sliders for growth and WACC; IV updates live.]`

---

## 8. Show your work — the full math

For every number above, the formula, inputs, and computation.

### 8.1 Free cash flow (EPFL formula sheet)

```
FCF  =  (EBITDA − Depreciation) × (1 − Tax rate)
        + Depreciation
        − Change in Working Capital
        − Capital Expenditure
```

For Tesla's most recent year:

```
FCF  =  ($14.7B − $5.4B) × (1 − 21%)  +  $5.4B  −  $1.1B  −  $8.6B
     =  $7.4B + $5.4B − $1.1B − $8.6B
     =  $3.1 B
```

A "median of recent positive years" is used as the projection base instead of
the latest year (which can be volatile). Base = **$3.4B**.

[Source: SEC EDGAR concepts `Revenues`, `OperatingIncomeLoss`,
`DepreciationAndAmortization`, `IncomeTaxExpenseBenefit`,
`NetCashProvidedByOperatingActivities`, `PaymentsToAcquireProductiveAssets`.]

### 8.2 Beta — the market-sensitivity measure (EPFL formula sheet)

```
β  =  Cov(r_TSLA, r_S&P500)  /  Var(r_S&P500)
```

5 years of daily log returns. Raw OLS estimate ≈ 2.3. **Capped at 2.0** as a
regularization — uncapped beta produces unstable WACC for high-volatility
stocks.

**β = 2.00** (capped — see calibration disclosure below).

### 8.3 Cost of equity — CAPM (EPFL formula sheet)

```
r_E  =  r_f  +  β × (r_M − r_f)
     =  4.5%  +  2.00 × 5.5%
     =  15.5%
```

| Input | Value | Source |
|---|---:|---|
| Risk-free rate (`r_f`) | 4.5% | 10-yr US Treasury (current) |
| Market risk premium (`MRP`) | 5.5% | Damodaran historical average |
| Beta (`β`) | 2.00 | OLS, capped |

### 8.4 Cost of debt — after-tax

```
r_D (after tax)  =  (Interest expense / Average debt) × (1 − Tax rate)
                 =  3.8% × (1 − 21%)
                 =  3.0%
```

### 8.5 WACC — the discount rate (EPFL formula sheet)

```
WACC  =  (E/V) × r_E  +  (D/V) × r_D × (1 − T)

Tesla's structure:  E = $1,580B   D = $11B   V = $1,591B
                    E/V = 99.3%   D/V = 0.7%

WACC  =  0.993 × 15.5%  +  0.007 × 3.0%
      =  15.5%
```

Because Tesla is ~100% equity-financed, WACC ≈ cost of equity. Debt barely
matters.

### 8.6 10-year FCF projection — future value × growth (EPFL formula sheet)

```
FCF in year t  =  Base FCF × (1 + g)^t
PV of FCF year t  =  FCF year t  /  (1 + WACC)^t
```

Base = $3.4B, g = 35%, WACC = 15.5%:

| Year | Projected FCF | Discount factor | Present value |
|---:|---:|---:|---:|
| 1 | $4.6B | 1.155 | $4.0B |
| 2 | $6.2B | 1.334 | $4.6B |
| 3 | $8.4B | 1.541 | $5.4B |
| 5 | $15.3B | 2.056 | $7.4B |
| 7 | $27.8B | 2.743 | $10.1B |
| 10 | $68.4B | 4.227 | $16.2B |
| **Sum** | | | **$88.5B** |

### 8.7 Terminal value — growing perpetuity (EPFL formula sheet)

After year 10, we assume Tesla settles into long-run growth at GDP-adjacent
rates.

```
TV (at end of year 10)  =  FCF_year10 × (1 + g_term) / (WACC − g_term)
                        =  $68.4B × 1.025 / (0.155 − 0.025)
                        =  $539B

PV of TV  =  $539B / (1.155)^10  =  $128B
```

### 8.8 Equity bridge — from enterprise value to per-share

```
Enterprise Value (EV)  =  PV of FCFs + PV of TV  =  $88.5B + $128B  =  $216B
Net Debt              =  Total Debt − Cash       =  $11B − $21B = −$10B (net cash)
Equity Value          =  EV − Net Debt           =  $216B + $10B  =  $226B
Intrinsic Value/share =  Equity / Diluted shares =  $226B / 3.71B =  $108.45
```

### 8.9 Reverse DCF — solving for implied growth

We hold WACC, terminal growth, and the 10-year horizon constant. We solve for
the growth rate `g` that makes `IV per share = $426.01` exactly. Implemented
via `scipy.optimize.brentq`.

```
solve for g:  IV(g; WACC=15.5%, g_term=2.5%) = $426.01
            ⇒ g* = 57.5%/yr
```

That's the market's implied bet.

---

## 9. Suitability and red flags

`[Visual: red-flag list with traffic-light dots]`

🟡 **Suitability rating: AMBER** — DCF model is appropriate but with caveats.

**Red flags surfaced by the model:**

- 🟡 **Negative FCF in 3 of 10 historical years** — our growth estimate uses
  only positive-to-positive transitions, which is more stable but excludes
  ~30% of the data.
- 🟡 **Terminal value = 59% of enterprise value** — most of the answer comes
  from cash flows beyond year 10, which we can't observe.
- 🟡 **Beta capped at 2.0** — raw OLS estimate was ~2.3. The cap improves
  stability but understates risk by about 1.5pp of WACC.
- 🟡 **Scenario growth caps at 35%** — base and optimistic scenarios collapse
  to the same rate because historical growth is already high. The
  "optimistic" case provides no real differentiation from base.
- 🟢 **Balance sheet healthy** — Tesla has $10B more cash than debt; not
  a distress concern.

None of these are dealbreakers. They're the honest disclosure of where this
model is least confident.

---

## 10. How much should you trust this?

`[Visual: warning callout box]`

> **Calibration status: PENDING.** This model has been *unit-tested* against
> the EPFL Principles of Finance answer keys (163 tests, all passing). It has
> **not yet been backtested** on historical predictions — we don't yet know
> whether its "fair value" estimates have been accurate for real companies
> over time.
>
> A walk-forward backtest across 50+ S&P 500 stocks (2014–2024) is the next
> deliverable. Until then, treat every number on this page as the output of a
> *formal model* — not as a forecast that has been shown to be right.

This is unusual to disclose. Most retail tools hide the question.
[Roadmap and methodology: see `/about` page.]

---

## 11. Sources, formulas, and audit trail

`[Visual: a clean disclosure block, monospace font, like an academic citation list]`

**Financial data**
SEC EDGAR XBRL filings (US-GAAP), live at request time, cached 24 hours.

**Price data**
yfinance (Yahoo Finance free API), 5 years of daily adjusted closes.

**Macro inputs (configurable in API)**
- Risk-free rate: 4.5%
- Market risk premium: 5.5% (Damodaran historical)
- Terminal growth: 2.5%

**Formulas applied** (every reference to EPFL = Berk-DeMarzo, *Principles of Finance*, formula sheet)

| Step | Formula | Source |
|---|---|---|
| FCF | `(EBITDA − D&A)(1−T) + D&A − ΔWC − Capex` | EPFL FCF appendix |
| Beta | `Cov(r_s, r_m) / Var(r_m)` | EPFL formula sheet |
| CAPM | `rf + β·MRP` | EPFL formula sheet |
| WACC | `(E/V)·rE + (D/V)·rD·(1−T)` | EPFL formula sheet |
| FCF projection | `FCF × (1+g)^t` | EPFL FV factor |
| Discount factor | `1 / (1+WACC)^t` | EPFL formula sheet |
| Terminal value | `C(1+g) / (r−g)` | EPFL growing perpetuity |
| Reverse DCF | Numeric: `brentq(IV(g) − P = 0)` | scipy |

**Code**
Every formula has a tested function in `core/`. Source:
[github.com/A-bv/openquant](https://github.com/A-bv/openquant). 163 tests.

---

## 12. Action

- **📄 Download this report as PDF** *(coming next)*
- **💾 Save TSLA to a watchlist** *(coming after auth)*
- **🔍 Compare to peers (GM, F, RIVN, NIO)** *(coming with portfolio module)*

---

### Side note — what about Buffett?

Buffett doesn't use WACC. He discounts at the long-bond rate (~4–5%), uses
"owner's earnings" (a slight FCF variant), and demands a **30%+ margin of
safety** below intrinsic value before buying. His method would yield a higher
intrinsic value for Tesla (because he'd discount at 5%, not 15.5%) — but he'd
also refuse to use the method for Tesla at all, because he doesn't invest in
businesses whose future he can't predict with confidence.

OpenQuant uses the academic method because it's *traceable* to a published
curriculum — every step can be verified against the EPFL formula sheet.
Buffett's method is equally legitimate but harder to make reproducible.

---

**End of document.**

---

## Author's notes for review

**What's new in v2 (vs v1):**
- Hero now has a price gauge + 5-dimension scorecard (Simply Wall St style)
- The reverse-DCF question is moved up to section 2 (was §12)
- "What you'd need to believe" moved to section 4 (was §16)
- Multiples sanity check at section 5 (was §15)
- All the math consolidated into a single "Show your work" section
- Buffett demoted to a single footer paragraph
- Visual cues: `[Visual: ...]` callouts mark where charts/graphics go
- Status badges (🟢 🟡 🔴) replace prose descriptions where possible

**What I'd test on a real beginner:**
- Does the scorecard in §1 give them enough to decide whether to keep reading?
- Does §2's "the market's implied bet" land as the central insight?
- Do they read §8 (the math), or just skim it? If they skim, that's fine —
  the verdict and explanation should hold without the math
- Is section 10 (calibration honesty) confidence-destroying or
  confidence-building? Goal is the latter.

**What still feels heavy to me:**
- §8 is unavoidably dense. Could split into 8a (cash flow), 8b (discount rate),
  8c (the calculation) on tabs or scroll-spy if needed.
- §7 sensitivity grid is hard to read in tabular form — it really wants to
  be an interactive heatmap with hover tooltips.

**What's deliberately omitted:**
- DCF for dividend-paying stocks (DDM) — Tesla doesn't pay dividends
- Portfolio module — orphaned; restoration is Phase 1.5
- Owner's earnings adjustment — folded into the Buffett side-note
- APV (alternative valuation) — different model, separate page if added
