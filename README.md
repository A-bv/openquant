# OpenQuant

**The EPFL *Principles of Finance* course, made usable on real company data.**

The whole idea is honesty over false precision. OpenQuant never tells you *"this stock is worth $X."* It shows you *"at today's price you're betting on X — do you believe it?"*

---

## What works today

- **🃏 The teaching deck** — the entire course (H1–H4) as **51 interactive cards**: one idea, one picture, one live formula you can drag. It's a single standalone HTML file — no backend, no build. *This is the most complete part of the project.*
  → open `frontend/public/companion.html`, or live at **https://a-bv.github.io/openquant**
- **📊 The real-data layer** — pulls live company numbers from **SEC EDGAR** (financials) and **yfinance** (prices), and is pinned to worked EPFL exam answers in the test suite.

---

## Where it's heading — the live-data "labs"

The goal is to apply each course block to that real data, one tab per block. The engine and tests exist; wiring them into a finished app is the current work.

| Lab | Course block | The question it answers | State |
|---|---|---|---|
| **Money** | H1 · time value of money | Take a lump sum now, or payments over time? | in progress |
| **Portfolio** | H2 · risk & return | N stocks — how many *independent bets*, really? | in progress |
| **Stock** | H3 · valuation | What growth is today's price assuming? (reverse-DCF) | in progress |
| *(none yet)* | **H4 · derivatives** | forwards, options, Black-Scholes | **deck only** |

Every lab follows one pattern: a plain-English result up front, with the depth (formula, live numbers, the EPFL source) one click away.

---

## How it fits together

![OpenQuant architecture: external data feeds a pure-Python core engine, exposed by a thin FastAPI layer, rendered by the React app; the teaching deck is standalone.](docs/openquant-architecture.svg)

`core/` holds the finance math (pure Python, no web dependencies, tested against EPFL exams) · `api/` is a thin FastAPI wrapper · `frontend/` is the React app **plus** the standalone deck. Data comes in from SEC EDGAR + yfinance.

```text
core/         money/ · portfolio/ · valuation/   (one folder per course block)
              + data/ (EDGAR + yfinance) + common/ (shared helpers)
api/          thin main.py + routers/{money,portfolio,stock}.py
frontend/     src/features/{money,stock,portfolio} + src/shared/
              public/companion.html   ← the 51-card deck
tests/        pinned to real EPFL sample-exam answers
```

---

## Run it

```bash
make install     # one-time: Python + frontend deps
make dev         # API on :8000 + app on :5173 together (Ctrl-C stops both)
```

Then open **http://localhost:5173** (the app) — the deck is at **/companion.html**.
`make test` runs the suite.

---

## Deploying

![OpenQuant deployment: pushing to GitHub auto-deploys the app to Vercel and the API to Render; the teaching deck is published manually to GitHub Pages.](docs/openquant-deploy.svg)

The app (Vercel) and API (Render) **auto-deploy on push**. The teaching deck is the only manual step — copy `companion.html` onto the `gh-pages` branch as `index.html`.

---

MIT licensed. Built from the EPFL *Principles of Finance* course (ref. Berk & DeMarzo, *Corporate Finance*).
