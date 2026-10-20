from __future__ import annotations

import pandas as pd
import streamlit as st

from finance_assistant.analysis import summarize_history
from finance_assistant.market_data import (
    SUPPORTED_PERIODS,
    MarketDataError,
    fetch_history,
    normalize_ticker,
)

st.set_page_config(page_title="Finance Assistant", page_icon="📈", layout="wide")
st.title("Finance Assistant")
st.caption("Historical market data, explained through transparent descriptive metrics.")

with st.sidebar:
    st.header("Analysis settings")
    ticker_input = st.text_input("Ticker symbol", value="AAPL", help="Examples: AAPL, MSFT, RELIANCE.NS, BTC-USD")
    period = st.selectbox("History window", options=["1mo", "3mo", "6mo", "1y", "2y", "5y", "max"], index=3)
    refresh = st.button("Refresh market data")

@st.cache_data(ttl=300, show_spinner=False)
def load_history(symbol: str, window: str) -> pd.DataFrame:
    return fetch_history(symbol, window)

try:
    symbol = normalize_ticker(ticker_input)
    if refresh:
        load_history.clear()
    with st.spinner(f"Loading historical data for {symbol}..."):
        history = load_history(symbol, period)
    metrics = summarize_history(history)

    st.subheader(f"{symbol} · {period} history")
    st.caption(
        f"Data returned by Yahoo Finance from {metrics['first_date']} through {metrics['latest_date']}. "
        "Quotes may be delayed or unavailable for some symbols."
    )

    top = st.columns(4)
    top[0].metric("Latest close", f"{metrics['latest_close']:,.2f}")
    change = metrics["daily_change_pct"]
    top[1].metric("Last-observation change", f"{change:+.2f}%" if change is not None else "N/A")
    total = metrics["period_return_pct"]
    top[2].metric("Period return", f"{total:+.2f}%" if total is not None else "N/A")
    vol = metrics["annualized_volatility_pct"]
    top[3].metric("Annualized volatility*", f"{vol:.2f}%" if vol is not None else "N/A")

    chart_data = history[["Close"]].rename(columns={"Close": "Closing price"})
    st.line_chart(chart_data)
    st.subheader("Descriptive metrics")
    metric_rows = [
        ("Observations", metrics["observations"]),
        ("Previous close", metrics["previous_close"]),
        ("Daily change", metrics["daily_change"]),
        ("20-observation moving average", metrics["moving_average_20"]),
        ("Maximum observed drawdown", metrics["max_drawdown_pct"]),
    ]
    st.dataframe(
        pd.DataFrame(metric_rows, columns=["Metric", "Value"]),
        use_container_width=True,
        hide_index=True,
    )
    st.caption("*Annualized volatility assumes daily trading-session observations. Metrics describe historical prices and do not predict future performance.")
except ValueError as exc:
    st.error(str(exc))
except MarketDataError as exc:
    st.error(str(exc))
except Exception:
    st.error("Market data could not be loaded. Please try another symbol or refresh in a few minutes.")

st.divider()
st.caption(
    "Educational prototype only. Market data may be incomplete or delayed. "
    "Nothing on this page is personalized financial advice or a buy/sell recommendation."
)
