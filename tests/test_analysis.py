import pandas as pd
import pytest

from finance_assistant.analysis import history_records, summarize_history
from finance_assistant.market_data import normalize_ticker, validate_period


def test_summary_returns_expected_descriptive_metrics():
    dates = pd.date_range("2025-01-01", periods=4, freq="D")
    history = pd.DataFrame({"Close": [100.0, 110.0, 105.0, 120.0]}, index=dates)

    result = summarize_history(history)

    assert result["observations"] == 4
    assert result["latest_close"] == 120.0
    assert result["previous_close"] == 105.0
    assert result["daily_change_pct"] == 14.2857
    assert result["period_return_pct"] == 20.0
    assert result["max_drawdown_pct"] == -4.5455


def test_summary_rejects_missing_or_insufficient_prices():
    with pytest.raises(ValueError, match="Close"):
        summarize_history(pd.DataFrame({"Open": [1.0, 2.0]}))
    with pytest.raises(ValueError, match="At least two"):
        summarize_history(pd.DataFrame({"Close": [None, 1.0]}))


def test_ticker_validation_normalizes_common_symbols():
    assert normalize_ticker(" aapl ") == "AAPL"
    assert normalize_ticker("btc-usd") == "BTC-USD"
    assert normalize_ticker("RELIANCE.NS") == "RELIANCE.NS"


@pytest.mark.parametrize("ticker", ["", "AAPL;DROP", "INVALID TICKER", "../AAPL"])
def test_ticker_validation_rejects_malformed_symbols(ticker):
    with pytest.raises(ValueError):
        normalize_ticker(ticker)


def test_period_validation_only_accepts_supported_windows():
    assert validate_period("1y") == "1y"
    with pytest.raises(ValueError, match="Unsupported period"):
        validate_period("10y")


def test_history_records_is_bounded_and_serializable():
    dates = pd.date_range("2025-01-01", periods=4, freq="D")
    history = pd.DataFrame({"Close": [10, 11, 12, 13]}, index=dates)

    result = history_records(history, limit=2)

    assert result == [
        {"date": "2025-01-03", "close": 12.0},
        {"date": "2025-01-04", "close": 13.0},
    ]
