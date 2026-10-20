from __future__ import annotations

import math
from typing import Any

import pandas as pd


def summarize_history(history: pd.DataFrame) -> dict[str, Any]:
    """Calculate descriptive metrics from historical closing prices.

    Annualized volatility assumes observations represent daily trading sessions.
    These indicators describe history and are not investment recommendations.
    """
    if "Close" not in history.columns:
        raise ValueError("History must contain a Close column.")

    close = pd.to_numeric(history["Close"], errors="coerce").dropna()
    if len(close) < 2:
        raise ValueError("At least two valid closing prices are required.")

    returns = close.pct_change().dropna()
    latest = float(close.iloc[-1])
    previous = float(close.iloc[-2])
    first = float(close.iloc[0])
    peak = close.cummax()
    drawdown = close.div(peak).sub(1)

    daily_change_pct = ((latest / previous) - 1) * 100 if previous else None
    total_return_pct = ((latest / first) - 1) * 100 if first else None
    return_volatility = (
        float(returns.tail(252).std(ddof=1) * math.sqrt(252) * 100)
        if len(returns.tail(252)) >= 2
        else None
    )

    def rounded(value: float | None) -> float | None:
        return round(value, 4) if value is not None and math.isfinite(value) else None

    return {
        "observations": int(len(close)),
        "latest_close": rounded(latest),
        "previous_close": rounded(previous),
        "daily_change": rounded(latest - previous),
        "daily_change_pct": rounded(daily_change_pct),
        "period_return_pct": rounded(total_return_pct),
        "moving_average_20": rounded(float(close.tail(20).mean())),
        "annualized_volatility_pct": rounded(return_volatility),
        "max_drawdown_pct": rounded(float(drawdown.min() * 100)),
        "first_date": str(close.index[0].date()) if isinstance(close.index, pd.DatetimeIndex) else str(close.index[0]),
        "latest_date": str(close.index[-1].date()) if isinstance(close.index, pd.DatetimeIndex) else str(close.index[-1]),
    }


def history_records(history: pd.DataFrame, limit: int = 500) -> list[dict[str, object]]:
    """Serialize a bounded number of closing prices for API/UI charts."""
    if "Close" not in history.columns:
        raise ValueError("History must contain a Close column.")
    if limit < 1:
        raise ValueError("limit must be positive.")

    records: list[dict[str, object]] = []
    subset = history.tail(limit)
    for index, value in subset["Close"].items():
        number = pd.to_numeric(value, errors="coerce")
        if pd.isna(number):
            continue
        date_label = index.date().isoformat() if isinstance(index, pd.Timestamp) else str(index)
        records.append({"date": date_label, "close": round(float(number), 6)})
    return records
