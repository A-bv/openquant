"""
Parity test: the browser math (frontend/public/finance.js) must agree with the
proven Python engine (core/). This is the guardrail of the hybrid architecture —
simple formulas are reimplemented in JS so the cards run with no server, and this
test pins JS == Python so the two can never drift apart.

Runs finance.js through Node and compares to core/. Skipped if Node is absent.
"""

import json
import math
import os
import shutil
import subprocess
import tempfile

import pytest

from core.valuation.dcf import DCFEngine
from core.valuation.wacc import capm_cost_of_equity

FINANCE_JS = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "frontend", "public", "finance.js")
)

pytestmark = pytest.mark.skipif(
    shutil.which("node") is None, reason="Node.js not installed; cannot run JS parity"
)


def _run_js(calls: dict) -> dict:
    """calls: name -> [jsFunctionName, [args...]]. Returns name -> numeric result.

    finance.js lives under frontend/ whose package.json is "type": module, so
    Node would load it as ESM. Copy it to a .cjs file (always CommonJS) so its
    module.exports works and we can require it.
    """
    with open(FINANCE_JS) as f:
        src = f.read()
    fd, tmp = tempfile.mkstemp(suffix=".cjs")
    try:
        with os.fdopen(fd, "w") as out:
            out.write(src)
        script = (
            "const F=require(process.argv[1]);"
            "const calls=JSON.parse(process.argv[2]);"
            "const out={};for(const k in calls){const c=calls[k];out[k]=F[c[0]](...c[1]);}"
            "process.stdout.write(JSON.stringify(out));"
        )
        res = subprocess.run(
            ["node", "-e", script, tmp, json.dumps(calls)],
            capture_output=True, text=True, check=True,
        )
        return json.loads(res.stdout)
    finally:
        os.unlink(tmp)


def _engine() -> DCFEngine:
    # The formula methods are pure (use only their args), so bypass __init__.
    return DCFEngine.__new__(DCFEngine)


def test_js_matches_core_python():
    eng = _engine()
    cf_npv = [-24000, 8400, 9150, 11100, 14850]
    cf_irr = [-5000, 3600, 3600]

    js = _run_js({
        "pv":               ["pv",                [1000, 0.08, 6]],
        "annuityPV":        ["annuityPV",         [1000, 0.05, 10]],
        "perpetuity":       ["perpetuity",        [1000, 0.05]],
        "growingAnnuityPV": ["growingAnnuityPV",  [400, 0.075, 0.04, 18]],
        "growingPerpetuity":["growingPerpetuity", [1000, 0.06, 0.02]],
        "npv":              ["npv",               [0.20, cf_npv]],
        "irr":              ["irr",               [cf_irr]],
        "capm":             ["capm",              [0.08, 1.5, 0.08]],
        "ddm":              ["ddm",               [2, 0.08, 0.02]],
        "bondPrice":        ["bondPrice",         [5, 100, 0.04, 10]],
        "ear":              ["ear",               [0.18, 12]],
    })

    # Each JS formula pinned to a core/ (Python) computation of the same thing.
    assert math.isclose(js["pv"],                eng.npv([0] * 6 + [1000], 0.08),        rel_tol=1e-9)
    assert math.isclose(js["annuityPV"],         eng.growing_annuity_pv(1000, 0.05, 0.0, 10), rel_tol=1e-9)
    assert math.isclose(js["perpetuity"],        eng.growing_perpetuity_pv(1000, 0.05, 0.0), rel_tol=1e-9)
    assert math.isclose(js["growingAnnuityPV"],  eng.growing_annuity_pv(400, 0.075, 0.04, 18), rel_tol=1e-9)
    assert math.isclose(js["growingPerpetuity"], eng.growing_perpetuity_pv(1000, 0.06, 0.02), rel_tol=1e-9)
    assert math.isclose(js["npv"],               eng.npv(cf_npv, 0.20),                  rel_tol=1e-9)
    assert math.isclose(js["irr"],               eng.irr(cf_irr),                        rel_tol=1e-6)
    assert math.isclose(js["capm"],              capm_cost_of_equity(0.08, 1.5, 0.08),   rel_tol=1e-12)
    assert math.isclose(js["ddm"],               eng.growing_perpetuity_pv(2, 0.08, 0.02), rel_tol=1e-9)
    # A bond is the NPV of its coupon stream plus face at maturity.
    bond_cf = [0] + [5] * 9 + [5 + 100]
    assert math.isclose(js["bondPrice"],         eng.npv(bond_cf, 0.04),                 rel_tol=1e-9)
    # EAR has no standalone core function; pin to its textbook closed form.
    assert math.isclose(js["ear"],               (1 + 0.18 / 12) ** 12 - 1,              rel_tol=1e-12)
