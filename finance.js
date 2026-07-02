/*
 * OpenQuant — shared finance math (the browser side of core/).
 *
 * Pure formulas, no data, no network. Every formula-card and journey uses these
 * instead of re-implementing the math inline. A parity test (tests/test_js_parity.py)
 * runs these through Node and compares them to core/ (Python), so the browser
 * math and the proven Python engine can never drift apart.
 *
 * Works in the browser (global `Finance`) and in Node (module.exports).
 */
(function (root) {
  "use strict";

  // Time value of money
  function pv(futureValue, rate, periods) {
    return futureValue / Math.pow(1 + rate, periods);
  }
  function fv(presentValue, rate, periods) {
    return presentValue * Math.pow(1 + rate, periods);
  }
  function perpetuity(cashflow, rate) {
    return cashflow / rate;
  }
  function growingPerpetuity(cashflow, rate, growth) {
    return cashflow / (rate - growth);
  }
  function annuityPV(cashflow, rate, periods) {
    if (rate === 0) return cashflow * periods;
    return (cashflow / rate) * (1 - 1 / Math.pow(1 + rate, periods));
  }
  // rate === growth throws, mirroring core/valuation/dcf.py (the closed form
  // degenerates; the caller must use periods * cashflow / (1 + rate) explicitly).
  function growingAnnuityPV(cashflow, rate, growth, periods) {
    if (rate === growth) {
      throw new Error(
        "growingAnnuityPV is undefined for rate == growth; use periods * cashflow / (1 + rate) for that limit"
      );
    }
    return (cashflow / (rate - growth)) *
      (1 - Math.pow((1 + growth) / (1 + rate), periods));
  }

  // Project decisions
  // cashflows[t] is the cash at period t; index 0 is "today".
  function npv(rate, cashflows) {
    var s = 0;
    for (var t = 0; t < cashflows.length; t++) {
      s += cashflows[t] / Math.pow(1 + rate, t);
    }
    return s;
  }
  // Bracket and failure semantics mirror core/valuation/dcf.py irr():
  // search [-99%, 1000%], and throw when the bracket holds no root instead of
  // silently returning the bracket edge.
  function irr(cashflows) {
    var lo = -0.99, hi = 10.0;
    var fLo = npv(lo, cashflows), fHi = npv(hi, cashflows);
    if (fLo === 0) return lo;
    if (fHi === 0) return hi;
    if ((fLo > 0) === (fHi > 0)) {
      throw new Error(
        "IRR not found in [-99%, 1000%]; cash flow series may have no real root or multiple sign changes"
      );
    }
    for (var i = 0; i < 200; i++) {
      var mid = (lo + hi) / 2, fMid = npv(mid, cashflows);
      if ((fMid > 0) === (fLo > 0)) { lo = mid; fLo = fMid; } else { hi = mid; }
    }
    return (lo + hi) / 2;
  }

  // Rates and bonds
  function ear(apr, compoundsPerYear) {
    return Math.pow(1 + apr / compoundsPerYear, compoundsPerYear) - 1;
  }
  function loanPayment(principal, ratePerPeriod, periods) {
    return (principal * ratePerPeriod) / (1 - Math.pow(1 + ratePerPeriod, -periods));
  }
  function bondPrice(coupon, face, yieldRate, periods) {
    return annuityPV(coupon, yieldRate, periods) + face / Math.pow(1 + yieldRate, periods);
  }
  function ytm(price, coupon, face, periods) {
    var lo = 1e-9, hi = 10.0;
    var f = function (y) { return bondPrice(coupon, face, y, periods) - price; };
    var fLo = f(lo), fHi = f(hi);
    if ((fLo > 0) === (fHi > 0)) {
      throw new Error("YTM not found in (0%, 1000%]; no yield matches this price");
    }
    for (var i = 0; i < 200; i++) {
      var mid = (lo + hi) / 2, fMid = f(mid);
      if ((fMid > 0) === (fLo > 0)) { lo = mid; fLo = fMid; } else { hi = mid; }
    }
    return (lo + hi) / 2;
  }

  // Risk and return
  function capm(riskFree, beta, marketPremium) {
    return riskFree + beta * marketPremium;
  }
  function ddm(nextDividend, rate, growth) {
    return nextDividend / (rate - growth);
  }
  // Effective number of independent bets: n / (1 + (n-1)·rho)
  function effectiveBets(n, rho) {
    return n / (1 + (n - 1) * rho);
  }

  var Finance = {
    pv: pv,
    fv: fv,
    perpetuity: perpetuity,
    growingPerpetuity: growingPerpetuity,
    annuityPV: annuityPV,
    growingAnnuityPV: growingAnnuityPV,
    npv: npv,
    irr: irr,
    ear: ear,
    loanPayment: loanPayment,
    bondPrice: bondPrice,
    ytm: ytm,
    capm: capm,
    ddm: ddm,
    effectiveBets: effectiveBets,
  };

  /* global module */
  if (typeof module !== "undefined" && module.exports) {
    module.exports = Finance;       // Node (used by the parity test)
  } else {
    root.Finance = Finance;         // Browser
  }
})(typeof self !== "undefined" ? self : this);
