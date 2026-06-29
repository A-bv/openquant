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
  function growingAnnuityPV(cashflow, rate, growth, periods) {
    if (rate === growth) return (cashflow * periods) / (1 + rate);
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
  function irr(cashflows) {
    var lo = -0.99, hi = 1.0;
    for (var i = 0; i < 200; i++) {
      var mid = (lo + hi) / 2;
      if (npv(mid, cashflows) > 0) lo = mid; else hi = mid;
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
    var lo = 1e-6, hi = 1.0;
    for (var i = 0; i < 200; i++) {
      var mid = (lo + hi) / 2;
      if (bondPrice(coupon, face, mid, periods) > price) lo = mid; else hi = mid;
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

  if (typeof module !== "undefined" && module.exports) {
    module.exports = Finance;       // Node (used by the parity test)
  } else {
    root.Finance = Finance;         // Browser
  }
})(typeof self !== "undefined" ? self : this);
