# Course extract — H2: Risk & Return

Source: EPFL `PF2handout.pdf` (Morellec, 44 slides) · Berk-DeMarzo Ch. 10-12.
Compact extraction so the material is actionable without re-opening the slides.

**Through-line of the whole handout:** `Rate of return = Riskless rate + Risk premium`.
You are only paid for the risk you *cannot* diversify away.

## Formulas (slide → formula)

| # | Concept | Formula | Slide |
|---|---|---|---|
| 1 | Realized return | `R = (Div + ΔP)/P = div yield + capital gain rate` | 2 |
| 2 | Expected / variance | `E[R]=Σ p·R` ; `Var=Σ p(R−E)²` or `1/(T−1)Σ(R_t−R̄)²` ; `SD=√Var` = volatility | 3-6 |
| 3 | Portfolio return | `R_p = Σ xᵢRᵢ` ; `E[R_p] = Σ xᵢE[Rᵢ]` | 7-9 |
| 4 | Portfolio variance | `Var(R_p) = Σᵢ Σⱼ xᵢxⱼ Cov(Rᵢ,Rⱼ) = wᵀΣw` | 13-14 |
| 5 | **Risk contribution** (Implication 1) | `SD(R_p) = Σᵢ xᵢ · SD(Rᵢ) · Corr(Rᵢ,R_p)` — each name contributes per its vol scaled by its correlation with the book | 13 |
| 6 | Large-portfolio limit (Impl. 2) | `Var(R_p) → average covariance` | 14 |
| 7 | Two-asset | `Var = x₁²σ₁² + x₂²σ₂² + 2x₁x₂·Corr·σ₁σ₂` ; corr=+1 → `σ=x₁σ₁+x₂σ₂` ; corr=−1 → `σ=|x₁σ₁−x₂σ₂|` | 14-16 |
| 8 | Risk-free + risky | `E=rf+x(E[Rp]−rf)` ; `SD=x·SD(Rp)` | 21-22 |
| 9 | **Sharpe / tangent** | `Sharpe = (E[Rp]−rf)/SD(Rp)` ; highest-Sharpe portfolio = tangent = efficient | 23-24 |
| 10 | **Beta** | `βᵢ = Cov(Rᵢ,R_mkt)/Var(R_mkt) = Corr(Rᵢ,R_mkt)·σᵢ/σ_mkt` | 29 |
| 11 | **CAPM** | `E[Rᵢ] = rf + βᵢ(E[R_mkt]−rf)` | 28-29 |
| 12 | Portfolio beta | `β_p = Σ xᵢβᵢ` (weighted average of betas) | 33 |
| 13 | **Alpha** | `α = E[R] − required return(SML)` ; Jensen's: `α = αᵢ − rf(1−βᵢ)` from regression `Rᵢ = αᵢ + βᵢR_mkt + ε` | 34-35, 40 |
| 14 | **Variance decomposition** | `σᵢ² = βᵢ²σ_mkt² + σε²` ; `R² = 1 − σε²/σᵢ²` = fraction of risk that is market (systematic) | 39 |
| 15 | CAPM inputs | risk-free rate (gov bond), market risk premium (historical), beta (2-5yr regression) | 36-38 |

CML (total-vol view) vs SML (beta view). Appendix = APT / Fama-French 3-factor — **out of scope** for now.

## Relatable examples the course uses (Tier-2 deliverable seeds)

- **Sally Ferson**: 100% Coca-Cola → move 40% into Intel ⇒ *same* vol (25%) but expected return 6%→14%. "Same risk, more return."
- **Brother-in-law**: 100% McDonald's → mix market+risk-free ⇒ lower vol for same return, OR higher return for same vol (CML dominance).
- **Margin**: $10k + borrow $10k ⇒ doubles *both* return and risk (55%/−25% vs 30%/−10%).
- **Disney**: β=1.25 ⇒ `E[R]=3.6%+1.25·6%=11.1%` — "managers must earn ≥11.1% to break even for equity investors."

## What this unlocks for OpenQuant (Tier 2 deliverables)

| Deliverable (Layer-1 result) | Formula | Status in `core/` |
|---|---|---|
| "6 holdings = 1.8 independent bets" + risk driver | #4,#5 | ✅ `portfolio.py` (BUILT) |
| "65/35 minimises vol at 11%" | min-variance | ✅ `portfolio.py` |
| "Your Sharpe 0.4 < 0.6 for 60/40 → dominated" | #9 | ✅ `utils.sharpe_from_stats` |
| "For beta 1.4, require 11%/yr before buying" | #11 | ✅ `wacc.capm_cost_of_equity` |
| "Beta 1.8 → market −10% means expect −18%" | #10 | ✅ `wacc.beta_from_correlation` |
| "70% of this stock's risk is firm-specific, 30% market" | #14 (R²) | ◑ `wacc.idiosyncratic_variance` exists; needs market-relative wiring to live returns |
| "You earned +12% but beta justified +13% → negative alpha" | #13 | ✗ **add Jensen's alpha** |
| "This basket's beta is 0.9" | #12 | ✗ **add portfolio beta** |
| "Same risk, +8% more return" (Sally move) | efficient frontier / CML | ✗ relatable, worth building |

## Verification — our engine matches the course exactly

| Course (H2 slide) | Our implementation |
|---|---|
| `Var(R_p)=wᵀΣw` (13-14) | `portfolio.portfolio_variance` |
| `SD = Σ xᵢ SD(Rᵢ) Corr(Rᵢ,R_p)` (13) | `portfolio.risk_contributions` (Euler) |
| corr=−1 → `|x₁σ₁−x₂σ₂|` (16) | `tests/test_portfolio.py::TestExam2P4_ReducesToTwoAsset` |
| `β = Cov/Var = Corr·σᵢ/σ_M` (29) | `wacc.beta_from_correlation` |
| `CAPM = rf + β·MRP` (28-29) | `wacc.capm_cost_of_equity` |
| `σᵢ² = β²σ_M² + σε²` (39) | `wacc.idiosyncratic_variance` |
| `Sharpe = (E−rf)/SD` (23) | `utils.sharpe_from_stats` |

→ The risk/portfolio engine is **faithful to the course**. The three gaps to finish Tier 2 are: **portfolio beta** (#12), **Jensen's alpha** (#13), and wiring the **systematic/idiosyncratic split** (#14, R²) to live returns.
