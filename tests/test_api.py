import pandas as pd
from fastapi.testclient import TestClient

import api as api_module

client = TestClient(api_module.app)


def test_health_route():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_analysis_route_returns_metrics_and_disclaimer(monkeypatch):
    dates = pd.date_range("2025-01-01", periods=3, freq="D")
    history = pd.DataFrame({"Close": [100.0, 105.0, 110.0]}, index=dates)
    monkeypatch.setattr(api_module, "fetch_history", lambda _ticker, _period: history)

    response = client.get("/api/analysis/aapl?period=1y")

    assert response.status_code == 200
    body = response.json()
    assert body["ticker"] == "AAPL"
    assert body["metrics"]["latest_close"] == 110.0
    assert len(body["history"]) == 3
    assert "not financial advice" in body["disclaimer"].lower()


def test_analysis_route_rejects_bad_ticker():
    response = client.get("/api/analysis/INVALID%20TICKER")
    assert response.status_code == 422


def test_analysis_route_rejects_bad_period():
    response = client.get("/api/analysis/AAPL?period=10y")
    assert response.status_code == 422


def test_analysis_route_returns_502_when_provider_has_no_data(monkeypatch):
    def no_data(_ticker, _period):
        from finance_assistant.market_data import MarketDataError
        raise MarketDataError("No historical price data")

    monkeypatch.setattr(api_module, "fetch_history", no_data)
    response = client.get("/api/analysis/AAPL")
    assert response.status_code == 502
