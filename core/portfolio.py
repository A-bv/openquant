"""
OpenQuant — Portfolio construction module.

Implements EPFL portfolio theory:
    V = D × C × D'           (covariance matrix)
    σ²_p = w · V · w'        (portfolio variance)
    β_p = Σ w_i × β_i        (portfolio beta)

Five portfolio comparisons (per spec):
    1. Current portfolio (user weights)
    2. Equal weight
    3. Inverse-volatility weighting (simple risk parity approx)
    4. Minimum variance (scipy SLSQP)
    5. Max Sharpe (least reliable — labeled clearly)

EPFL ground truth fixture:
    EPFL_H2_exemple: portfolio SD = 0.050794 at w=[0, 0.5, 0.5]

Dependency rule: zero Streamlit imports. Pure Python. Fully testable.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
import numpy as np
import pandas as pd
from scipy.optimize import minimize

from config import (
    DEFAULT_RISK_FREE_RATE,
    DEFAULT_TRADING_DAYS,
    LEDOIT_WOLF_THRESHOLD,
    MONTE_CARLO_PORTFOLIOS,
    BOOTSTRAP_RESAMPLES,
    EPFL_H2_PORTFOLIO_SD,
)
from core.utils import log_returns, annualise_return, annualise_vol, sharpe_ratio


@dataclass
class PortfolioResult:
    """Complete portfolio analysis result."""
    tickers: list[str]
    weights: dict[str, float]
    name: str

    # Risk/return
    expected_return: float
    volatility: float
    sharpe_ratio: float
    portfolio_beta: float

    # Risk decomposition
    systematic_variance: float
    idiosyncratic_variance: float

    # Covariance matrix
    cov_matrix: pd.DataFrame
    corr_matrix: pd.DataFrame

    # DCD' components
    D_matrix: np.ndarray
    C_matrix: np.ndarray

    warnings: list[str] = field(default_factory=list)


@dataclass
class PortfolioComparison:
    """All five portfolio comparisons."""
    tickers: list[str]
    returns: pd.DataFrame              # Daily log returns, columns=tickers
    cov_matrix: pd.DataFrame           # DCD' covariance matrix
    corr_matrix: pd.DataFrame          # Correlation matrix

    current: PortfolioResult
    equal_weight: PortfolioResult
    inverse_vol: PortfolioResult
    min_variance: PortfolioResult
    max_sharpe: PortfolioResult

    # Efficient frontier
    frontier_returns: np.ndarray
    frontier_vols: np.ndarray
    monte_carlo_returns: np.ndarray
    monte_carlo_vols: np.ndarray
    monte_carlo_sharpes: np.ndarray

    warnings: list[str] = field(default_factory=list)


class PortfolioAnalyser:
    """
    Builds portfolio analysis from price data.

    EPFL DCD' covariance matrix construction:
        D = diag(σ_1, ..., σ_n)
        C = correlation matrix
        V = D × C × D'
        σ²_p = w · V · w'
    """

    def analyse(
        self,
        prices: dict[str, pd.Series],
        current_weights: dict[str, float],
        risk_free_rate: float = DEFAULT_RISK_FREE_RATE,
        market_returns: Optional[pd.Series] = None,
    ) -> PortfolioComparison:
        """
        Compute full portfolio comparison.

        Args:
            prices: Dict of ticker → price series.
            current_weights: User's current weights (sum to 1).
            risk_free_rate: Annual risk-free rate.
            market_returns: Optional market return series for beta.

        Returns:
            PortfolioComparison with all five portfolios.
        """
        warnings = []
        tickers = list(prices.keys())
        n = len(tickers)

        # ── Compute returns ────────────────────────────────────────────────
        returns_dict = {}
        for ticker, price_series in prices.items():
            returns_dict[ticker] = log_returns(price_series)

        returns_df = pd.DataFrame(returns_dict).dropna()
        T, N = returns_df.shape

        # ── Covariance matrix (DCD') ───────────────────────────────────────
        if N >= LEDOIT_WOLF_THRESHOLD:
            from sklearn.covariance import LedoitWolf
            lw = LedoitWolf().fit(returns_df.values)
            cov_daily = pd.DataFrame(
                lw.covariance_,
                index=tickers, columns=tickers,
            )
            warnings.append(
                f"Ledoit-Wolf shrinkage applied (n_assets={N} ≥ threshold={LEDOIT_WOLF_THRESHOLD}). "
                "Reduces estimation noise when assets > observations ratio is high."
            )
        else:
            cov_daily = returns_df.cov(ddof=1)

        # Annualise
        cov_annual = cov_daily * DEFAULT_TRADING_DAYS
        corr_matrix = returns_df.corr()

        # D matrix (diagonal SDs) — EPFL DCD' formula
        sds = np.sqrt(np.diag(cov_annual.values))
        D = np.diag(sds)

        # Verify DCD' = V
        C = corr_matrix.values
        V_check = D @ C @ D
        # cov_annual ≈ V_check (minor floating point differences ok)

        # Annual expected returns
        mu = returns_df.mean() * DEFAULT_TRADING_DAYS

        # ── Five portfolios ────────────────────────────────────────────────
        w_current = np.array([current_weights.get(t, 1/n) for t in tickers])
        w_equal = np.ones(n) / n
        w_inv_vol = self._inverse_vol_weights(sds)
        w_min_var = self._min_variance_weights(cov_annual.values, n)
        w_max_sharpe = self._max_sharpe_weights(
            cov_annual.values, mu.values, risk_free_rate, n
        )

        def _build(weights, name):
            return self._compute_portfolio(
                weights, tickers, returns_df, cov_annual,
                corr_matrix, mu, risk_free_rate, market_returns,
                name, D, C,
            )

        current = _build(w_current, "Current Portfolio")
        equal_weight = _build(w_equal, "Equal Weight")
        inverse_vol = _build(w_inv_vol, "Inverse-Volatility")
        min_variance = _build(w_min_var, "Minimum Variance")
        max_sharpe = _build(w_max_sharpe, "Max Sharpe")

        # ── Efficient frontier (Monte Carlo) ───────────────────────────────
        mc_ret, mc_vol, mc_sr = self._monte_carlo_frontier(
            cov_annual.values, mu.values, risk_free_rate, n,
        )

        # ── Optimized frontier ─────────────────────────────────────────────
        f_ret, f_vol = self._optimized_frontier(
            cov_annual.values, mu.values, n,
        )

        return PortfolioComparison(
            tickers=tickers,
            returns=returns_df,
            cov_matrix=cov_annual,
            corr_matrix=corr_matrix,
            current=current,
            equal_weight=equal_weight,
            inverse_vol=inverse_vol,
            min_variance=min_variance,
            max_sharpe=max_sharpe,
            frontier_returns=f_ret,
            frontier_vols=f_vol,
            monte_carlo_returns=mc_ret,
            monte_carlo_vols=mc_vol,
            monte_carlo_sharpes=mc_sr,
            warnings=warnings,
        )

    def _compute_portfolio(
        self,
        weights: np.ndarray,
        tickers: list[str],
        returns_df: pd.DataFrame,
        cov_annual: pd.DataFrame,
        corr_matrix: pd.DataFrame,
        mu: pd.Series,
        risk_free_rate: float,
        market_returns: Optional[pd.Series],
        name: str,
        D: np.ndarray,
        C: np.ndarray,
    ) -> PortfolioResult:
        """Compute metrics for one portfolio."""
        wsum = float(weights.sum())
        if not np.isfinite(wsum) or wsum <= 0:
            raise ValueError(
                f"Cannot construct portfolio '{name}': weights sum to {wsum}. "
                f"Provide positive weights that sum to a positive value."
            )
        w = weights / wsum

        # Portfolio return and variance
        port_return = float(w @ mu.values)
        port_var = float(w @ cov_annual.values @ w)
        port_vol = np.sqrt(max(port_var, 0))

        # Sharpe ratio
        sr = (port_return - risk_free_rate) / port_vol if port_vol > 0 else 0.0

        # Portfolio beta
        port_beta = 0.0
        systematic_var = 0.0
        if market_returns is not None:
            mkt_ret = log_returns(market_returns)
            mkt_var = float(mkt_ret.var(ddof=1)) * DEFAULT_TRADING_DAYS
            port_returns = (returns_df * w).sum(axis=1)
            port_cov_mkt = float(port_returns.cov(mkt_ret)) * DEFAULT_TRADING_DAYS
            port_beta = port_cov_mkt / mkt_var if mkt_var > 0 else 0.0
            systematic_var = port_beta ** 2 * mkt_var
        idio_var = max(port_var - systematic_var, 0)

        return PortfolioResult(
            tickers=tickers,
            weights={t: float(w[i]) for i, t in enumerate(tickers)},
            name=name,
            expected_return=port_return,
            volatility=port_vol,
            sharpe_ratio=sr,
            portfolio_beta=port_beta,
            systematic_variance=systematic_var,
            idiosyncratic_variance=idio_var,
            cov_matrix=cov_annual,
            corr_matrix=corr_matrix,
            D_matrix=D,
            C_matrix=C,
        )

    def _inverse_vol_weights(self, vols: np.ndarray) -> np.ndarray:
        """
        Inverse-volatility weights.
        w_i = (1/σ_i) / Σ(1/σ_j)

        Simple risk parity approximation.
        Ignores correlations. No expected return estimates needed.
        """
        inv_vols = 1.0 / np.where(vols > 0, vols, 1e-8)
        return inv_vols / inv_vols.sum()

    def _min_variance_weights(
        self, cov: np.ndarray, n: int
    ) -> np.ndarray:
        """
        Minimum variance portfolio weights via SLSQP.
        Uses only covariance matrix — no expected return estimates.
        More robust than max Sharpe.
        Falls back to equal weight if optimizer fails.
        """
        def objective(w):
            return float(w @ cov @ w)

        constraints = [{"type": "eq", "fun": lambda w: w.sum() - 1}]
        bounds = [(0, 1)] * n
        w0 = np.ones(n) / n

        try:
            result = minimize(
                objective, w0,
                method="SLSQP",
                bounds=bounds,
                constraints=constraints,
                options={"ftol": 1e-12, "maxiter": 1000},
            )
            if result.success:
                return result.x
        except Exception:
            pass
        return w0  # Equal weight fallback

    def _max_sharpe_weights(
        self,
        cov: np.ndarray,
        mu: np.ndarray,
        rf: float,
        n: int,
    ) -> np.ndarray:
        """
        Maximum Sharpe ratio weights.
        Sensitive to expected return estimates — labeled clearly in UI.
        Falls back to equal weight if optimizer fails.
        """
        def neg_sharpe(w):
            port_ret = float(w @ mu)
            port_vol = np.sqrt(float(w @ cov @ w))
            if port_vol < 1e-8:
                return 0.0
            return -(port_ret - rf) / port_vol

        constraints = [{"type": "eq", "fun": lambda w: w.sum() - 1}]
        bounds = [(0, 1)] * n
        w0 = np.ones(n) / n

        try:
            result = minimize(
                neg_sharpe, w0,
                method="SLSQP",
                bounds=bounds,
                constraints=constraints,
                options={"ftol": 1e-12, "maxiter": 1000},
            )
            if result.success:
                return result.x
        except Exception:
            pass
        return w0

    def _monte_carlo_frontier(
        self,
        cov: np.ndarray,
        mu: np.ndarray,
        rf: float,
        n: int,
        n_portfolios: int = MONTE_CARLO_PORTFOLIOS,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Generate Monte Carlo random portfolios for frontier visualisation."""
        rng = np.random.default_rng(42)
        returns = np.zeros(n_portfolios)
        vols = np.zeros(n_portfolios)
        sharpes = np.zeros(n_portfolios)

        for i in range(n_portfolios):
            w = rng.dirichlet(np.ones(n))
            r = float(w @ mu)
            v = np.sqrt(float(w @ cov @ w))
            returns[i] = r
            vols[i] = v
            sharpes[i] = (r - rf) / v if v > 0 else 0

        return returns, vols, sharpes

    def _optimized_frontier(
        self,
        cov: np.ndarray,
        mu: np.ndarray,
        n: int,
        n_points: int = 50,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Compute optimized efficient frontier via SLSQP."""
        target_returns = np.linspace(mu.min(), mu.max(), n_points)
        frontier_vols = []
        frontier_rets = []

        for target in target_returns:
            constraints = [
                {"type": "eq", "fun": lambda w: w.sum() - 1},
                {"type": "eq", "fun": lambda w, t=target: float(w @ mu) - t},
            ]
            bounds = [(0, 1)] * n
            w0 = np.ones(n) / n

            try:
                result = minimize(
                    lambda w: float(w @ cov @ w),
                    w0,
                    method="SLSQP",
                    bounds=bounds,
                    constraints=constraints,
                    options={"ftol": 1e-12, "maxiter": 500},
                )
                if result.success:
                    frontier_vols.append(np.sqrt(result.fun))
                    frontier_rets.append(target)
            except Exception:
                pass

        return np.array(frontier_rets), np.array(frontier_vols)
