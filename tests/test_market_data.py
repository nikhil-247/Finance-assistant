import pandas as pd
import pytest

from finance_assistant import market_data


def test_fetch_history_wraps_provider_exception(monkeypatch):
    class BrokenTicker:
        def __init__(self, symbol):
            assert symbol == "AAPL"

        def history(self, *, period, auto_adjust):
            assert period == "1y"
            assert auto_adjust is True
            raise RuntimeError("upstream provider details should not leak")

    monkeypatch.setattr(market_data.yf, "Ticker", BrokenTicker)

    with pytest.raises(
        market_data.MarketDataError,
        match="Unable to fetch market data",
    ) as exc_info:
        market_data.fetch_history("aapl", "1y")

    assert "upstream provider details" not in str(exc_info.value)


def test_fetch_history_rejects_empty_provider_response(monkeypatch):
    class EmptyTicker:
        def __init__(self, _symbol):
            pass

        def history(self, *, period, auto_adjust):
            return pd.DataFrame()

    monkeypatch.setattr(market_data.yf, "Ticker", EmptyTicker)

    with pytest.raises(market_data.MarketDataError, match="No historical price data"):
        market_data.fetch_history("AAPL", "1y")


def test_fetch_history_rejects_response_without_close_column(monkeypatch):
    class MissingCloseTicker:
        def __init__(self, _symbol):
            pass

        def history(self, *, period, auto_adjust):
            return pd.DataFrame({"Open": [100.0, 101.0]})

    monkeypatch.setattr(market_data.yf, "Ticker", MissingCloseTicker)

    with pytest.raises(market_data.MarketDataError, match="no closing-price column"):
        market_data.fetch_history("AAPL", "1y")


def test_fetch_history_rejects_fewer_than_two_valid_closes(monkeypatch):
    dates = pd.date_range("2025-01-01", periods=2, freq="D")
    history = pd.DataFrame({"Close": [float("nan"), 100.0]}, index=dates)

    class InsufficientHistoryTicker:
        def __init__(self, _symbol):
            pass

        def history(self, *, period, auto_adjust):
            return history

    monkeypatch.setattr(market_data.yf, "Ticker", InsufficientHistoryTicker)

    with pytest.raises(
        market_data.MarketDataError,
        match="At least two valid closing prices",
    ):
        market_data.fetch_history("AAPL", "1y")
