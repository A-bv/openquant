# OpenQuant — Portfolio-Grade Audit

Date: 2026-07-02 · Auditor: staff-engineer pass (inline, single-agent; adversarial
multi-agent pass unavailable — session limit) · Scope: branch `codex/stock-lab-progressive`,
working tree dirty only at `api/main.py` (deliberate, in-flight CORS prep).

## Ground truth (all verified by running them)

| Check | Result |
|---|---|
| `pytest -m "not live"` | **192 passed**, 6 deselected, ~1.2s |
| `vite build` | passes; warning: main chunk **658 kB** (recharts) |
| `eslint .` (frontend) | clean |
| `git status` | only `api/main.py` modified (deliberate); no junk tracked |
| Node v24.1.0, npm 11.3.0, Python 3.13.3 | — |

What this is: a hybrid product — static, client-side finance card pages
(`frontend/public/*.html` + `finance.js`) published to GitHub Pages, a React SPA
for live-ticker labs (needs FastAPI backend), a Python engine (`core/`) pinned to
EPFL exam answers, and an already-computed backtest. Architecture of record:
`docs/PRODUCT_PLAN.md` (live data → one small API; everything else API-less).

## 1. Verdict

The foundations are stronger than the packaging: a 192-test engine pinned to
worked exam answers, an honest backtest surfaced as a product page, and a written
architecture that the code mostly follows. But the repo currently fails the
"check any claim" test a reviewer will run in the first five minutes: the
README's deploy section describes a GitHub Action that **does not exist**, no CI
runs the impressive test suite, `core/` cannot be installed standalone because
every module imports a root-level `config.py`, and the flagship "parity-tested"
browser math returns **silent wrong answers** on IRR edge cases. Nothing here is
architecturally rotten — the gaps are concentrated at the trust boundary between
what the repo *says* and what it *provably does*. All of it is fixable in a day.

## 2. Findings (deep → shallow)

### L0 — Foundation

**F1 · `core/` is coupled to root-level `config.py` — not packageable**
FIX-BEFORE-MERGE · [L0 · Works→Senior] · (Observed)
15 imports of `from config import …` across `core/` (`core/common/utils.py:16`,
`core/portfolio/portfolio.py:32`, `core/data/cache.py:22`, all of
`core/valuation/*`, both providers). `import config` only resolves when the CWD
is the repo root — `core/` can't be pip-installed or reused, which contradicts
both the extraction work already done (P1b) and PRODUCT_PLAN's "clean importable
data layer".
→ Fix: move `config.py` → `core/config.py`; keep a root `config.py` shim
(`from core.config import *`) so `api/`, `backtest/`, `scripts/` keep working.
Mechanical, test-guarded.

**F2 · Money lab violates the architecture of record**
FOLLOW-UP · [L0 · Works→Correct] · (Observed)
`api/routers/money.py:20` imports `core.money`; `App.jsx` POSTs to `/now-or-later`.
Pure arithmetic with no market data round-trips through the server — the exact
pattern PRODUCT_PLAN retires ("API-less by default"). Known, planned P1 work;
listed so it isn't lost.
→ Fix: drive `NowOrLaterLab` from shared client-side math (`finance.js`), retire
the endpoint after.

### L1 — Behavior

**F3 · `finance.js` `irr()` returns silent wrong answers on edge cases**
FIX-BEFORE-MERGE · [L1 · Works→Correct] · (Observed — executed)
`irr([-100, 250])` → `1.0` (true answer 1.5; bisection bracket hard-capped at
`hi=1.0`). `irr([100, 100])` (no root exists) → `1.0` instead of failing.
Python `core` raises `ValueError` in both regimes (`dcf.py:496` brackets to 10.0
and raises on no-sign-change). The file's entire premise is "parity with core/";
the 11-case parity test pins only happy paths.
→ Fix: widen bracket to match core (10.0), add a no-sign-change guard that
throws, extend `tests/test_js_parity.py` with edge pins (high-IRR, no-root,
r==g).

**F4 · `growingAnnuityPV(r == g)`: JS returns a value, Python raises**
FOLLOW-UP · [L1 · Works→Correct] · (Observed — executed)
JS returns `952.38` (the correct N·C/(1+r) limit) where
`core/valuation/dcf.py:602` raises `ValueError`. Divergent *behavior* (the JS
value is mathematically right). Either align JS to throw, or accept the limit in
both and pin it in the parity test. Pick one; document it.

**F5 · `providers/prices.py` double-wraps its own error**
DON'T-BLOCK · [L1 · Works→Correct] · (Observed)
The `raise DataFetchError("No price data …")` inside the `try` is caught by the
trailing `except Exception as e:` and re-wrapped as "Price fetch failed …".
Harmless but sloppy error text.
→ Fix: `except DataFetchError: raise` before the broad catch (or move the raise
out of the try).

### L2 — Surface (what others read and depend on)

**F6 · README "Deploying" section is false**
FIX-BEFORE-MERGE · [L2 · Broken→Showcase] · (Observed)
README claims "Push to `main` and everything ships on its own" and cites
`.github/workflows/deploy-deck.yml`. **There is no `.github/` directory at all.**
The gh-pages publish is a manual worktree dance (performed by hand three times
this session). Vercel/Render auto-deploys are unverifiable from the repo. A
reviewer checks this in ten seconds and every other claim loses credibility.
→ Fix: rewrite README to the truth (user has asked for full README restructure
as the closing step).

**F7 · Zero CI**
FIX-BEFORE-MERGE · [L2 · Works→Showcase] · (Observed)
No `.github/` → the 192-test suite, the JS-parity test, eslint and the build run
only on developer machines. For a portfolio repo the green Actions badge *is*
the proof of quality.
→ Fix: add `.github/workflows/ci.yml` (pytest offline + frontend build + eslint).
Optionally a second workflow to publish `frontend/public/` to gh-pages — which
would make the README's deploy claim *true* instead of deleting it.

**F8 · No LICENSE file, README says "MIT licensed"**
FIX-BEFORE-MERGE · [L2 · Broken→Works] · (Observed)
`ls LICENSE*` → nothing. Legally the code is all-rights-reserved today.
→ Fix: add MIT `LICENSE`.

**F9 · CORS: `allow_credentials=True` + any-`*.github.io` origin regex**
FOLLOW-UP · [L2 · Works→Senior] · (Observed, incl. the uncommitted widening)
`api/main.py:24-40`. No cookies/auth exist, so exploitability is ~nil today, but
credentials+wildcard-ish origins is a foot-gun and reads junior. The widened
regex admits *any* GitHub Pages site, not just this project's.
→ Fix: narrow to `a-bv\.github\.io`, drop `allow_credentials`, then commit the
in-flight change.

**F10 · Docs sprawl: 66 KB of stale drafts presented alongside the source of truth**
FOLLOW-UP · [L2 · Works→Senior] · (Observed)
Root: `COURSE_TO_PRODUCT_MAP.md` (16 KB). `docs/`: `phase1_tsla_sketch.md`
(18 KB), `phase1_tsla_sketch_v3.md` (21.5 KB), `blog_draft.md` (10.7 KB),
`backtest_plan.md` (9.7 KB). PRODUCT_PLAN names some as historical, but a
newcomer cannot tell current from archaeology.
→ Fix: `docs/archive/` for drafts; root keeps only README (+ AUDIT while open).

**F11 · `requirements.txt` fully unpinned (14 × `>=`)**
FOLLOW-UP · [L2 · Works→Senior] · (Observed)
Non-reproducible builds; a future pandas/scipy major can break the exam oracles.
→ Fix: pin exact versions (or add a constraints/lock file) and let CI prove them.

**F12 · React app's API fallback is wrong for its own target deployment**
FOLLOW-UP · [L2 · Works→Correct] · (Observed)
`App.jsx:27-31`: without `VITE_API_URL`, falls back to
`window.location.hostname:8000` — on any static host that's garbage
(`a-bv.github.io:8000`). Fine locally, wrong by design for the plan's "static
build + cloud API".
→ Fix: require `VITE_API_URL` in production builds (fail loud), keep localhost
fallback for dev only.

**F13 · Makefile `test` disagrees with pytest markers**
DON'T-BLOCK · [L2 · Works→Senior] · (Observed)
`make test` uses `--ignore=tests/test_edgar_live.py` while the suite's own
convention is `-m "not live"` (pytest.ini defines the marker). Two definitions of
"offline suite".
→ Fix: `pytest -q -m "not live"` in the Makefile.

### L3 — Polish

**F14 · Dead code: unreachable `return None` in `providers/edgar.py`**
DON'T-BLOCK · [L3] · (Observed — file tail)
`extract_annual_series` ends `return max(...)` followed by `return None`
(carried over verbatim from the pre-extraction file).
→ Fix: delete the line.

**F15 · Main bundle 658 kB (recharts, single chunk)**
DON'T-BLOCK · [L3] · (Observed — build warning)
Acceptable for a demo SPA; code-split if the React app becomes a first-class
deliverable.

**F16 · Static pages duplicate `:root` CSS vars + nav bar ×4**
DON'T-BLOCK · [L3 · taste, accepted trade-off] · (Observed)
Self-contained pages are the stated design (deployable-anywhere); the cost is a
4-file edit for any nav/theme change. Accepted for now; revisit only if page
count grows. `companion.html`'s 53 cards also still carry inline math not yet
delegated to `finance.js` (planned P1; only `card1.html` is wired).

### Verified fine (no finding — checked, not skipped)

- `theory.html` hardcoded numbers vs `backtest/results/calibration_summary.json`:
  **all six figures faithful** (44% hit rate, 12.3/13.6/8.8 %/yr, R²≈0.04, 50/33).
- `api/sanitize.py` NaN/Inf handling: clean, recursive, correct.
- No bare `except:` anywhere; the 8 `except Exception` sites are boundary wraps
  that re-raise typed errors (minus F5's wart).
- `.gitignore` covers `.DS_Store`, caches, `infoSource/` (copyright) — nothing
  sensitive tracked.
- Git history: readable, plain-language, one-topic commits.

## 3. Ranked action queue (fix order)

1. **F1** config.py → core/config.py + shim (L0, mechanical, test-guarded)
2. **F3** finance.js IRR guards + edge parity pins (L1, silent-wrong-answer)
3. **F7** CI workflow: pytest + parity + eslint + build (L2, makes quality provable)
4. **F8** LICENSE (MIT) (L2, 1 min)
5. **F9** CORS narrow + drop credentials + commit in-flight change (L2)
6. **F4** r==g divergence: align + pin (L1 small)
7. **F12** fail-loud VITE_API_URL in prod builds (L2)
8. **F11** pin requirements (L2)
9. **F10** docs/archive/ sweep (L2)
10. **F13** Makefile ↔ marker consistency (L2 small)
11. **F5** prices.py error double-wrap (L1 small)
12. **F14** delete dead line (L3)
13. **F6 README rewrite — deliberately LAST** per user instruction (cleanup +
    restructure once the above makes every claim true)
14. **F2** Money lab client-side (FOLLOW-UP, planned P1 — do after this queue)

## 4. Single highest-leverage change

**CI (F7).** One workflow file turns "trust me, 192 tests pass" into a green
badge on every push, guards the parity contract (F3's fix) forever, and is the
prerequisite for making the README's deploy story honest (F6). Everything else
in the queue gets locked in by it.

## 5. Showcase readiness

**Already reads portfolio-grade:** the EPFL-exam-pinned test oracle (192 tests,
~1s, offline), the honest "did the theory hold?" backtest page, the provider
extraction with offline fixtures + self-check, a written architecture decision
(PRODUCT_PLAN) the code actually follows, clean plain-language git history.

**Top 3 gaps blocking showcase:**
1. **Claims ≠ reality** — false deploy section, missing LICENSE, no CI to prove
   the tests (F6/F7/F8).
2. **`core/` not installable** — root config coupling undermines the "engine as
   a real package" story (F1).
3. **Parity promise with silent edge failures** — the one file whose job is
   correctness-by-construction can return wrong numbers without erroring (F3).

## Ongoing issues (in-flight, not code defects)

- `theory.html` is committed but **404 live** — three publish attempts blocked by
  a transient safety-classifier outage. Retry pending.
- `api/main.py` CORS widening uncommitted — superseded by F9 (narrow, then commit).
- Stock showcase deploy to Render — awaiting the user's hosting account
  (render.yaml + Procfile ready; CORS prep done).
- Multi-agent adversarial audit pass — unavailable this session (subagent limit,
  resets 16:10 Europe/Paris); this audit is the inline single-agent pass.
