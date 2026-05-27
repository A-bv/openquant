# OpenQuant Product Strategy

## Product Thesis

OpenQuant should not be a generic DCF calculator.

The stronger product is an interactive finance lab that turns a university
finance course into real-world decision tools. The app should help a user move
from a textbook formula to an actual financial judgment:

> What must be true for this investment, project, bond, portfolio, or capital
> structure decision to make sense?

The product's value is not prediction certainty. Its value is clarity:
identifying the assumptions behind a financial decision, showing the formulas
that connect those assumptions to an answer, and making the limits of the
model explicit.

## Target Users

### Primary

Finance students who know the formulas but struggle to understand why they
matter in real life.

### Secondary

Self-directed investors, founders, analysts, and technically minded learners
who want transparent financial reasoning instead of black-box ratings.

### Tertiary

Recruiters, professors, and reviewers evaluating whether the project can turn
academic finance into a practical software product.

## Core Promise

OpenQuant helps users answer real financial questions with course concepts:

- Is this stock price justified by the cash flows the market is implying?
- Does this project create value after accounting for the time value of money?
- How sensitive is a bond to changes in interest rates?
- Is this portfolio actually diversified, or just holding many correlated bets?
- How does leverage change value, risk, WACC, and distress exposure?
- What payoff is embedded in an option, forward, swap, or derivative contract?

## Product Positioning

Avoid positioning the product as:

> A tool that tells you whether to buy or sell a stock.

Prefer positioning it as:

> A tool that shows what a financial decision requires you to believe.

For public messaging, the clearest one-line positioning is:

> OpenQuant turns finance formulas into real-world decision tools.

For the stock module specifically:

> OpenQuant shows what the market is already pricing in.

## Product Principles

### 1. Start With a Real Question

Every module should begin with a decision a real person might face. The formula
comes after the question, not before it.

Examples:

- "Is Apple expensive at today's price?"
- "Should this project be accepted?"
- "How much would this bond fall if rates rise by 1%?"
- "Does adding this asset improve my portfolio?"

### 2. Give the Plain-English Answer First

The first screen should answer the question in simple language. The user should
not need to read a WACC table, heatmap, or formula audit to understand the
initial conclusion.

### 3. Make Assumptions Editable

The app should teach that finance outputs are assumption-driven. Key variables
should be interactive:

- growth
- discount rate
- terminal growth
- cash-flow timing
- interest rates
- volatility
- correlation
- leverage
- tax rate

### 4. Reveal Complexity Progressively

The complete model can be deep, but the first experience should be simple.
Advanced material should be available through expandable sections:

- formula
- source chapter
- detailed calculation
- sensitivity table
- audit trail
- backtest evidence
- model limitation

### 5. Be Honest About Predictive Limits

The backtest is a strength, not an embarrassment. If the model's historical
predictive power is weak, the app should say so clearly.

This changes the product from "trust our fair value" to "understand the bet."

### 6. Teach Judgment, Not Memorization

The goal is not to reproduce exam exercises in software. The goal is to show
how course concepts help interpret real decisions under uncertainty.

## Recommended App Structure

### Home

The homepage should not be a marketing page. It should be a decision menu:

- Value a stock
- Evaluate a project
- Stress-test a bond
- Build a portfolio
- Analyze capital structure
- Price a derivative

Each entry should state the real question it answers.

### Module 1: Stock Valuation Lab

Current backend work should be reused here.

Core question:

> What must be true for this stock price to be justified?

Default flow:

1. Enter ticker.
2. Show market-implied growth and plain-English verdict.
3. Let the user adjust growth, discount rate, and terminal growth.
4. Show DCF scenarios.
5. Hide WACC, heatmap, multiples, and formula audit behind expandable details.

### Module 2: Project Decision Lab

Core question:

> Does this project create value?

Concepts:

- NPV
- IRR
- profitability index
- payback intuition
- scale problem
- discount-rate sensitivity

### Module 3: Bond & Rates Lab

Core question:

> What happens to this bond when rates move?

Concepts:

- bond price
- YTM
- spot rates
- forward rates
- Macaulay duration
- price sensitivity

### Module 4: Portfolio Lab

Core question:

> Is this portfolio actually diversified?

Concepts:

- expected return
- variance
- covariance
- correlation
- minimum variance portfolio
- efficient frontier
- Sharpe ratio
- beta and systematic risk

### Module 5: Capital Structure Lab

Core question:

> How does debt change value and risk?

Concepts:

- WACC
- unlevering and relevering beta
- Modigliani-Miller
- tax shield
- bankruptcy costs
- APV

### Module 6: Derivatives Lab

Core question:

> What payoff is this contract creating?

Concepts:

- forwards
- futures
- swaps
- put-call parity
- binomial option pricing
- Black-Scholes

## UX Pattern for Every Module

Each module should follow the same structure:

1. **Question**: the real decision.
2. **Answer**: a short plain-English conclusion.
3. **Drivers**: the key assumptions that matter most.
4. **Interaction**: sliders, inputs, toggles, or scenario controls.
5. **Visualization**: chart, payoff diagram, sensitivity table, or frontier.
6. **Formula**: the course formula used.
7. **Details**: expandable audit trail and limitations.

## First Implementation Milestone

Do not rebuild every module at once.

The first milestone should be a refactor of the existing stock analyzer into a
clearer Stock Valuation Lab:

- keep the existing backend
- improve API/deployment reliability
- make errors specific and understandable
- change the product language from "fair value" to "market-implied belief"
- show only the essential result first
- move advanced sections into expandable panels
- fix sector benchmark logic
- add a clear "model reliability" panel explaining the backtest

## Success Criteria

The product is working when a user can say:

- "I understand what the formula is used for."
- "I understand which assumption matters most."
- "I understand what the market/project/bond/portfolio is asking me to believe."
- "I can change the assumptions and see the decision change."
- "I understand the model's limits."

OpenQuant succeeds if it makes finance useful, not if it pretends finance can
predict the future with precision.
