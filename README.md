# Finance Assistant — Market Analysis Prototype

[![Tests](https://github.com/nikhil-247/Finance-assistant/actions/workflows/tests.yml/badge.svg)](https://github.com/nikhil-247/Finance-assistant/actions/workflows/tests.yml)

A small Python application for exploring historical market prices and calculating transparent, descriptive metrics. It provides both a Streamlit dashboard and a FastAPI endpoint, backed by Yahoo Finance history through `yfinance`.

> **Scope:** This repository is a market-data analysis prototype, not a multi-agent trading system. It does not execute trades, provide personalized investment advice, or predict future prices. Yahoo Finance data may be delayed, incomplete, or unavailable for some symbols.

## Features

- Validate ticker symbols and supported history windows before calling the data provider.
- Fetch, clean, and sort historical closing-price observations; return clear domain errors when provider data is missing or unusable.
- Calculate latest close, last-observation change, period return, 20-observation moving average, annualized historical volatility, and maximum observed drawdown.
- Explore the price history and descriptive metrics in a Streamlit dashboard with short-lived caching and a manual refresh control.
- Access the same analysis through a FastAPI endpoint with input validation, bounded history output, health status, and API documentation.
- Test calculations, validation, API responses, and provider failure paths with fixed or mocked data.
- Run automated tests on Python 3.11 and 3.12 through GitHub Actions.

## Tech stack

- Python 3.11+
- pandas, yfinance
- FastAPI and Uvicorn
- Streamlit
- pytest and FastAPI TestClient
- GitHub Actions

## Run locally

Clone the repository and create an environment:

```bash
git clone https://github.com/nikhil-247/Finance-assistant.git
cd Finance-assistant
python -m venv .venv
```

Activate the environment and install development dependencies:

```bash
# Windows PowerShell
.venv\\Scripts\\Activate.ps1

# macOS/Linux
source .venv/bin/activate

python -m pip install -r requirements-dev.txt
```

### Streamlit dashboard

```bash
streamlit run app.py
```

Enter a ticker such as `AAPL`, `MSFT`, `RELIANCE.NS`, or `BTC-USD` and choose the period to analyze.

### FastAPI service

In another terminal:

```bash
uvicorn api:app --reload --port 8000
```

- Health: `GET http://127.0.0.1:8000/health`
- Analysis: `GET http://127.0.0.1:8000/api/analysis/AAPL?period=1y`
- Interactive docs: `http://127.0.0.1:8000/docs`

Supported history periods: `1mo`, `3mo`, `6mo`, `1y`, `2y`, `5y`, and `max`.

## Tests

Run the local test suite:

```bash
python -m pytest -q
```

Tests cover metric calculations, malformed ticker and period inputs, history serialization, API responses, and provider failures. Provider calls are mocked in tests, so the suite does not depend on a live Yahoo Finance connection. GitHub Actions runs the tests on pushes to `main` and `improve/**`, and on pull requests targeting `main`.

## Metric definitions

- **Last-observation change %:** percentage change between the most recent and previous available closing-price observations; these observations are not guaranteed to represent consecutive calendar days.
- **Period return %:** change from the first to the latest close returned for the selected history window.
- **20-observation moving average:** average of the last 20 available closing-price observations (or fewer if the period has fewer observations).
- **Annualized volatility:** standard deviation of recent daily percentage returns multiplied by the square root of 252, when sufficient observations are available.
- **Maximum observed drawdown:** largest percentage decline from a running closing-price peak within the selected history window.

These values summarize past prices only. Volatility uses a daily-trading-session assumption, and metrics can vary with the data returned by the provider.

## Current limitations

- This version has no LLM, multi-agent orchestration, portfolio/account integration, trade execution, or future-price prediction.
- User preferences and watchlists are not persisted.
- Live data access depends on Yahoo Finance and is not guaranteed; caching is short-lived and is not a guarantee of freshness.
- Ticker validation catches malformed input but does not certify that a symbol is valid or listed.
- The service is a prototype and does not yet provide production-grade rate limiting, authentication, monitoring, or an SLA.
- No investment outcome or performance guarantee is implied.

## Next steps

1. Add explicit data freshness timestamps, provider attribution, and clearer stale-data status.
2. Add a tested comparison workflow for multiple tickers.
3. Improve deployment configuration, rate limiting, structured observability, and operational documentation.
4. If AI-generated summaries are introduced, evaluate them against a documented dataset and show source provenance and uncertainty.

## Author

Nikhil Kushwaha · [GitHub](https://github.com/nikhil-247) · [LinkedIn](https://www.linkedin.com/in/nikhil-kushwaha-265880273)
