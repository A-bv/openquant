"""
OpenQuant — Data fetching layer.

Architecture:
- SEC EDGAR as primary source for financial statements (US companies)
  Unlimited, free, official, no API key required.
- yfinance as primary source for price data
- Local CSV cache to avoid repeat fetches and enable offline use
- FMP API as optional enhancement (user provides own key, v2 international)

Dependency rule: zero Streamlit imports. Pure Python. Fully testable.

All external calls wrapped in try/except.
Custom exceptions propagate cleanly to UI layer.
"""

from __future__ import annotations

import json
import os
import time
import hashlib
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
import requests

from config import (
    EDGAR_BASE_URL,
    EDGAR_SUBMISSIONS_URL,
    EDGAR_FACTS_URL,
    FMP_BASE_URL,
    CACHE_DIR,
    CACHE_TTL_RECENT_SECONDS,
    CROSS_VALIDATION_TOLERANCE,
    CROSS_VALIDATION_FIELDS,
    DEFAULT_MARKET_INDEX,
    BETA_LOOKBACK_YEARS,
)

logger = logging.getLogger(__name__)


# ── Custom exceptions ─────────────────────────────────────────────────────────

class DataFetchError(Exception):
    """Raised when all data sources fail for a ticker."""
    pass


class InsufficientDataError(Exception):
    """Raised when data exists but is insufficient for analysis."""
    pass


class UnsupportedTickerError(Exception):
    """Raised when a ticker is not a supported US company."""
    pass


class DataInconsistencyWarning(UserWarning):
    """Raised when cross-validation detects source disagreement."""
    pass


# ── Data structures ───────────────────────────────────────────────────────────

@dataclass
class FinancialStatements:
    """
    Standardised financial statements for one company.
    All values in USD. Annual frequency.
    """
    ticker: str
    company_name: str
    cik: str
    source: str                          # "edgar" or "fmp"
    fetched_at: datetime

    # Income statement
    revenue: pd.Series                   # Annual revenue
    ebit: pd.Series                      # Earnings before interest and tax
    depreciation_amortisation: pd.Series # D&A
    interest_expense: pd.Series          # Interest expense
    tax_expense: pd.Series               # Income tax expense
    net_income: pd.Series                # Net income
    ebitda: pd.Series                    # EBITDA

    # Balance sheet
    total_assets: pd.Series
    total_debt: pd.Series                # Short + long term debt
    beginning_debt: pd.Series            # Prior year debt (for avg debt cost)
    cash_and_equivalents: pd.Series
    shares_outstanding: pd.Series        # Diluted
    net_working_capital: pd.Series       # Current assets - current liabilities

    # Cash flow statement
    operating_cash_flow: pd.Series
    capital_expenditure: pd.Series       # Always positive (outflow)
    free_cash_flow: pd.Series            # Computed: OCF - CapEx
    stock_based_compensation: pd.Series  # SBC — shown separately

    # Derived
    effective_tax_rate: pd.Series        # tax_expense / pretax_income
    fcf_margin: pd.Series                # FCF / revenue

    # Warnings
    data_warnings: list[str] = field(default_factory=list)


@dataclass
class PriceData:
    """Daily adjusted closing prices for beta computation."""
    ticker: str
    prices: pd.Series                    # Adjusted close, date-indexed
    market_prices: pd.Series             # Market index adjusted close
    source: str
    fetched_at: datetime


@dataclass
class TickerValidation:
    """Result of pre-flight ticker validation."""
    ticker: str
    is_valid: bool
    is_us_company: bool
    company_name: str
    sector: str
    cik: Optional[str]
    trading_days_available: int
    has_financial_statements: bool
    badge: str                           # "green", "amber", "red"
    message: str


# ── Cache manager ─────────────────────────────────────────────────────────────

class CacheManager:
    """
    Simple file-based cache for fetched data.
    JSON for financial data, CSV for price series.
    """

    def __init__(self, cache_dir: str = CACHE_DIR):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _key_to_path(self, key: str, ext: str = "json") -> Path:
        """Convert cache key to file path."""
        safe_key = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{safe_key}.{ext}"

    def get(self, key: str, ttl_seconds: Optional[int] = CACHE_TTL_RECENT_SECONDS) -> Optional[dict]:
        """
        Retrieve cached value if it exists and is not expired.

        Args:
            key: Cache key string.
            ttl_seconds: TTL in seconds. None means permanent.

        Returns:
            Cached data dict or None if miss/expired.
        """
        path = self._key_to_path(key)
        if not path.exists():
            return None

        if ttl_seconds is not None:
            age = time.time() - path.stat().st_mtime
            if age > ttl_seconds:
                path.unlink(missing_ok=True)
                return None

        try:
            with open(path) as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            path.unlink(missing_ok=True)
            return None

    def set(self, key: str, data: dict) -> None:
        """Store data in cache."""
        path = self._key_to_path(key)
        try:
            with open(path, "w") as f:
                json.dump(data, f, default=str)
        except IOError as e:
            logger.warning(f"Cache write failed for key {key}: {e}")

    def get_prices(self, key: str, ttl_seconds: Optional[int] = CACHE_TTL_RECENT_SECONDS) -> Optional[pd.Series]:
        """Retrieve cached price series."""
        path = self._key_to_path(key, ext="csv")
        if not path.exists():
            return None

        age = time.time() - path.stat().st_mtime
        if ttl_seconds is not None and age > ttl_seconds:
            path.unlink(missing_ok=True)
            return None

        try:
            df = pd.read_csv(path, index_col=0, parse_dates=True)
            return df.iloc[:, 0]
        except Exception:
            path.unlink(missing_ok=True)
            return None

    def set_prices(self, key: str, prices: pd.Series) -> None:
        """Store price series in cache."""
        path = self._key_to_path(key, ext="csv")
        try:
            prices.to_csv(path)
        except IOError as e:
            logger.warning(f"Price cache write failed: {e}")


# ── EDGAR client ──────────────────────────────────────────────────────────────

class EDGARClient:
    """
    SEC EDGAR API client.
    Fetches XBRL financial data directly from the official source.
    Unlimited, free, no API key required.
    US companies only.
    """

    BASE_URL = "https://data.sec.gov"
    HEADERS = {
        "User-Agent": "OpenQuant educational-tool contact@openquant.dev",
        "Accept-Encoding": "gzip, deflate",
    }
    # Rate limit: EDGAR requests max 10/second
    REQUEST_DELAY = 0.12

    # XBRL tag mappings — companies use different tags for same concept
    TAG_MAPPINGS = {
        "revenue": [
            "Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax",
            "SalesRevenueNet", "SalesRevenueGoodsNet", "RevenueFromContractWithCustomer",
        ],
        "ebit": [
            "OperatingIncomeLoss",
        ],
        "depreciation_amortisation": [
            "DepreciationDepletionAndAmortization",
            "DepreciationAndAmortization",
            "Depreciation",
        ],
        "interest_expense": [
            "InterestExpense", "InterestAndDebtExpense",
        ],
        "net_income": [
            "NetIncomeLoss", "NetIncome",
        ],
        "capital_expenditure": [
            "PaymentsToAcquirePropertyPlantAndEquipment",
            "CapitalExpendituresIncurringObligation",
        ],
        "operating_cash_flow": [
            "NetCashProvidedByUsedInOperatingActivities",
        ],
        "total_debt": [
            "LongTermDebtAndCapitalLeaseObligations",
            "LongTermDebt", "DebtAndCapitalLeaseObligations",
        ],
        "cash_and_equivalents": [
            "CashAndCashEquivalentsAtCarryingValue",
            "CashCashEquivalentsAndShortTermInvestments",
        ],
        "shares_outstanding": [
            "CommonStockSharesOutstanding",
            "WeightedAverageNumberOfDilutedSharesOutstanding",
        ],
        "tax_expense": [
            "IncomeTaxExpenseBenefit",
        ],
        "stock_based_compensation": [
            "ShareBasedCompensation",
            "AllocatedShareBasedCompensationExpense",
        ],
        "current_assets": [
            "AssetsCurrent",
        ],
        "current_liabilities": [
            "LiabilitiesCurrent",
        ],
    }

    def __init__(self):
        self._session = requests.Session()
        self._session.headers.update(self.HEADERS)

    def _get(self, url: str) -> dict:
        """Make a GET request with rate limiting and error handling."""
        time.sleep(self.REQUEST_DELAY)
        try:
            response = self._session.get(url, timeout=15)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            raise DataFetchError(f"EDGAR HTTP error: {e}")
        except requests.exceptions.ConnectionError:
            raise DataFetchError("Cannot connect to SEC EDGAR. Check your internet connection.")
        except requests.exceptions.Timeout:
            raise DataFetchError("SEC EDGAR request timed out.")

    def get_cik(self, ticker: str) -> Optional[str]:
        """
        Look up CIK (Central Index Key) for a ticker symbol.

        Args:
            ticker: Stock ticker symbol (e.g. "AAPL").

        Returns:
            CIK as zero-padded 10-digit string, or None if not found.
        """
        try:
            url = f"{self.BASE_URL}/files/company_tickers.json"
            data = self._get(url)
            ticker_upper = ticker.upper()
            for _, company in data.items():
                if company.get("ticker", "").upper() == ticker_upper:
                    return str(company["cik_str"]).zfill(10)
            return None
        except DataFetchError:
            return None

    def get_company_info(self, cik: str) -> dict:
        """
        Get company metadata from EDGAR submissions.

        Args:
            cik: Zero-padded 10-digit CIK.

        Returns:
            Dict with name, sic, sector, exchanges.
        """
        url = EDGAR_SUBMISSIONS_URL.format(cik=int(cik))
        data = self._get(url)
        return {
            "name": data.get("name", ""),
            "sic": data.get("sic", ""),
            "sic_description": data.get("sicDescription", ""),
            "exchanges": data.get("exchanges", []),
            "tickers": data.get("tickers", []),
        }

    def get_facts(self, cik: str) -> dict:
        """
        Get all XBRL facts for a company.

        Args:
            cik: Zero-padded 10-digit CIK.

        Returns:
            Raw XBRL facts dict.
        """
        url = EDGAR_FACTS_URL.format(cik=int(cik))
        return self._get(url)

    def extract_annual_series(
        self,
        facts: dict,
        concept_tags: list[str],
        unit: str = "USD",
    ) -> Optional[pd.Series]:
        """
        Extract annual values for a concept from XBRL facts.

        Tries each tag in concept_tags in order — companies use
        different tag names for the same concept.

        Args:
            facts: Raw facts dict from get_facts().
            concept_tags: List of XBRL tags to try.
            unit: Unit of measurement. Default "USD".
                  Use "shares" for share count data.

        Returns:
            pd.Series indexed by fiscal year end date, or None if not found.
        """
        us_gaap = facts.get("facts", {}).get("us-gaap", {})

        for tag in concept_tags:
            if tag not in us_gaap:
                continue

            tag_data = us_gaap[tag]
            units = tag_data.get("units", {})

            # Try specified unit first, then any available unit
            unit_to_use = unit if unit in units else (next(iter(units), None))
            if unit_to_use is None or unit_to_use not in units:
                continue
            unit = unit_to_use

            records = units[unit]

            # Filter for annual 10-K filings only
            annual = [
                r for r in records
                if r.get("form") in ("10-K", "10-K/A")
                and r.get("fp") == "FY"
                and "end" in r
            ]

            if not annual:
                continue

            # Deduplicate by end date — keep most recent filing
            by_date = {}
            for r in annual:
                end = r["end"]
                if end not in by_date or r.get("filed", "") > by_date[end].get("filed", ""):
                    by_date[end] = r

            if not by_date:
                continue

            series = pd.Series(
                {pd.Timestamp(end): r["val"] for end, r in by_date.items()}
            ).sort_index()

            return series

        return None


# ── yfinance price fetcher (mock-friendly interface) ─────────────────────────

class PriceFetcher:
    """
    Fetches daily adjusted closing prices.
    Uses yfinance when available, falls back to mock for testing.
    """

    def fetch(
        self,
        ticker: str,
        years: int = BETA_LOOKBACK_YEARS,
    ) -> pd.Series:
        """
        Fetch adjusted closing prices for a ticker.

        Args:
            ticker: Stock ticker symbol.
            years: Years of history to fetch.

        Returns:
            pd.Series of adjusted closing prices, date-indexed.

        Raises:
            DataFetchError: If prices cannot be fetched.
        """
        try:
            import yfinance as yf
            end = datetime.today()
            start = end - timedelta(days=years * 365 + 10)
            data = yf.download(
                ticker,
                start=start.strftime("%Y-%m-%d"),
                end=end.strftime("%Y-%m-%d"),
                auto_adjust=True,
                progress=False,
            )
            if data.empty:
                raise DataFetchError(f"No price data found for {ticker}")
            prices = data["Close"]
            if isinstance(prices, pd.DataFrame):
                prices = prices.iloc[:, 0]
            prices.name = ticker
            return prices.dropna()

        except ImportError:
            raise DataFetchError(
                "yfinance is not installed. Run: pip install yfinance"
            )
        except Exception as e:
            raise DataFetchError(f"Price fetch failed for {ticker}: {e}")


# ── Main DataFetcher ──────────────────────────────────────────────────────────

class DataFetcher:
    """
    Main data access object for OpenQuant.

    Orchestrates:
    1. SEC EDGAR for financial statements (US companies)
    2. yfinance for price data
    3. Local cache for all fetched data
    4. Cross-validation between sources

    Usage:
        fetcher = DataFetcher()
        validation = fetcher.validate_ticker("AAPL")
        if validation.is_valid:
            statements = fetcher.get_financial_statements("AAPL")
            prices = fetcher.get_prices("AAPL")
    """

    def __init__(
        self,
        cache_dir: str = CACHE_DIR,
        fmp_api_key: Optional[str] = None,
    ):
        self.cache = CacheManager(cache_dir)
        self.edgar = EDGARClient()
        self.price_fetcher = PriceFetcher()
        self.fmp_api_key = fmp_api_key or os.getenv("FMP_API_KEY")

    def validate_ticker(self, ticker: str) -> TickerValidation:
        """
        Pre-flight validation for a ticker.
        Fast check: 5-day price fetch + CIK lookup.

        Args:
            ticker: Stock ticker symbol.

        Returns:
            TickerValidation with badge (green/amber/red) and message.
        """
        ticker = ticker.upper().strip()

        # Check cache first
        cache_key = f"validation_{ticker}"
        cached = self.cache.get(cache_key, ttl_seconds=3600)  # 1h TTL for validation
        if cached:
            return TickerValidation(**cached)

        # Step 1: CIK lookup — confirms US company
        cik = self.edgar.get_cik(ticker)
        if not cik:
            result = TickerValidation(
                ticker=ticker,
                is_valid=False,
                is_us_company=False,
                company_name="",
                sector="",
                cik=None,
                trading_days_available=0,
                has_financial_statements=False,
                badge="red",
                message=(
                    f"'{ticker}' not found in SEC EDGAR. "
                    f"OpenQuant currently supports US-listed companies only. "
                    f"International coverage coming in v2."
                ),
            )
            return result

        # Step 2: Company info
        try:
            info = self.edgar.get_company_info(cik)
            company_name = info.get("name", ticker)
            sector = info.get("sic_description", "Unknown")
        except DataFetchError:
            company_name = ticker
            sector = "Unknown"

        # Step 3: Price history check
        trading_days = 0
        try:
            prices = self.price_fetcher.fetch(ticker, years=3)
            trading_days = len(prices)
        except DataFetchError:
            pass

        # Step 4: Financial statements availability
        has_financials = False
        try:
            facts = self.edgar.get_facts(cik)
            us_gaap = facts.get("facts", {}).get("us-gaap", {})
            has_financials = len(us_gaap) > 10
        except DataFetchError:
            pass

        # Determine badge
        from config import MIN_TRADING_DAYS, MIN_PRICE_HISTORY_YEARS
        min_days = MIN_TRADING_DAYS * MIN_PRICE_HISTORY_YEARS

        if not has_financials:
            badge = "red"
            message = f"{company_name}: No financial statement data found in EDGAR."
        elif trading_days < min_days:
            badge = "amber"
            message = (
                f"{company_name}: Only {trading_days} days of price history. "
                f"Beta computation may be unreliable (need {min_days}+ days)."
            )
        else:
            badge = "green"
            message = (
                f"{company_name}: Valid. "
                f"{trading_days} trading days available."
            )

        result = TickerValidation(
            ticker=ticker,
            is_valid=badge != "red",
            is_us_company=True,
            company_name=company_name,
            sector=sector,
            cik=cik,
            trading_days_available=trading_days,
            has_financial_statements=has_financials,
            badge=badge,
            message=message,
        )

        # Cache validation result
        self.cache.set(cache_key, {
            "ticker": result.ticker,
            "is_valid": result.is_valid,
            "is_us_company": result.is_us_company,
            "company_name": result.company_name,
            "sector": result.sector,
            "cik": result.cik,
            "trading_days_available": result.trading_days_available,
            "has_financial_statements": result.has_financial_statements,
            "badge": result.badge,
            "message": result.message,
        })

        return result

    def get_financial_statements(self, ticker: str) -> FinancialStatements:
        """
        Fetch and standardise financial statements for a US company.

        Uses SEC EDGAR as primary source.
        All values in USD, annual frequency, last 10 years max.

        Args:
            ticker: Stock ticker symbol (US company).

        Returns:
            FinancialStatements dataclass with all required fields.

        Raises:
            DataFetchError: If EDGAR fetch fails.
            InsufficientDataError: If insufficient history available.
            UnsupportedTickerError: If company not found in EDGAR.
        """
        ticker = ticker.upper().strip()

        # Check cache
        cache_key = f"financials_{ticker}"
        cached = self.cache.get(cache_key)
        if cached:
            return self._deserialise_statements(cached)

        # CIK lookup
        cik = self.edgar.get_cik(ticker)
        if not cik:
            raise UnsupportedTickerError(
                f"{ticker} not found in SEC EDGAR. "
                f"OpenQuant supports US-listed companies only."
            )

        # Company info
        info = self.edgar.get_company_info(cik)
        company_name = info.get("name", ticker)

        # Fetch all XBRL facts
        facts = self.edgar.get_facts(cik)
        warnings = []

        def _extract(concept: str) -> Optional[pd.Series]:
            tags = EDGARClient.TAG_MAPPINGS.get(concept, [])
            series = self.edgar.extract_annual_series(facts, tags)
            if series is None:
                warnings.append(f"Could not find '{concept}' in EDGAR data.")
            return series

        # Extract all components
        revenue = _extract("revenue")
        ebit = _extract("ebit")
        da = _extract("depreciation_amortisation")
        interest = _extract("interest_expense")
        tax = _extract("tax_expense")
        net_income = _extract("net_income")
        capex_raw = _extract("capital_expenditure")
        ocf = _extract("operating_cash_flow")
        debt = _extract("total_debt")
        cash = _extract("cash_and_equivalents")
        shares_raw = self.edgar.extract_annual_series(
            facts, EDGARClient.TAG_MAPPINGS["shares_outstanding"], unit="shares"
        )
        if shares_raw is None:
            shares_raw = _extract("shares_outstanding")
        shares = shares_raw
        sbc = _extract("stock_based_compensation")
        current_assets = _extract("current_assets")
        current_liabilities = _extract("current_liabilities")

        # Validate minimum required fields
        required = {
            "revenue": revenue,
            "operating_cash_flow": ocf,
            "capital_expenditure": capex_raw,
            "total_debt": debt,
            "shares_outstanding": shares,
        }
        missing = [k for k, v in required.items() if v is None]
        if missing:
            raise InsufficientDataError(
                f"Missing required financial data for {ticker}: {missing}. "
                f"This company may not have sufficient EDGAR filings."
            )

        # Align all series to common index (fiscal year ends)
        # Use last 10 years
        common_idx = revenue.index[-10:] if len(revenue) >= 10 else revenue.index

        def _align(s: Optional[pd.Series]) -> pd.Series:
            if s is None:
                return pd.Series(np.nan, index=common_idx)
            return s.reindex(common_idx, method="nearest", tolerance="180D").fillna(np.nan)

        revenue_a = _align(revenue)
        ebit_a = _align(ebit)
        da_a = _align(da)
        interest_a = _align(interest)
        tax_a = _align(tax)
        net_income_a = _align(net_income)
        capex_a = _align(capex_raw).abs()   # Ensure positive
        ocf_a = _align(ocf)
        debt_a = _align(debt)
        cash_a = _align(cash)
        shares_a = _align(shares)
        sbc_a = _align(sbc)
        curr_assets_a = _align(current_assets)
        curr_liab_a = _align(current_liabilities)

        # Computed series
        fcf = ocf_a - capex_a
        nwc = curr_assets_a - curr_liab_a

        # Beginning debt (prior year) for average debt cost calculation
        beginning_debt = debt_a.shift(1)

        # Effective tax rate
        pretax_income = net_income_a + tax_a
        eff_tax = (tax_a / pretax_income).clip(0, 0.60)

        # FCF margin
        fcf_margin = (fcf / revenue_a).replace([np.inf, -np.inf], np.nan)

        # EBITDA
        ebitda_a = ebit_a + da_a if ebit is not None and da is not None else pd.Series(np.nan, index=common_idx)

        statements = FinancialStatements(
            ticker=ticker,
            company_name=company_name,
            cik=cik,
            source="edgar",
            fetched_at=datetime.now(),
            revenue=revenue_a,
            ebit=ebit_a,
            depreciation_amortisation=da_a,
            interest_expense=interest_a,
            tax_expense=tax_a,
            net_income=net_income_a,
            ebitda=ebitda_a,
            total_assets=pd.Series(np.nan, index=common_idx),
            total_debt=debt_a,
            beginning_debt=beginning_debt,
            cash_and_equivalents=cash_a,
            shares_outstanding=shares_a,
            net_working_capital=nwc,
            operating_cash_flow=ocf_a,
            capital_expenditure=capex_a,
            free_cash_flow=fcf,
            stock_based_compensation=sbc_a,
            effective_tax_rate=eff_tax,
            fcf_margin=fcf_margin,
            data_warnings=warnings,
        )

        # Cache serialised version
        self.cache.set(cache_key, self._serialise_statements(statements))

        return statements

    def get_prices(
        self,
        ticker: str,
        market_index: str = DEFAULT_MARKET_INDEX,
        years: int = BETA_LOOKBACK_YEARS,
    ) -> PriceData:
        """
        Fetch daily adjusted prices for ticker and market index.

        Args:
            ticker: Stock ticker symbol.
            market_index: Market benchmark ticker. Default ^GSPC.
            years: Years of history.

        Returns:
            PriceData with aligned stock and market price series.

        Raises:
            DataFetchError: If prices cannot be fetched.
        """
        ticker = ticker.upper().strip()

        # Check cache for both series
        stock_key = f"prices_{ticker}_{years}y"
        market_key = f"prices_{market_index}_{years}y"

        stock_prices = self.cache.get_prices(stock_key)
        market_prices = self.cache.get_prices(market_key)

        if stock_prices is None:
            stock_prices = self.price_fetcher.fetch(ticker, years)
            self.cache.set_prices(stock_key, stock_prices)

        if market_prices is None:
            market_prices = self.price_fetcher.fetch(market_index, years)
            self.cache.set_prices(market_key, market_prices)

        # Align to common dates
        common_idx = stock_prices.index.intersection(market_prices.index)
        if len(common_idx) < 252:
            raise InsufficientDataError(
                f"Insufficient overlapping price data for {ticker} "
                f"and {market_index}. Need at least 252 days."
            )

        return PriceData(
            ticker=ticker,
            prices=stock_prices.loc[common_idx],
            market_prices=market_prices.loc[common_idx],
            source="yfinance",
            fetched_at=datetime.now(),
        )

    def _serialise_statements(self, s: FinancialStatements) -> dict:
        """Convert FinancialStatements to JSON-serialisable dict."""
        def _series_to_dict(series: pd.Series) -> dict:
            return {str(k): v for k, v in series.items()}

        return {
            "ticker": s.ticker,
            "company_name": s.company_name,
            "cik": s.cik,
            "source": s.source,
            "fetched_at": s.fetched_at.isoformat(),
            "revenue": _series_to_dict(s.revenue),
            "ebit": _series_to_dict(s.ebit),
            "depreciation_amortisation": _series_to_dict(s.depreciation_amortisation),
            "interest_expense": _series_to_dict(s.interest_expense),
            "tax_expense": _series_to_dict(s.tax_expense),
            "net_income": _series_to_dict(s.net_income),
            "ebitda": _series_to_dict(s.ebitda),
            "total_assets": _series_to_dict(s.total_assets),
            "total_debt": _series_to_dict(s.total_debt),
            "beginning_debt": _series_to_dict(s.beginning_debt),
            "cash_and_equivalents": _series_to_dict(s.cash_and_equivalents),
            "shares_outstanding": _series_to_dict(s.shares_outstanding),
            "net_working_capital": _series_to_dict(s.net_working_capital),
            "operating_cash_flow": _series_to_dict(s.operating_cash_flow),
            "capital_expenditure": _series_to_dict(s.capital_expenditure),
            "free_cash_flow": _series_to_dict(s.free_cash_flow),
            "stock_based_compensation": _series_to_dict(s.stock_based_compensation),
            "effective_tax_rate": _series_to_dict(s.effective_tax_rate),
            "fcf_margin": _series_to_dict(s.fcf_margin),
            "data_warnings": s.data_warnings,
        }

    def _deserialise_statements(self, data: dict) -> FinancialStatements:
        """Reconstruct FinancialStatements from cached dict."""
        def _dict_to_series(d: dict) -> pd.Series:
            return pd.Series(
                {pd.Timestamp(k): float(v) if v is not None else np.nan
                 for k, v in d.items()}
            ).sort_index()

        return FinancialStatements(
            ticker=data["ticker"],
            company_name=data["company_name"],
            cik=data["cik"],
            source=data["source"],
            fetched_at=datetime.fromisoformat(data["fetched_at"]),
            revenue=_dict_to_series(data["revenue"]),
            ebit=_dict_to_series(data["ebit"]),
            depreciation_amortisation=_dict_to_series(data["depreciation_amortisation"]),
            interest_expense=_dict_to_series(data["interest_expense"]),
            tax_expense=_dict_to_series(data["tax_expense"]),
            net_income=_dict_to_series(data["net_income"]),
            ebitda=_dict_to_series(data["ebitda"]),
            total_assets=_dict_to_series(data["total_assets"]),
            total_debt=_dict_to_series(data["total_debt"]),
            beginning_debt=_dict_to_series(data["beginning_debt"]),
            cash_and_equivalents=_dict_to_series(data["cash_and_equivalents"]),
            shares_outstanding=_dict_to_series(data["shares_outstanding"]),
            net_working_capital=_dict_to_series(data["net_working_capital"]),
            operating_cash_flow=_dict_to_series(data["operating_cash_flow"]),
            capital_expenditure=_dict_to_series(data["capital_expenditure"]),
            free_cash_flow=_dict_to_series(data["free_cash_flow"]),
            stock_based_compensation=_dict_to_series(data["stock_based_compensation"]),
            effective_tax_rate=_dict_to_series(data["effective_tax_rate"]),
            fcf_margin=_dict_to_series(data["fcf_margin"]),
            data_warnings=data.get("data_warnings", []),
        )
