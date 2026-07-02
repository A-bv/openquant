# OpenQuant

[![CI](https://github.com/A-bv/openquant/actions/workflows/ci.yml/badge.svg)](https://github.com/A-bv/openquant/actions/workflows/ci.yml)

OpenQuant is a hands-on way into the decisions at the heart of corporate finance:
what something is worth, how much return to demand for its risk, which projects
to back, how to finance them, and how derivatives shift risk around.

It never claims the impossible. No screen says "this stock is worth $X". It
shows the bet baked into a price, with its honest limit, and lets you decide
whether you believe it.

## Try it (no install, plain links)

| Page | What it is |
|---|---|
| **[The 53 cards](https://a-bv.github.io/openquant/)** | The whole theory as a deck of interactive cards: one idea, one picture, one live formula each |
| **[Should I take this deal?](https://a-bv.github.io/openquant/card1.html)** | A 4-step decision journey: a lump sum now versus payments over time, and the one rate that flips the answer |
| **[Did the theory hold?](https://a-bv.github.io/openquant/theory.html)** | The valuation theory run on 50 real stocks, 2014 to 2024, against what actually happened |
| **[Project map](https://a-bv.github.io/openquant/app.html)** | Everything built so far, in one page |

## The honest result

The check page above is the project's spine. A reverse-DCF was run on 50 large
US stocks as of January 2014 and compared with realized returns through
January 2024. The stocks it called cheap beat the market less than half the
time, and the ones it called expensive earned more. That is the point: a
valuation is not a crystal ball. It tells you what growth the market is already
paying for, not what happens next.

## How it is built

One rule decides where code runs:

- **Needs live market data** → one small FastAPI service (`api/`), which exists
  to showcase a full Python stack on the single feature that truly needs a
  server: valuing a real ticker from its SEC filings and prices.
- **Everything else** → plain client-side pages that work from a link with no
  server, like the deck.

![OpenQuant architecture](docs/openquant-architecture.svg)

- **`core/`** — the finance engine in plain Python, self-contained (its config
  lives inside the package). No web code.
- **`core/data/`** — the data layer: one module per source (SEC EDGAR for
  filings, yfinance for prices), a file cache, offline sample data, and a
  functional interface (`get_fundamentals`, `get_prices`, ...).
- **`api/`** — a thin FastAPI layer that serves `core/` to the React app.
- **`frontend/public/`** — the self-contained card pages listed above, plus
  `finance.js`, the shared browser math.
- **`frontend/src/`** — the React app for the live-data labs (Money, Stock,
  Portfolio).
- **`backtest/`** — the 2014→2024 study behind the check page.

## Trusted numbers

- **193 offline tests** pin the engine to worked answers from two finance exams
  (`tests/test_epfl_exam1.py`, `test_epfl_exam2.py`), so every formula matches
  the course it teaches.
- **A JS/Python parity test** (`tests/test_js_parity.py`) runs the browser math
  through Node and checks it gives exactly the same answers as `core/`,
  including the failure cases: where Python raises, the browser throws. The two
  implementations cannot drift apart silently.
- CI runs all of it, plus the frontend lint and build, on every push.

## Running it locally

You need Python and Node. From the project root:

```bash
make install     # install the Python and frontend packages
make dev         # run the API (:8000) and the app (:5173) together
make test        # run the offline test suite
```

The card pages need none of this; they are already live at the links above.
Locally they are served at `http://localhost:5173/companion.html`,
`/card1.html`, `/theory.html` and `/app.html`.

## Deploying

- **Card pages**: `.github/workflows/deploy-deck.yml` publishes
  `frontend/public/` to GitHub Pages when those files change on `main`
  (root stays the 53-card deck).
- **API**: `render.yaml` and `Procfile` describe the service for Render.
  Production builds of the React app must set `VITE_API_URL` to the deployed
  API address.

## Docs

`docs/PRODUCT_PLAN.md` is the source of truth for where the product is going.
`docs/openquant_deliverables.md` is the backlog of concrete results. Historical
working drafts live in `docs/archive/`. The current audit lives in `AUDIT.md`.

MIT licensed. The finance follows Berk and DeMarzo, *Corporate Finance*.
