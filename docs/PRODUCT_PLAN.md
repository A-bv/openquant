# OpenQuant — Product Plan

Status: active source of truth · updated 2026-07-16

## Product

OpenQuant is a static educational web application that turns corporate-finance
theory into interactive cards and short decision journeys. It teaches what a
model says, lets the reader change its assumptions, and shows where empirical
evidence did not support the theory.

The product must never present a valuation as a prediction or a uniquely true
price. Every important result carries its assumptions and practical limit.

## Repository boundary

This repository is the public static product:

- `site/companion.html`: the 53-card course deck;
- `site/card1.html`: the first guided decision journey;
- `site/theory.html`: the historical reality check;
- `site/finance.js`: reusable browser-side finance formulas;
- `tests/`: parity and static-site contracts.

The Python engine, API, live-data experiments and reproducible backtest live in
the sister repository, [openquant-engine](https://github.com/A-bv/openquant-engine).
References from this site should point to the exact engine revision tested by
CI, not to paths that only existed before the repository split.

## Architecture rules

1. The shipped product remains static and usable without an account or server.
2. Reusable formulas live in `site/finance.js`; cards call them instead of
   reimplementing them.
3. The parity suite compares every exported shared formula with the pinned
   Python engine where an equivalent exists, including failure behavior.
4. Card-specific visual or pedagogical models may remain local to a card, but
   their assumptions must be explicit and they need direct tests before they
   influence a decision headline.
5. Historical claims link to methodology and results at a pinned engine commit.
6. Progressive enhancement is mandatory: content and raw formulas remain
   understandable when optional typesetting is unavailable.

## Product quality bar

- **Correct:** domains, units, sign conventions and edge cases are explicit.
- **Honest:** models expose assumptions, limitations and empirical calibration.
- **Accessible:** semantic HTML, keyboard operation, labelled controls, visible
  focus and WCAG 2.2 AA contrast.
- **Responsive:** primary flows work without horizontal overflow from 320 px.
- **Private:** no account, tracking or transmission of entered values.
- **Reproducible:** dependencies and engine revisions are pinned; CI is the
  documented local workflow.
- **Maintainable:** product copy never describes removed architecture; tests
  enforce the highest-risk documentation and integration contracts.

## Current state

- [x] Static GitHub Pages deployment.
- [x] 53 interactive cards and one four-step journey.
- [x] Historical reality-check page.
- [x] Shared browser finance module used by both interactive surfaces.
- [x] Full export coverage, with Python parity wherever the engine has an equivalent.
- [x] Basic navigation, slider labelling, keyboard steps and 320 px support.
- [x] Pinned development dependencies and SHA-pinned GitHub Actions.
- [ ] KaTeX self-hosted; the current CDN has a raw-text fallback.
- [ ] Browser end-to-end, automated accessibility and visual-regression suites.
- [ ] Card catalogue separated from the monolithic HTML renderer.
- [ ] Historical headline figures generated from a versioned data artifact.

## Next milestones

### M1 — Browser quality gate

- Add Playwright smoke tests for home, one card per chapter and the journey.
- Run axe-core on all four public pages.
- Test 320, 375, 768 and 1280 px viewports.
- Add link and assembled-deployment checks.

### M2 — Maintainable static modules

- Extract the card catalogue into structured JavaScript data.
- Split routing, rendering and visual helpers into native ES modules.
- Keep the deployment output static and framework-free.
- Add direct tests for formulas that remain card-specific.

### M3 — Fully offline and verifiable

- Self-host the pinned KaTeX runtime and stylesheet.
- Generate the reality-check page from a committed summary artifact exported by
  the pinned engine backtest.
- Add a visible methodology/version link beside every empirical headline.

### M4 — Product depth

- Add more decision journeys without duplicating standalone cards.
- Introduce shareable state only when URLs remain readable and stable.
- Measure success through anonymous, optional user research rather than adding
  behavioural tracking by default.
