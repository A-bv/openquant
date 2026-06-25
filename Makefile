.PHONY: install dev api web test

install:        ## one-time: install Python + frontend deps
	pip install -r requirements.txt
	cd frontend && npm install

dev:            ## run API (:8000) and app (:5173) together; Ctrl-C stops both
	@trap 'kill 0' EXIT; \
	python -m uvicorn api.main:app --host 127.0.0.1 --port 8000 & \
	( cd frontend && npm run dev ) & \
	wait

api:            ## run only the API on :8000
	python -m uvicorn api.main:app --host 127.0.0.1 --port 8000

web:            ## run only the frontend on :5173
	cd frontend && npm run dev

test:           ## run the offline test suite (EPFL exam oracles included)
	pytest -q --ignore=tests/test_edgar_live.py
