.PHONY: serve test

serve:          ## preview the site locally on http://localhost:5173
	cd site && python3 -m http.server 5173

test:           ## parity: site/finance.js must equal the engine (pip install openquant-engine first)
	python -m pytest -q tests/
