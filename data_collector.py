import yfinance as yf
import pandas as pd

def fetch_historical_data(ticker_symbol: str, period: str = "2y", interval: str = "1d") -> pd.DataFrame:
    """
    Fetch historical data for a given ticker from Yahoo Finance.
    For Indian stocks, append '.NS' (e.g., RELIANCE.NS).
    For Crypto, use pairs like 'BTC-USD'.
    """
    try:
        ticker = yf.Ticker(ticker_symbol)
        df = ticker.history(period=period, interval=interval)
        if df.empty:
            return pd.DataFrame()
        # Clean up column names and keep required columns
        df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
        # yfinance returns timezone-aware index sometimes, make it tz-naive for simplicity
        if df.index.tz is not None:
            df.index = df.index.tz_convert(None)
        return df
    except Exception as e:
        print(f"Error fetching data for {ticker_symbol}: {e}")
        return pd.DataFrame()

if __name__ == "__main__":
    df = fetch_historical_data("RELIANCE.NS", "1mo", "1d")
    print(df.head())
