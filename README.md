# OpenQuant

[![CI](https://github.com/A-bv/openquant/actions/workflows/ci.yml/badge.svg)](https://github.com/A-bv/openquant/actions/workflows/ci.yml)
[![Live site](https://img.shields.io/badge/live-a--bv.github.io%2Fopenquant-2ea44f)](https://a-bv.github.io/openquant/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

Corporate finance you can actually act on: the whole theory as **interactive
cards**, guided **decision journeys**, and one honest question — *did the
theory hold on ten years of real returns?*

Everything runs in your browser. There is no server, no account, no install:
every page below is a plain link.

## Try it

| Page | What it is |
|---|---|
| **[The 53 cards](https://a-bv.github.io/openquant/)** | The whole theory as a deck of interactive cards: one idea, one picture, one live formula each |
| **[Should I take this deal?](https://a-bv.github.io/openquant/card1.html)** | A 4-step decision journey: a lump sum now versus payments over time, and the one rate that flips the answer |
| **[Did the theory hold?](https://a-bv.github.io/openquant/theory.html)** | The valuation theory run on 50 real stocks, 2014 → 2024, against what actually happened |
| **[Project map](https://a-bv.github.io/openquant/app.html)** | Everything in one page |

## The honest result

The theory says a valuation reveals whether a stock is cheap. So it was run on
50 large US stocks as of January 2014 and checked against reality in 2024: the
stocks it called *cheap* beat the market **less than half the time**, and the
ones it called *expensive* earned more. That is the site's whole stance — a
valuation tells you **the bet baked into a price**, never the future. No page
here ever claims "this stock is worth $X".

## How it works

- Everything under [`site/`](site/) is static HTML, CSS, JavaScript and bundled
  fonts. It can be opened locally or served by any static host. The two
  interactive pages use [KaTeX](https://katex.org) from a CDN for typesetting;
  if it is unavailable, the formulas remain visible as raw text.
- Reusable browser math lives in [`site/finance.js`](site/finance.js). Both the
  53-card deck and the guided journey call this module for the core formulas;
  card-specific visual models stay close to their cards.
- Every exported shared formula is exercised by
  [`tests/test_js_parity.py`](tests/test_js_parity.py), which runs the JavaScript
  through Node and compares the applicable calculations and failure behavior
  with the pinned [**openquant-engine**](https://github.com/A-bv/openquant-engine)
  revision. The sister repository contains the Python engine, its exam-pinned
  suite, the API, live-ticker labs and backtest.
- Pushing to `main` republishes the site automatically
  ([`deploy-deck.yml`](.github/workflows/deploy-deck.yml)).

```
site/        the product: 53-card deck, journeys, the honest check, shared math
tests/       one suite: browser math == engine math
docs/        the product plan, course notes, and the archive
```

## Run it locally

```bash
make serve        # http://localhost:5173 — plain static serving, nothing else
```

To run the parity and site-contract suites, install the pinned development
dependencies and run the tests:

```bash
pip install -r requirements-dev.txt
make test
```

The engine is pinned to a commit and CI installs the same file. Bump the ref
deliberately when adopting a newer engine.

## The numbers behind the "did it hold?" page

They come from the backtest committed in the engine repo
([`backtest/`](https://github.com/A-bv/openquant-engine/tree/7ab97a8bf6ca3c327bc80743e032f894b6d81522/backtest)),
run on SEC EDGAR filings and market prices. Nothing on the page is illustrative;
every figure traces to that study.

MIT licensed. The finance follows Berk & DeMarzo, *Corporate Finance*.
