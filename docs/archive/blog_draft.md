# I built a stock-valuation tool from my finance course homework. Then I tested it on 10 years of history. The result was humbling.

> Draft post for LinkedIn / personal blog / CV portfolio.
> Adjust tone, length, and platform as needed.
> Estimated read time: 6-8 minutes.

---

## The hook (140 chars for social)

> I implemented every DCF, WACC, and CAPM formula from my finance course
> exactly as taught. Then I tested it on 50 real stocks. R² = 0.04.
> Here's what I learned.

---

## Opening (LinkedIn / blog header)

Most finance tools that show you a "fair value" for a stock are black boxes.
Bloomberg costs $24K/year and never explains its math. Simply Wall St gives
you a number with no derivation. Even free tools like finbox skip the steps.

I wanted to know: what happens if you take the exact formulas from an
introductory finance course — the ones in the EPFL Principles of Finance
formula sheet — and apply them transparently to real market data?

So I built **OpenQuant**. Every formula traceable to the textbook. Every
intermediate calculation visible. And then I did something most tools never
do: I tested it against 10 years of S&P 500 history and **published the
results, including the failures.**

This is what I learned.

---

## Part 1 — What I built (1 minute)

OpenQuant takes any US stock ticker, pulls 10 years of SEC EDGAR filings
plus historical prices from Yahoo Finance, and runs the academic equity
valuation pipeline:

1. **Free Cash Flow** from EBITDA, depreciation, working capital, capex —
   the exact formula in the EPFL textbook appendix
2. **Beta** as Cov(stock, market) / Var(market) — also the textbook formula
3. **Cost of equity** via CAPM: `rf + β × MRP`
4. **WACC** weighted by market-value capital structure with Hamada
   unlevering for capital-structure adjustments
5. **DCF**: project FCF 10 years forward, discount at WACC, add growing
   perpetuity terminal value
6. **Reverse DCF**: solve numerically for the growth rate that would make
   intrinsic value equal today's price — the question Warren Buffett
   actually asks ("what assumptions justify the current price?")
7. **Sensitivity grid** across growth × WACC

Built in Python (FastAPI backend) + React frontend. Every formula has a
unit test pinning it to the corresponding answer key in the EPFL Sample
Exams. 163 tests pass. The math is provably correct.

---

## Part 2 — The pretty UI (the part that's easy)

I won't dwell on this. The frontend has:

- Plain-English verdict ("Tesla at $426 is overvalued under our model")
- Three valuation scenarios (conservative / base / optimistic)
- An interactive slider panel — drag growth, drag WACC, watch intrinsic
  value recompute live
- "What would you need to believe?" cards
- Heatmap sensitivity grid
- Honest hover-definitions on every jargon term

If I had stopped here, I'd have shipped a "valuation tool" like every
other one on the internet — except prettier and with cleaner math. That
seemed too easy, and not actually useful.

---

## Part 3 — The hard question

A model can be **mathematically correct** and **empirically useless** at
the same time. The formulas can be flawless and the predictions still wrong.

So I built a backtest framework. I took 50 S&P 500 stocks as of January
2014 — using **only data that would have been available then** — and ran
the full model. I used **period-appropriate macro inputs** (10-year UST
yield of 2.65%, market risk premium of 5.0% per Damodaran for that month)
instead of today's values, because using today's rates for a 2014
valuation is just hindsight cheating.

Then I waited until 2024 and compared each prediction to what actually
happened.

---

## Part 4 — The result

This is the part most finance bloggers skip. I'll show it.

| Model verdict | n | Mean realized 10-yr return (annualised) |
|---|:---:|---:|
| Stocks the model called "undervalued" (you should buy) | 25 | **+12.3%/yr** |
| Stocks called "fairly priced" (hold) | 2 | +9.4%/yr |
| Stocks called "overvalued" (you should avoid) | 6 | **+13.6%/yr** |
| S&P 500 baseline | — | +12.1%/yr |

**The stocks I told you to avoid outperformed the stocks I told you to buy.**

The calibration regression — predicted upside vs realized return — has
**R² = 0.04 and slope ≈ 0**. The model explains 4% of the cross-sectional
variation in realized returns. A coin flip explains 0%. We're barely
better than nothing.

If the model had been calibrated, the "undervalued" basket would have
beaten the index and the "overvalued" basket would have lagged. They
basically didn't.

---

## Part 5 — Why it failed (the interesting part)

The math is correct. So what's wrong? Three structural issues:

**1. The 35% FCF growth cap, compounded over 10 years, explodes.**
Cap growth at 35%/yr for 10 years means year-10 FCF is 20× starting FCF.
For most large-caps, that's wildly optimistic. The model thinks every
profitable company is undervalued because it projects them into a
hypergrowth future.

**2. The 2014 macro regime broke the discount.**
Risk-free rate was 2.65%. Most of my universe had β between 0.5-1.1.
That produces WACC of 5-7%. The growing perpetuity formula
`C(1+g)/(r-g)` is wildly sensitive when `r-g` is small — at WACC=6%
and terminal growth=2.5%, the perpetuity multiplier is 29×. Most of
the model's "valuation" came from cash flows beyond year 10 that
nobody can predict.

**3. Universe selection biased toward survivors.**
"Companies that had 10 years of EDGAR coverage as of 2014" tilts
toward mature, profitable firms — exactly the ones that grew slower
than the 35% cap.

None of this is a bug. It's the model's structural design colliding with
the empirical reality of how stocks actually behave. **You can't see
that from the formulas alone. You only see it by testing.**

---

## Part 6 — Why I'm publishing the failure

Most retail finance tools are sold as products. Sellers don't publish
backtests because publishing a bad backtest kills the sale.

This isn't a product. It's a learning artifact. The most useful thing
about it isn't the "verdict" — it's the journey:

- You **can** implement academic theory from a textbook in working code
- Even **correct** math gives **wrong** answers when calibration is off
- The model can be improved (growth cap, fade, WACC floor, larger universe),
  and each improvement is testable against the same backtest
- **A transparent tool that admits its limits is more useful than a black
  box that doesn't** — even when "admits limits" means "the model doesn't
  work well yet"

Bloomberg won't publish their backtest. Simply Wall St won't. Most analysts
on CNBC won't tell you their hit rate. I will: I'm right about as often as
a coin flip, and I can tell you exactly why.

---

## Part 7 — What I'd do next (if I were going to)

The next moves are clear from the implemented backtest metrics:

1. **Lower the FCF growth cap from 35% to 20%** (no large-cap sustains 35%
   over a decade in practice)
2. **Fade growth to terminal rate over years 4-10** (instead of step
   function at year 11)
3. **WACC floor ≥ 8%** (regardless of CAPM output)
4. **Re-run backtest, measure R² improvement**
5. **Expand universe to 100+ stocks, multiple "as of" dates**

Each fix is bounded. Each is testable. The success metric is the
calibration R², not vibes.

But honestly, the project has done its job for me. It taught me more than
the course did about what these formulas actually mean — because applying
them to a real, messy, partly-wrong real-world test is fundamentally
different from solving a clean exam problem with a known answer.

---

## What I learned (the listicle)

For the post version:

- **Implementing theory is way more revealing than reading it.** I knew
  the CAPM formula. Until I implemented it against SEC EDGAR data, I
  didn't really understand why β estimates are unstable, why historical
  growth is a bad anchor, or why terminal values dominate every DCF.
- **Testing your model honestly is unsettling.** Watching my carefully
  built tool produce R² = 0.04 was uncomfortable. But the alternative —
  not testing, and shipping with false confidence — is worse.
- **Transparency is itself a feature.** Most finance tools sell a
  number. The number is wrong as often as right. A tool that shows you
  the *derivation* of the wrong number is more honest, and arguably more
  useful — because you can disagree with specific assumptions.
- **Finance theory has tractable shortcomings.** Discount rates compound;
  growth caps compound; survivor selection biases the universe. None of
  these are revealed by reading Berk & DeMarzo. All of them are revealed
  by running the model on 50 stocks and looking at what came out.
- **The reverse DCF is a better framing than the forward DCF.** Instead
  of "what's this worth?" (a prediction problem), ask "what does today's
  price imply?" (a judgment problem). Same math, opposite direction,
  vastly more useful.

---

## If you want to look

Code, tests, and implemented backtest results:
**[github.com/A-bv/openquant](https://github.com/A-bv/openquant)**

The main backtest result appears in the OpenQuant reliability panel. Raw
results live in `backtest/results/` and the headline metrics are locked by
tests.

If you spot a math bug — particularly any case where my output disagrees
with an EPFL Sample Exam answer key — open an issue. That's the
highest-priority feedback.

If you find this honest about its limits in a way most finance tools
aren't, that was the point.

---

## Suggested headlines / opening lines for variants

**LinkedIn (professional):**
*"I built a stock-valuation tool from my finance coursework. Then I
back-tested it on 10 years of history. R² = 0.04. Here's what that taught
me about academic finance."*

**Twitter/X thread opener:**
*"Most finance tools that give you a 'fair value' are black boxes. So I
built one that shows every formula AND publishes its own backtest.
The result was humbling. 🧵"*

**Hacker News:**
*"Show HN: I implemented every DCF/WACC/CAPM formula from a finance
course and back-tested it on 50 real stocks. Math is provably correct;
predictions explain 4% of realized returns. Here's the full report."*

**CV one-liner:**
*"Built a transparent equity-valuation tool from EPFL Principles of
Finance course material, applied to real SEC EDGAR data, including a
walk-forward backtest revealing the model's structural limits — all
formulas traceable and unit-tested against published exam answer keys."*

---

**End of draft.** Adjust tone, edit ruthlessly for length, replace the
TSLA example with whatever resonates. The honest backtest is the
distinguishing feature — lean into it everywhere.
