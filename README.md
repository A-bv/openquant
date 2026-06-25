# OpenQuant

OpenQuant is a hands-on way into the core ideas of finance: what a future dollar is worth today, how risk trades off against return, and what a company is actually worth.

Today it is a deck of **53 cards**. Each card explains one idea with a picture, then lets you drag the numbers in its formula and watch the result change.

Try it live at **https://a-bv.github.io/openquant**, or open `frontend/public/companion.html`.

## Applying it to real companies (in progress)

The other half of the project points that same theory at real companies, using live data: company filings from **SEC EDGAR** and prices from **Yahoo Finance**.

You can't predict the future. But you can take the theory as far as it goes, work out what it implies, and then judge whether that holds up. Three tools are taking shape, each from one part of the theory:

| Tool | What it works out |
|---|---|
| **Money** | Take all the money now, or smaller amounts spread over many years? Which is really worth more? |
| **Portfolio** | You own a dozen stocks and feel spread out. But if they tend to rise and fall together, that is closer to one big bet than twelve. How spread out are you really? |
| **Stock** | Today's price already assumes a future. This works out which future, so you can decide whether you believe it. |

This half isn't finished. The options part of the theory, for now, lives only in the cards.

## How it is built

![OpenQuant architecture](docs/openquant-architecture.svg)

- **`frontend/`**: the React app, plus the standalone card deck (`public/companion.html`).
- **`core/`**: the finance math in plain Python, with no web code, checked against worked exam answers.
- **`api/`**: a thin FastAPI layer that serves `core/` to the app.

## Running it locally

You need Python and Node. From the project root:

```bash
make install     # install the Python and frontend packages
make dev         # run the API and the app together
```

This is only for working on the project; the cards are already live at the link above. Once it starts, the app is at `http://localhost:5173` and the cards at `http://localhost:5173/companion.html`. `make test` runs the checks.

## Deploying

Push to `main` and everything ships on its own, no manual steps:

- the **app** redeploys to **Vercel**,
- the **API** redeploys to **Render**,
- the **card deck** republishes to **GitHub Pages** via a GitHub Action (`.github/workflows/deploy-deck.yml`) whenever `companion.html` changes.

MIT licensed. The finance follows Berk and DeMarzo, *Corporate Finance*.
