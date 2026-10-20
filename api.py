from __future__ import annotations

import logging

from fastapi import FastAPI, HTTPException, Query

from finance_assistant import __version__
from finance_assistant.analysis import history_records, summarize_history
from finance_assistant.market_data import (
    SUPPORTED_PERIODS,
    MarketDataError,
    fetch_history,
    normalize_ticker,
    validate_period,
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Finance Assistant Market Analysis API",
    version=__version__,
    description=(
        "Historical market-data summaries and descriptive indicators. "
        "The API does not provide personalized investment advice or trading signals."
    ),
)


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok", "service": "finance-assistant", "version": __version__}


@app.get("/api/analysis/{ticker}", tags=["analysis"])
def analyze_ticker(
    ticker: str,
    period: str = Query(default="1y", description=f"Supported windows: {', '.join(sorted(SUPPORTED_PERIODS))}"),
) -> dict[str, object]:
    try:
        symbol = normalize_ticker(ticker)
        window = validate_period(period)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    try:
        history = fetch_history(symbol, window)
        return {
            "ticker": symbol,
            "period": window,
            "metrics": summarize_history(history),
            "history": history_records(history),
            "disclaimer": (
                "Historical descriptive analytics only. Not financial advice, a forecast, "
                "or a recommendation to buy or sell."
            ),
        }
    except MarketDataError as exc:
        logger.warning("Market data unavailable for %s (%s)", symbol, window)
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
