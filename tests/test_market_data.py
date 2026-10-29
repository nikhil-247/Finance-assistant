import pandas as pd
import pytest

from finance_assistant import market_data


def test_fetch_history_normalizes_ticker_and_returns_sorted_clean_data(monkeypatch):
    source = pd.DataFrame(
        {"Close": [None, 12.0, 10.0]},
        index=pd.to_datetime(["2025-01-03", "2025-01-02", "2025-01-01"]),
    )
    calls = {}

    class FakeTicker:
        def __init__(self, symbol):
            calls["symbol"] = symbol

        def history(self, *, period, auto_adjust):
            calls["period"] = period
            calls["auto_adjust"] = auto_adjust
            return source

    monkeypatch.setattr(market_data.yf, "Ticker", FakeTicker)

    result = market_data.fetch_history(" aapl ", "1y")

    assert calls == {"symbol": "AAPL", "period": "1y", "auto_adjust": True}
    assert result["Close"].tolist() == [10.0, 12.0]
    assert result.index.is_monotonic_increasing


def test_fetch_history_rejects_unsupported_period_before_provider_call(monkeypatch):
    def unexpected_call(_symbol):
        pytest.fail("Provider should not be called for an invalid period")

    monkeypatch.setattr(market_data.yf, "Ticker", unexpected_call)

    with pytest.raises(ValueError, match="Unsupported period"):
        market_data.fetch_history("AAPL", "10y")


def test_fetch_history_wraps_provider_errors(monkeypatch):
    class BrokenTicker:
        def __init__(self, _symbol):
            pass

        def history(self, **_kwargs):
            raise TimeoutError("provider details should not leak")

    monkeypatch.setattr(market_data.yf, "Ticker", BrokenTicker)

    with pytest.raises(market_data.MarketDataError, match="Unable to fetch market data"):
        market_data.fetch_history("AAPL", "1y")


@pytest.mark.parametrize(
    "frame, message",
    [
        (pd.DataFrame(), "No historical price data"),
        (pd.DataFrame({"Open": [1.0, 2.0]}), "no closing-price column"),
        (pd.DataFrame({"Close": [None, 1.0]}), "At least two valid"),
    ],
)
def test_fetch_history_rejects_unusable_provider_responses(monkeypatch, frame, message):
    class FakeTicker:
        def __init__(self, _symbol):
            pass

        def history(self, **_kwargs):
            return frame

    monkeypatch.setattr(market_data.yf, "Ticker", FakeTicker)

    with pytest.raises(market_data.MarketDataError, match=message):
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
