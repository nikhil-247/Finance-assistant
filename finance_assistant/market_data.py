from __future__ import annotations

import re

import pandas as pd
import yfinance as yf

SUPPORTED_PERIODS = frozenset({"1mo", "3mo", "6mo", "1y", "2y", "5y", "max"})
TICKER_PATTERN = re.compile(r"[A-Z0-9^][A-Z0-9.^=-]{0,19}")


class MarketDataError(RuntimeError):
    """Raised when a supported symbol cannot be analyzed with available data."""


def normalize_ticker(value: str) -> str:
    """Normalize a ticker symbol and reject malformed input before provider use."""
    if not isinstance(value, str):
        raise ValueError("Ticker must be a string.")

    ticker = value.strip().upper()
    if not ticker or not TICKER_PATTERN.fullmatch(ticker):
        raise ValueError(
            "Enter a valid ticker using letters, numbers, dots, hyphens, equals, or ^."
        )
    return ticker


def validate_period(period: str) -> str:
    """Accept only supported Yahoo Finance history windows."""
    if period not in SUPPORTED_PERIODS:
        allowed = ", ".join(sorted(SUPPORTED_PERIODS))
        raise ValueError(f"Unsupported period. Choose one of: {allowed}.")
    return period


def fetch_history(ticker: str, period: str = "1y") -> pd.DataFrame:
    """Fetch historical prices. Raises a safe domain error on provider failures."""
    symbol = normalize_ticker(ticker)
    window = validate_period(period)

    try:
        history = yf.Ticker(symbol).history(period=window, auto_adjust=True)
    except Exception as exc:
        raise MarketDataError("Unable to fetch market data. Try again later.") from exc

    if not isinstance(history, pd.DataFrame) or history.empty:
        raise MarketDataError(
            f"No historical price data was returned for {symbol}. Check the ticker or try another period."
        )
    if "Close" not in history.columns:
        raise MarketDataError("The data provider returned no closing-price column.")

    cleaned = history.copy()
    cleaned["Close"] = pd.to_numeric(cleaned["Close"], errors="coerce")
    cleaned = cleaned.loc[cleaned["Close"].notna()].sort_index()
    if len(cleaned) < 2:
        raise MarketDataError("At least two valid closing prices are required for analysis.")

    return cleaned
