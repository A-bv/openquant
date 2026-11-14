# OpenQuant

[![CI](https://github.com/A-bv/openquant/actions/workflows/ci.yml/badge.svg)](https://github.com/A-bv/openquant/actions/workflows/ci.yml)
[![Live site](https://img.shields.io/badge/live-a--bv.github.io%2Fopenquant-2ea44f)](https://a-bv.github.io/openquant/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

Corporate finance you can actually act on: the whole theory as **interactive
cards**, guided **decision journeys**, and one honest question — *did the
theory hold on ten years of real returns?*

The course runs entirely in your browser. The live-ticker labs use the Python
engine and its FastAPI service; there is no account or paid dependency.

## Try it

| Page | What it is |
|---|---|
| **[The 53 cards](https://a-bv.github.io/openquant/)** | The whole theory as a deck of interactive cards: one idea, one picture, one live formula each |
| **[Should I take this deal?](https://a-bv.github.io/openquant/card1.html)** | A 4-step decision journey: a lump sum now versus payments over time, and the one rate that flips the answer |
| **[Did the theory hold?](https://a-bv.github.io/openquant/theory.html)** | The valuation theory run on 50 real stocks, 2014 → 2024, against what actually happened |
| **[Live-ticker labs](https://a-bv.github.io/openquant/labs/)** | Reverse-DCF, diversification, and time-value-of-money tools backed by the API |
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
  with the local [`engine/`](engine/) package.
- [`engine/`](engine/) contains the Python engine, its exam-pinned suite, the
  FastAPI service, React labs, and the historical backtest. Its original Git
  history was retained when the repositories were consolidated.
- Pushing to `main` republishes the site automatically
  ([`deploy-deck.yml`](.github/workflows/deploy-deck.yml)).

```
site/        53-card course, journeys, honest check, and shared browser math
tests/       static-site contracts and JavaScript ↔ Python parity
engine/      Python engine, API, React labs, backtest, and exam-pinned tests
docs/        product plan, course notes, and archive
```

## Run it locally

```bash
make install      # engine, Python test tools, and React dependencies
make serve        # static course on http://localhost:5173
make engine-dev   # API on :8000 and React labs on :5173
make test         # all offline engine, API, site, and parity tests
make engine-lint  # ruff, mypy, and ESLint
```

## The numbers behind the "did it hold?" page

They come from the committed [`engine/backtest/`](engine/backtest/),
run on SEC EDGAR filings and market prices. Nothing on the page is illustrative;
every figure traces to that study.

MIT licensed. The finance follows Berk & DeMarzo, *Corporate Finance*.
