# Finance Assistant — Market Analysis Prototype

A small Python application for exploring historical market prices and calculating transparent, descriptive metrics. It provides both a Streamlit dashboard and a FastAPI endpoint, backed by Yahoo Finance history through `yfinance`.

> **Scope:** This repository is a market-data analysis prototype, not a multi-agent trading system. It does not execute trades, provide personalized investment advice, or predict future prices. Yahoo Finance data may be delayed, incomplete, or unavailable for some symbols.

## Features

- Validate ticker symbols and supported history windows.
- Fetch historical closing prices through `yfinance`.
- Calculate the latest close, last-observation change, period return, 20-observation moving average, annualized historical volatility, and maximum observed drawdown.
- View a price chart and metrics in Streamlit.
- Access the same analysis through a FastAPI endpoint.
- Unit and API tests that mock provider data so routine tests do not depend on a live market-data service.

## Tech stack

- Python 3.12+
- pandas, yfinance
- FastAPI and Uvicorn
- Streamlit
- pytest and FastAPI TestClient

## Run locally

Clone the repository and create an environment:

```bash
git clone https://github.com/nikhil-247/Finance-assistant.git
cd Finance-assistant
python -m venv .venv
```

Activate the environment and install dependencies:

```bash
# Windows PowerShell
.venv\Scripts\Activate.ps1

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

```bash
python -m pytest -q
```

Tests cover input validation, metric calculations, API responses, and provider-error handling. They use fixed data or mocked provider results, so they do not verify live Yahoo Finance availability.

## Metric definitions

- **Daily change %:** percentage change between the most recent and previous available closing-price observations.
- **Period return %:** change from the first to the latest close returned for the selected history window.
- **20-observation moving average:** average of the last 20 available closing-price observations (or fewer if the period has fewer observations).
- **Annualized volatility:** standard deviation of recent daily percentage returns multiplied by the square root of 252, when sufficient observations are available.
- **Maximum observed drawdown:** largest percentage decline from a running closing-price peak within the selected history window.

These values summarize past prices only. Volatility uses a daily-trading-session assumption, and metrics can vary with the data returned by the provider.

## Current limitations

- There is no LLM, multi-agent orchestration, portfolio/account integration, or trade execution in this version.
- This version does not persist user preferences or watchlists.
- Live data access depends on Yahoo Finance and is not guaranteed.
- Ticker validation prevents malformed input, but it does not certify that a symbol is valid or listed.
- No investment outcome or performance guarantee is implied.

## Next steps

1. Add cached, timestamped market data with provider attribution and status.
2. Add an explicit comparison workflow for multiple tickers.
3. Improve deployment configuration, rate limiting, and observability.
4. Add a documented evaluation set for any future AI-generated summaries, with sources and uncertainty shown to users.

## Author

Nikhil Kushwaha · [GitHub](https://github.com/nikhil-247) · [LinkedIn](https://www.linkedin.com/in/nikhil-kushwaha-265880273)
