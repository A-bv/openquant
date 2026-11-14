# Monorepo migration

OpenQuant's static course and Python engine originally lived in two GitHub
repositories. The engine history is now merged into this repository under
`engine/`; no source history was squashed.

## Canonical layout

- `site/` — static course and decision journeys
- `tests/` — site contracts and JavaScript/Python formula parity
- `engine/openquant/` — installable Python package
- `engine/api/` — FastAPI service
- `engine/app/` — React live-ticker labs
- `engine/backtest/` — historical study and committed results

## Cutover sequence

1. Merge the monorepo branch only after both CI jobs pass.
2. Confirm the unified Pages deployment serves the course at `/openquant/`
   and the labs at `/openquant/labs/`.
3. Rebuild the Hugging Face Space with `engine/deploy/hf/` and confirm
   `/health` plus the browser labs.
4. Update the old `openquant-engine` repository description with a migration
   notice and archive it. Keep its Pages deployment temporarily as a redirect
   if existing links still receive traffic.

The old repository must not be archived before step 3: its Docker build was
the source of the live API before this migration.
