# OpenQuant

OpenQuant brings corporate finance out of the classroom and applies it to real
listed companies.

It is built from the EPFL Introduction to Finance course, with reference to
Jonathan Berk and Peter DeMarzo, *Corporate Finance*, Pearson, 2nd ed. Its
purpose is to make financial valuation and value-enhancing decisions concrete.

OpenQuant makes that goal practical: enter a ticker, inspect the company
through real data, and see what the market price requires you to believe about
value creation.

It is a Python-powered web app that can be tested live online on real US market
data, or cloned and run locally.

Data comes from SEC EDGAR for company financials and yfinance for market prices
and historical returns.

Course/formula coverage is tracked in `docs/openquant_scope_table.xlsx`.

## Run Locally

```bash
git clone https://github.com/A-bv/openquant
cd openquant
pip install -r requirements.txt
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000
```

In another terminal:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` and enter a US ticker.

API example:

```bash
curl -X POST http://localhost:8000/analyse \
  -H 'Content-Type: application/json' \
  -d '{"ticker":"AAPL"}'
```

Backtest reliability summary:

```bash
curl http://localhost:8000/calibration
```

## Architecture

```text
openquant/
├── api/                  FastAPI endpoints
├── core/                 finance logic, no web dependencies
├── backtest/             historical as-of validation pipeline
├── backtest/results/     raw backtest CSV and calibration summary JSON
├── frontend/             React app
├── tests/                formula, regression, and backtest metric tests
└── docs/                 scope and course-coverage material
```

## Verification

```bash
pytest -q --ignore=tests/test_edgar_live.py
```

The offline suite verifies formula implementations, regression fixes, and the
main backtest metrics. Live EDGAR tests are separate because they depend on
network access to SEC data.

## License

MIT.
