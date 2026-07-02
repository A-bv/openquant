# OpenQuant — Product Plan (source of truth)

> This is the single document that defines what OpenQuant is becoming and how we
> get there. When other docs disagree with this one, this one wins. The older
> sketches (`phase1_tsla_sketch*.md`, `blog_draft.md`) are historical drafts.
> Keepers as reference: `openquant_deliverables.md` (the backlog of results) and
> `course_extract_h2.md` (the H2 course extraction).

## The goal

OpenQuant proves that the EPFL *Principles of Finance* course is **useful in real
life**. It does this by applying each course concept to data and returning a
**concrete result a normal person can act on** — never a formula, never a claim
of the impossible ("this stock is worth $X").

A finished OpenQuant is: **functional, easy to use, accessible to everyone**, and
honest about its limits.

## The one architecture decision

**One product = a self-contained, card-based web app.**

- **Pure-math cards run 100% in the browser** (time value of money, NPV, CAPM,
  bonds, options pricing). No server. They never fail, they deploy anywhere, they
  work for everyone. The deck (`companion.html`) already proves this is possible.
- **The Python engine (`core/`) stays as the proven reference (oracle).** Its 191
  tests are pinned to EPFL exam answers. The JS in the cards must match `core/`;
  a parity check guards this.
- **Live-data cards** (reverse-DCF on a real ticker, portfolio on real tickers,
  the backtest) ship with a **baked-in example dataset** so they work offline, and
  call the API only when one is present.
- **Cards group into short decision journeys** (the card1 stepper:
  *a dollar later → a stream → worth it? → decide*). Free browse stays too.
- **Each card carries three linked layers**: *learn* (the idea + formula),
  *do* (the interactive result on data), *check* (the backtest: "did the theory
  hold?").

Why this decision: the project's three biggest weaknesses — two disconnected
products, server fragility, and an invisible backtest — all dissolve in the
card format, because it is self-contained, it unifies the deck and the labs, and
it has a natural slot for the "check" layer.

## The guiding principle: everything is a link (user, 2026-06-29)

Like the 53-card deck on GitHub Pages, **every feature must be reachable by a
single link, with nothing for the user to run.** This is the simplicity bar.

- Pure-math features (most of the course) → 100% in the browser, a static file
  like the deck. Just a link, no server, ever.
- Live-data features (Stock reverse-DCF, Portfolio on real tickers) → the page
  itself is still a static link; the market data comes from the data module
  deployed **once** in the cloud (see P1b). The user clicks a link and never
  starts a server.
- The current React app + local FastAPI (two servers to run) is exactly the
  "needs things running" model we are retiring.
- Note: the Money/TVM lab does NOT need market data — it only routes through the
  backend because the math was put server-side. It belongs client-side like the
  cards.

## Architecture (decided 2026-06-29): hybrid

Where the calculations live — the decision the whole structure follows from.

**The boundary rule:** does it need live market data or a real dataset?
- NO  → pure formula on user inputs → runs in the BROWSER (JavaScript), no server.
- YES → runs on ONE Python service in the cloud.

**What that means per piece:**
- Browser (static, GitHub Pages, reachable by link): the deck, the journeys, and
  every simple-formula card — H1 (TVM, annuities, NPV/IRR, bonds), and the
  formula-level parts of H2/H3/H4 (CAPM, Sharpe, WACC, the DCF formula, options,
  Black-Scholes). The Money lab belongs here too.
- One cloud service (Python = `api/` + `core/` + `core/data`): the data labs that
  need real tickers — Stock reverse-DCF (EDGAR + yfinance) and Portfolio
  (price history → covariance / frontier). This is the ONLY server.

**Source of truth and bounded duplication:**
- `core/` stays the proven oracle (191 tests).
- Simple formulas are reimplemented in JS for the browser; a PARITY TEST pins
  `JS == Python` so the two can't drift. Duplication is limited to simple
  formulas only.
- Heavy / data-driven logic is never reimplemented in JS — it runs server-side.

**Deployment topology:**
- GitHub Pages: all static frontend.
- One cloud host (e.g. Render, `render.yaml` already present — needs the user's
  account): the Python service.

**Migration (current → target), in order:**
1. Pin the boundary list: which concepts are browser-JS vs server-Python.
2. One shared JS math module + parity tests vs `core/` (replaces the per-card
   copies). [P1]
3. Deploy the Python service to the cloud so the data labs work by link. [needs host]
4. Point the data labs at the cloud service (not localhost); ship them static.
5. One entry point + navigation across everything.

### Refinement (2026-06-29, user): API-less by default

Push as much as possible client-side; keep the Python API deliberately small —
**one showcase feature** that doubles as a full-stack Python web-app demo.

- The whole product is API-less except that one feature: the deck, the journeys,
  every formula card, and Portfolio / diversification (the deck already does
  diversification from manual inputs) all run in the browser.
- The one API feature: **Stock reverse-DCF on a real ticker**. It is the most
  impressive piece, and live data genuinely needs a server anyway — a browser
  cannot fetch SEC EDGAR or Yahoo / yfinance directly (CORS). So the single live
  feature is exactly where the full-stack Python app belongs: by necessity, not
  vanity.
- Net: one product, reachable by link, with a single live-ticker valuation that
  exists to demonstrate the full-stack Python skill.

## Why this format (from the honest evaluation)

Measured state today:
- Engine + tests: **A** (6,984 LOC, 191 tests green in ~3s, pinned to exams).
- The Money lab: **A−** (clear verdict, felt numbers, honest break-even).
- The deck (53 cards): **B+** (self-contained, deployed, faithful).
- Robustness: **C** (labs show "Calculation failed" without the backend).
- Product coherence: **C−** (deck ≠ app, no link).
- Coverage: **C−** (only ~3 of 5 blocks have live labs).
- Backtest: **D+** (1,260 LOC + results, wired nowhere).

Net: a strong engine and one great demo, not yet a coherent product. The work
ahead is product coherence, robustness, and reach — not engineering rigour.

## A rule we never break

Every number carries its honest limit, in one line. We show the *bet* embedded in
a price or the *trade-off*, never a false "truth". And the headline result must be
**felt** (e.g. "a bad year costs you −22%"), not abstract (e.g. "1.4 effective
bets" — which goes in the footnote).

## The plan (8 steps)

| # | Step | Plain goal | Fixes |
|---|---|---|---|
| P0 | Framing & cleanup | one source-of-truth doc; tidy repo; settle card1 | doc sprawl |
| P1 | Client-side math | pure-math cards work with no server | fragility |
| P2 | Unify into one card product | deck + labs become one app | two products |
| P3 | Decision journeys | group cards into journeys that end in a decision | card1 stepper |
| P4 | "Check" layer | the backtest shows on the relevant cards | orphaned backtest |
| P5 | Accessibility & finish | mobile, plain language, loading states, glossary | ease of use |
| P6 | Frictionless deploy | one automated public deploy (no manual copy) | accessible to all |
| P7 | Full coverage | turn the rest (rates, financing, derivatives) into cards | coverage |

## card1 decision

`frontend/public/card1.html` is essentially the deck's `pv` card (same idea, same
formula `today = future/(1+r)^n`, same split bar), polished and standalone, plus
one new thing: the 4-step stepper. The stepper is the seed of P3 (decision
journeys). Plan: fold card1 into the unified product as the first journey; do not
keep it as a separate app tab (it would be a duplicate).

## Status

- [x] P0 started — this document.
- [ ] P1–P7 — see the task list.
