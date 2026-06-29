# OpenQuant — Deliverables Backlog

This replaces "modules that mirror course chapters" with **useful deliverables**.

OpenQuant exists to answer one question: *is the EPFL Principles of Finance
course actually useful in real life?* The app proves it by applying each course
concept to **real financial data** and returning a **concrete result a normal
person can act on** — never a formula, never a false claim of truth.

## Design rules

1. **Concept = machinery, deliverable = a real-life result.** We never show the
   covariance matrix; we show *"8 holdings = 1.4 independent bets."*
2. **Never claim the impossible.** No screen ever says "this stock is worth $X."
   It says *"at this price you are betting on X — do you believe it?"*
3. **Two layers, for the general public.**
   - **Layer 1** — the simple result + an honest one-line limit. Default view.
   - **Layer 2** — opt-in depth: theory, the formula, the live computation, the
     EPFL source, and the test that pins it. Built from what is already
     calculated (`core/`), proven manually (the Excel Master Workbook), and
     verified (the EPFL sample-exam tests).
4. **Every number carries its honest limit.**

## Three assets we already have (and reuse, don't rebuild)

| Asset | Role | Where |
|---|---|---|
| EPFL Excel Master Workbook (13 sheets) | manual proof every concept is applicable | `infoSource/.../EPFL_Finance_Master_Workbook.xlsx`, catalogued in `docs/openquant_workbook_formula_inventory.csv` |
| EPFL Sample Exams 1 & 2 (worked answers) | correctness oracle | `tests/test_epfl_exam1.py`, `tests/test_epfl_exam2.py` |
| `core/` engine | live-data implementation | `core/*.py` |

Status legend: ✅ done · ◑ partial · ✗ missing

## The backlog

Columns: **Excel** (manual proof) · **Exam** (test oracle) · **core** (live engine).

### Tier 0 — Everyday money (TVM) · the course gives THE answer, for everyone
| Deliverable (Layer-1 result) | Excel | Exam | core | Status |
|---|:--:|:--:|:--:|:--:|
| "0% over 24mo vs −10% cash → the 0% deal costs you €312 more." (PV/FV) | ✅ | ◑ | ✅ `utils` | build UX |
| "This loan: €4,200 of interest = 21% of principal." (annuity) | ✅ | ✗ | ✅ `dcf` | build UX |
| "Paying X/yr forever is worth ~€300k at 4%." (perpetuity) | ✅ | ✅ | ✅ `dcf` | build UX |
| "Fund these 3 projects; the 4th destroys value." (profitability index) | ✅ | ✗ | ◑ | needs PI |

### Tier 1 — Rates & bonds · saver, near-exact answer
| Deliverable | Excel | Exam | core | Status |
|---|:--:|:--:|:--:|:--:|
| "1.5%/mo = 19.6% effective, not 18%." (rate conversion) | ✅ | ✗ | ✗ | new |
| "At your 4% hurdle this bond is worth 96.2 → at 98 you overpay." (bond price) | ✅ | ✗ | ✗ | new |
| "This price implies a 3.45%/yr return, not 3%." (YTM) | ✅ | ✗ | ✗ | new |
| "The curve prices a 3.8% 1y-rate in 1y — wait or lock?" (spot/forward) | ✅ | ✗ | ✗ | new |
| "+1% rates → −7% on your bonds." (duration) | ✅ | ✗ | ✗ | new |

### Tier 2 — Risk & return · the life-changing block (built first)
| Deliverable | Excel | Exam | core | Status |
|---|:--:|:--:|:--:|:--:|
| "8 holdings = 1.4 independent bets; you carry 2.4× the risk you think." (covariance) | ✅ | ✅ P4 | ✅ `portfolio` | **DONE (this slice)** |
| "This 10% position drives 25% of your risk." (risk contribution) | ✅ | ✗ | ✅ `portfolio` | **DONE** |
| "65/35 mix minimises vol at 11%." (min-variance) | ✅ | ✅ P4 | ✅ `portfolio`/`utils` | **DONE** |
| "70% of this stock's risk is diversifiable; 30% is market." (systematic split) | ✅ | ✅ P5 | ✅ `wacc` | wire to UX |
| "Vol 25% → a normal year runs −16% to +34%." (variance) | ✅ | ✅ | ✅ `utils` | wire to UX |
| "Your Sharpe 0.4 < 0.6 for a plain 60/40 — dominated." (Sharpe) | ✅ | ✅ P5 | ✅ `utils` | wire to UX |
| "Beta 1.8 → market −10% means expect −18%." (beta) | ✅ | ✅ | ✅ `wacc` | wire to UX |
| "You earned +12% but your beta justified +13% → negative alpha." (alpha) | ✅ | ✗ | ◑ | needs alpha |
| "For beta 1.4, require 11%/yr before buying." (CAPM) | ✅ | ✅ | ✅ `wacc` | wire to UX |

### Tier 3 — Valuing a company / project · structures, never states truth
| Deliverable | Excel | Exam | core | Status |
|---|:--:|:--:|:--:|:--:|
| "Profit €5B but FCF €1.2B — growth eats the cash." (FCF) | ✅ | ✅ | ✅ `fcf` | wire to UX |
| "At this price the market needs +57% FCF/yr for 10y. Believe it?" (reverse-DCF) | ✅ | ✅ | ✅✅ `reverse_dcf` | mature |
| "59% of the value sits beyond year 10 — an assumption, not data." (terminal value) | ✅ | ✅ | ✅ `dcf` | mature |
| "A: IRR 28% but +€2M. B: IRR 21% but +€8M — IRR misleads." (NPV vs IRR) | ✅ | ✅ | ✅ `utils` | wire to UX |
| "WACC 9.2% — the minimum return this business must earn." (WACC) | ✅ | ✅ | ✅ `wacc` | mature |
| "Unlevered beta 0.8; levered 1.3 → 60% of equity risk is financing." (Hamada) | ✅ | ✅ | ✅ `wacc` | wire to UX |

### Tier 4 — Financing (advanced)
| Deliverable | Excel | Exam | core | Status |
|---|:--:|:--:|:--:|:--:|
| "Ops €10B + €1.5B tax shield − €0.4B distress = €11.1B." (APV) | ✅ | ◑ | ◑ | extend |
| "Each €1 of permanent debt → ~€0.21 of tax value." (tax shield) | ✅ | ✅ | ◑ | extend |
| "Beyond 40% debt, distress cost exceeds the tax gain. Optimum ~35%." (trade-off) | ✅ | ✗ | ✗ | new |

### Tier 5 — Derivatives / protection
| Deliverable | Excel | Exam | core | Status |
|---|:--:|:--:|:--:|:--:|
| "Spot 100, 4%, 1y → fair forward 104. At 108 it's rich." (forward) | ✅ | ✗ (Exam 3 uncabled) | ✗ | new |
| "Floating→fixed costs you 3.2% — the price of sleeping." (swap) | ✅ | ✗ | ✗ | new |
| "A −10% put on your book costs 2.3%/yr." (options) | ✅ | ✗ | ✗ | new |
| "Call−Put should be 3.2; market shows 3.8 → inconsistency." (put-call parity) | ✅ | ✗ | ✗ | new |
| "At $8 you pay 45% implied vol — a bet on panic." (Black-Scholes) | ✅ | ✗ (Exam 3 uncabled) | ✗ | new |

## Two open gaps worth closing early

1. **Sample Exam 3 is not wired as tests.** It is the untapped oracle for the
   derivatives / late material (Tier 5). Cabling it the way Exams 1–2 are cabled
   gives Tier 5 the same correctness guarantee the rest enjoys.
2. **The risk/portfolio engine had been deleted** (`core/portfolio.py` removed,
   only a stale `.pyc` remained). Restored in this slice as the first
   non-valuation block promoted Excel → exam → live data.

## Build order

1. **Risk/portfolio (Tier 2)** — least mature, most universally useful, already
   has an exam oracle. *(this slice)*
2. Wire the rest of Tier 2 (beta/CAPM/Sharpe/systematic split) into the
   two-layer UX — engine already exists in `core/`.
3. Tier 0 (everyday money) — broadest audience, the course gives THE answer.
4. Tier 3 reverse-DCF — reframe the existing mature engine into the two layers.
5. Tier 1 (bonds/rates) and Tier 5 (derivatives, after cabling Exam 3).
