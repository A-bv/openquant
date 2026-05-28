# OpenQuant

Financial valuation and value enhancement through real company data.

OpenQuant is the practical application of the finance course objective:

> introduce students to financial valuation and value enhancement through
> financial decision making.

The course is likely based on Jonathan Berk and Peter DeMarzo,
*Corporate Finance*, Pearson, 2nd ed., 2010. OpenQuant applies the
corporate-finance side of that course to real listed-company data.

It does not try to be a Bloomberg clone, a generic DCF calculator, or a
buy/sell recommendation engine. It answers one practical question:

> What must be true for the current market price to make sense?

Formulas such as FCF, CAPM, WACC, DCF, reverse DCF, sensitivity analysis, and
exam-style checks are tools used to support that question. They are not the
product by themselves.

## What OpenQuant Does

| Area | Status |
|---|---|
| Listed-company valuation using real data | Productized |
| Market-implied expectations / reverse DCF | Productized |
| DCF scenarios and sensitivity | Productized |
| WACC/CAPM inputs needed for valuation | Productized inside stock analysis |
| Formula correctness against sample-exam style answers | Implemented as tests |
| Historical backtest reliability summary | Productized in the app |

## What OpenQuant Does Not Do

| Area | Status |
|---|---|
| Derivatives | Out of scope today |
| Bonds and rates lab | Not productized |
| Portfolio lab | Not productized |
| Project decision lab | Not productized |
| Full capital-structure policy lab | Not productized |
| Buy/sell recommendations | Not a goal |

## Backtest Result

Backtests are implemented in code, not as a long Markdown report. The app shows
only the main reliability results.

Historical validation ran OpenQuant's listed-company valuation flow as of
January 2014 and compared the conclusions with realized outcomes through
January 2024.

| Metric | Result |
|---|---:|
| Backtest universe | 50 stocks |
| Successful historical runs | 33 stocks |
| Calibration regression R² | 0.038 |
| Regression slope | 0.002 |
| "Undervalued" bucket realized return | 12.3%/yr |
| "Overvalued" bucket realized return | 13.6%/yr |
| S&P 500 baseline | 12.1%/yr |

Interpretation: the finance formulas are tested, but the current
stock-valuation signal is not calibrated as a reliable predictor of realized
returns. OpenQuant is useful for making assumptions, valuation logic, and model
limits visible.

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
└── docs/                 supporting scope/specification material
```

## Verification

```bash
pytest -q --ignore=tests/test_edgar_live.py
```

The offline suite verifies formula implementations, regression fixes, and the
main backtest metrics. Live EDGAR tests are kept separate because they depend
on network access to SEC data.

## License

MIT.
