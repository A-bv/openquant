.PHONY: install serve test site-test engine-test engine-lint engine-dev

PYTHON ?= python3

install:        ## install the Python engine, test tools, and React dependencies
	$(PYTHON) -m pip install -e "./engine[api,dev]"
	cd engine/app && npm ci

serve:          ## preview the site locally on http://localhost:5173
	cd site && $(PYTHON) -m http.server 5173

test: site-test engine-test ## run every offline Python and browser-parity test

site-test:      ## static contracts and browser math == local Python engine
	$(PYTHON) -m pytest -q tests/

engine-test:    ## engine exam oracles and API tests (no live network calls)
	cd engine && $(PYTHON) -m pytest -q -m "not live"

engine-lint:    ## lint and type-check the Python engine; lint the React labs
	cd engine && ruff check . && mypy
	cd engine/app && npm run lint

engine-dev:     ## run the API on :8000 and React labs on :5173
	$(MAKE) -C engine dev
