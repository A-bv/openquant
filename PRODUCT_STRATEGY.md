# OpenQuant Product Strategy

## Goal

OpenQuant is the practical application of the course objective:

> financial valuation and value enhancement through financial decision making.

The current product applies that objective to real listed-company data. It is
not a stock picker and not a full implementation of the entire course.

## Current Product

OpenQuant answers one question:

> What must be true for the current market price to make sense?

It uses course-tested finance logic to connect company cash flows, risk,
discount rates, market price, and assumptions. Formula names are implementation
tools, not the product.

## In Scope Now

| Area | Status |
|---|---|
| Listed-company valuation | Productized |
| Market-implied expectations / reverse DCF | Productized |
| DCF scenarios and sensitivity | Productized |
| WACC/CAPM inputs needed for valuation | Productized inside stock analysis |
| Formula correctness against sample-exam style answers | Implemented as tests |
| Historical backtest summary | Productized as model reliability disclosure |

## Out of Scope Now

| Area | Status |
|---|---|
| Derivatives | Out of scope |
| Bond and rates lab | Not productized |
| Portfolio lab | Not productized |
| Project decision lab | Not productized |
| Full capital-structure policy lab | Not productized |
| Buy/sell recommendations | Not a goal |

## Backtest Role

Backtests are not a Markdown story. They are implemented validation artifacts:

- `backtest/` runs historical as-of analysis.
- `backtest/results/` stores the raw CSV and calibration summary.
- `tests/` locks the main backtest metrics so they cannot drift silently.
- The app shows only the main reliability results.

Current result: formulas are tested, but the 2014-2024 stock-valuation signal
is not calibrated as a reliable predictor of realized returns.

## Product Rule

Every OpenQuant screen should follow this order:

1. Start with the real financial question.
2. Show the conclusion in plain English.
3. Show the assumptions that drive it.
4. Let the user change those assumptions.
5. Show formula details and limitations only as supporting evidence.

OpenQuant succeeds if it makes financial valuation reasoning practical,
transparent, and testable with real data.
