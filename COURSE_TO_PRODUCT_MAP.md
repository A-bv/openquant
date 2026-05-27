# Course to Product Map

This document maps the EPFL finance course material to real-world decisions
and app modules. The goal is to convert each course topic from "formula to
memorize" into "tool for judgment."

## Product Map Summary

| Course Area | Real-World Question | Product Module |
|---|---|---|
| Time value of money | What is a future cash flow worth today? | Project Decision Lab |
| Bonds and YTM | Is this bond attractive at this price/yield? | Bond & Rates Lab |
| Spot and forward rates | What rates are implied by today's yield curve? | Bond & Rates Lab |
| Duration | How much will a bond move if rates change? | Bond & Rates Lab |
| Statistics | How risky is this asset or portfolio? | Portfolio Lab |
| Portfolio theory | Does this combination improve risk-adjusted return? | Portfolio Lab |
| CAPM and beta | What return should I require for this risk? | Stock Valuation Lab / Portfolio Lab |
| WACC | What discount rate should value this business? | Stock Valuation Lab / Capital Structure Lab |
| DCF and FCF | Is this stock/project price justified by cash flows? | Stock Valuation Lab / Project Decision Lab |
| APV and tax shield | How does financing change value? | Capital Structure Lab |
| Bankruptcy costs | When does debt stop helping? | Capital Structure Lab |
| Derivatives | What payoff/risk transfer does this contract create? | Derivatives Lab |
| Buffett intrinsic value | What owner-earnings assumptions justify the price? | Stock Valuation Lab |

## H1: Time Value of Money, Bonds & Stocks

### 1.1 PV & FV

Real-world use:

- Compare money today with money in the future.
- Decide whether a future payment is worth enough today.
- Convert a future payoff into a present value.

Product use:

- Project Decision Lab input block.
- "Cash-flow timeline" component used across modules.

User-facing question:

> Is this future cash flow worth enough today to justify the investment?

### 1.2 Perpetuity & Growing Perpetuity

Real-world use:

- Value stable cash-flow streams.
- Understand terminal value in a DCF.
- Explain why long-run growth assumptions dominate valuations.

Product use:

- Stock Valuation Lab terminal value explanation.
- Project Decision Lab terminal value option.

User-facing question:

> How much of the value comes from cash flows beyond the forecast period?

### 1.3 Annuity

Real-world use:

- Value repeated payments such as loans, leases, mortgages, and fixed project
  cash flows.

Product use:

- Project Decision Lab.
- Loan/payment calculator inside Bond & Rates Lab if useful later.

User-facing question:

> What is this stream of repeated payments worth today?

### 1.4 Bond Pricing

Real-world use:

- Price a bond from coupons, face value, maturity, and discount rate.
- Understand why bond prices fall when rates rise.

Product use:

- Bond & Rates Lab.

User-facing question:

> What should this bond be worth given today's required yield?

### 1.5 Yield to Maturity

Real-world use:

- Convert a bond price into an implied return.

Product use:

- Bond & Rates Lab.

User-facing question:

> What return is this bond price implying if held to maturity?

### 1.6 Stock Valuation

Real-world use:

- Link dividends/cash flows to equity value.
- Introduce the idea that a price embeds growth expectations.

Product use:

- Stock Valuation Lab.

User-facing question:

> What growth belief is embedded in today's stock price?

## H1+: Rate Conversions, Spot/Forward Rates, Duration, PI

### 2.1 Rate Conversions

Real-world use:

- Compare APR, EAR, periodic rates, and continuously compounded rates.

Product use:

- Rate converter utility inside Bond & Rates Lab.

User-facing question:

> Are these two quoted rates actually comparable?

### 2.2 Spot Rates from Zero-Coupon Bonds

Real-world use:

- Derive the term structure of interest rates.

Product use:

- Bond & Rates Lab yield curve builder.

User-facing question:

> What does today's bond market imply about rates at each maturity?

### 2.3 Forward Rates from Spot Rates

Real-world use:

- Infer future borrowing/lending rates implied by today's curve.

Product use:

- Bond & Rates Lab.

User-facing question:

> What future rate is already priced into today's yield curve?

### 2.4 Coupon Bond Using Spot Rates

Real-world use:

- Price each cash flow with its own maturity-specific discount rate.

Product use:

- Bond & Rates Lab advanced mode.

User-facing question:

> Does valuing each cash flow with the curve change the bond's value?

### 2.5 Macaulay Duration & Price Sensitivity

Real-world use:

- Estimate how sensitive a bond is to rate changes.

Product use:

- Bond & Rates Lab rate shock simulator.

User-facing question:

> If rates rise by 1%, how much value might this bond lose?

### 2.6 Profitability Index

Real-world use:

- Rank projects when capital is limited.

Product use:

- Project Decision Lab.

User-facing question:

> If I cannot fund every project, which creates the most value per dollar invested?

## H2a: Statistics

### 3.1 Expected Return

Real-world use:

- Estimate average outcome across states or historical observations.

Product use:

- Portfolio Lab.

User-facing question:

> What return should I expect before considering risk?

### 3.2 Variance & Standard Deviation

Real-world use:

- Measure volatility and uncertainty.

Product use:

- Portfolio Lab risk display.

User-facing question:

> How uncertain is this return?

### 3.3 Covariance & Correlation

Real-world use:

- Understand whether assets move together.

Product use:

- Portfolio Lab diversification engine.

User-facing question:

> Does this asset really diversify the portfolio?

## H2b: Modern Portfolio Theory & Diversification

### 4.1 Portfolio Return & Variance

Real-world use:

- Compute risk and return of a combination of assets.

Product use:

- Portfolio Lab.

User-facing question:

> What does this portfolio actually earn and risk as a whole?

### 4.2 Minimum Variance Portfolio Weight

Real-world use:

- Find the lowest-risk mix of two risky assets.

Product use:

- Portfolio Lab allocation slider.

User-facing question:

> What allocation minimizes volatility?

### 4.3 Risk-Free Portfolio When Correlation Equals -1

Real-world use:

- Show the intuition of hedging and offsetting risk.

Product use:

- Portfolio Lab teaching mode.

User-facing question:

> Can two risky assets combine into something safer?

### 4.4 Systematic vs Idiosyncratic Risk

Real-world use:

- Explain why diversification removes some risks but not market risk.

Product use:

- Portfolio Lab / Stock Valuation Lab.

User-facing question:

> Which part of this risk can diversification remove?

### 4.5 Efficient Frontier & Sharpe Ratio

Real-world use:

- Compare portfolios by risk-adjusted return.

Product use:

- Portfolio Lab frontier chart.

User-facing question:

> Am I being paid enough for the risk I am taking?

## H2c: CAPM, CML, SML, Alpha, Beta

### 5.1 CAPM Formula

Real-world use:

- Estimate required return from market risk exposure.

Product use:

- Stock Valuation Lab WACC details.
- Portfolio Lab expected return benchmark.

User-facing question:

> What return should investors require for this level of market risk?

### 5.2 Beta Interpretation

Real-world use:

- Measure sensitivity to the market.

Product use:

- Stock Valuation Lab.
- Portfolio Lab.

User-facing question:

> Is this asset more or less exposed to market risk than the index?

### 5.3 Idiosyncratic Variance

Real-world use:

- Separate company-specific risk from systematic risk.

Product use:

- Portfolio Lab risk decomposition.

User-facing question:

> How much of this risk is stock-specific?

### 5.4 CML vs SML

Real-world use:

- Distinguish total-risk portfolio pricing from beta-based asset pricing.

Product use:

- Portfolio Lab advanced explanation.

User-facing question:

> Is this comparison using total volatility or market beta?

### 5.5 Alpha

Real-world use:

- Compare realized/expected return against CAPM-required return.

Product use:

- Portfolio Lab.

User-facing question:

> Is this asset outperforming relative to the risk it takes?

## H2+: Exam-Specific Portfolio Tools

### 6.1 Capital Gain Rate & Total Return

Real-world use:

- Break return into price appreciation and income.

Product use:

- Portfolio Lab return explanation.

User-facing question:

> How much of the return came from price change versus cash distributions?

### 6.2 Common Exam False-Statement Traps

Real-world use:

- Convert common misconceptions into warnings and teaching callouts.

Product use:

- Learn mode across modules.

User-facing question:

> What is the common mistake in interpreting this result?

## H3a: WACC & Capital Structure

### 7.1 WACC Formula

Real-world use:

- Discount business cash flows using a capital-structure-weighted required
  return.

Product use:

- Stock Valuation Lab.
- Capital Structure Lab.

User-facing question:

> What return does this business need to satisfy both debt and equity holders?

### 7.2 Beta Unlevering & Relevering

Real-world use:

- Separate business risk from financing risk.

Product use:

- Capital Structure Lab.

User-facing question:

> How does adding debt change equity risk?

### 7.3 Modigliani-Miller

Real-world use:

- Understand when capital structure should or should not affect firm value.

Product use:

- Capital Structure Lab.

User-facing question:

> Is this value coming from operations or financing?

## H3b: DCF Valuation, FCF, NWC Components

### 8.1 Free Cash Flow

Real-world use:

- Estimate cash generated by operations after reinvestment needs.

Product use:

- Stock Valuation Lab.
- Project Decision Lab.

User-facing question:

> How much cash is actually available to capital providers?

### 8.2 Net Working Capital Components

Real-world use:

- Explain why accounting profit is not the same as cash flow.

Product use:

- Project Decision Lab advanced cash-flow builder.

User-facing question:

> Is growth consuming cash through working capital?

### 8.3 Terminal Value & Enterprise Value

Real-world use:

- Explain why DCFs are often dominated by long-term assumptions.

Product use:

- Stock Valuation Lab.

User-facing question:

> How much of the valuation depends on assumptions after year 10?

### 8.4 NPV vs IRR: The Scale Problem

Real-world use:

- Show why IRR can mislead when projects differ in size or timing.

Product use:

- Project Decision Lab.

User-facing question:

> Should I choose the project with the highest percentage return or the most value created?

## H3c: Disney DCF Case Study

Real-world use:

- Demonstrate a full company valuation workflow with real assumptions.

Product use:

- Stock Valuation Lab case-study mode.

User-facing question:

> What does a complete professional DCF workflow look like?

## H3+: APV, Tax Shield, Bankruptcy Costs

### 10.1 APV Framework

Real-world use:

- Value operations separately from financing effects.

Product use:

- Capital Structure Lab.

User-facing question:

> What is the company worth before and after financing effects?

### 10.2 PV of Tax Shield

Real-world use:

- Quantify the tax benefit of debt.

Product use:

- Capital Structure Lab.

User-facing question:

> How much value does debt create through tax savings?

### 10.3 PV of Bankruptcy Costs

Real-world use:

- Quantify the expected cost of financial distress.

Product use:

- Capital Structure Lab.

User-facing question:

> At what point does more debt become dangerous?

### 10.4 Trade-Off Decision

Real-world use:

- Balance tax benefits against distress costs.

Product use:

- Capital Structure Lab.

User-facing question:

> What debt level creates the best trade-off between tax benefits and distress risk?

## H4: Derivatives

### 11.1 Forward vs Futures

Real-world use:

- Understand contractual differences in settlement and counterparty exposure.

Product use:

- Derivatives Lab.

User-facing question:

> What risk is transferred by this contract?

### 11.2 Forward Pricing

Real-world use:

- Price a forward from spot, rates, income, and storage/carry assumptions.

Product use:

- Derivatives Lab.

User-facing question:

> What future delivery price avoids arbitrage?

### 11.3 Swaps

Real-world use:

- Convert floating exposure to fixed exposure, or vice versa.

Product use:

- Derivatives Lab.

User-facing question:

> What cash-flow risk is this swap exchanging?

### 11.4 Options

Real-world use:

- Understand asymmetric payoff and downside protection.

Product use:

- Derivatives Lab.

User-facing question:

> What upside and downside does this option create?

### 11.5 Put-Call Parity

Real-world use:

- Detect arbitrage relationships between calls, puts, stock, and bonds.

Product use:

- Derivatives Lab.

User-facing question:

> Are these option prices internally consistent?

### 11.6 Early Exercise

Real-world use:

- Explain when exercising an American option early may or may not make sense.

Product use:

- Derivatives Lab advanced mode.

User-facing question:

> Is exercising now better than keeping optionality alive?

### 11.7 Binomial Model

Real-world use:

- Price options by modeling paths and replication.

Product use:

- Derivatives Lab interactive tree.

User-facing question:

> How does option value emerge from possible future states?

### 11.8 Black-Scholes

Real-world use:

- Price European options from spot, strike, time, rates, and volatility.

Product use:

- Derivatives Lab.

User-facing question:

> How much is this option worth given volatility and time?

## Warren Buffett Intrinsic Value

Real-world use:

- Compare textbook DCF with an owner-earnings philosophy.
- Explain how a lower hurdle rate and margin of safety change the decision.

Product use:

- Stock Valuation Lab optional valuation philosophy toggle.

User-facing question:

> How does the conclusion change under a Buffett-style owner earnings lens?

## Sample Exams and Worked Solutions

Real-world use:

- Validate that the app's formulas reproduce course/exam logic.
- Convert worked examples into regression tests and "learn more" examples.

Product use:

- Formula audit panels.
- Test-backed citations.
- Teaching examples.

User-facing question:

> Can I trust that the formula is implemented the way the course teaches it?

## Recommended Build Order

### Phase 1: Stock Valuation Lab

Reuse existing backend and refactor the UI around market-implied belief.

Must include:

- ticker input
- market-implied growth
- simple verdict
- editable assumptions
- DCF scenarios
- model reliability/backtest explanation
- expandable formula details

### Phase 2: Project Decision Lab

Build from course workbook formulas, not live data.

Must include:

- project cash-flow input
- discount rate
- NPV
- IRR
- profitability index
- NPV vs IRR conflict explanation
- sensitivity to discount rate

### Phase 3: Bond & Rates Lab

Must include:

- coupon bond pricing
- YTM
- duration
- rate shock simulator
- optional spot-rate pricing

### Phase 4: Portfolio Lab

Must include:

- two-asset portfolio first
- expected return and volatility
- correlation slider
- minimum variance weight
- Sharpe ratio
- diversification explanation

### Phase 5: Capital Structure Lab

Must include:

- WACC
- unlever/relever beta
- tax shield
- distress cost
- APV vs WACC explanation

### Phase 6: Derivatives Lab

Must include:

- payoff diagrams
- forward price
- put-call parity
- binomial tree
- Black-Scholes optional advanced view

## Immediate Product Decision

The existing app should become Module 1, not the whole product.

The right next UI change is to convert the current long stock-analysis page
into a progressive decision flow:

1. "What is the market pricing in?"
2. "Do you believe that assumption?"
3. "Change the assumption and see the value."
4. "Open details if you want the full finance course machinery."

This keeps the current technical work, but aligns it with the original goal:
making the course useful in real life.
