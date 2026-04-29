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

def get_option_expiry_dates(ticker_symbol: str):
    """
    Get available option expiry dates for a ticker.
    """
    try:
        ticker = yf.Ticker(ticker_symbol)
        return ticker.options
    except Exception as e:
        print(f"Error fetching expiry dates: {e}")
        return []

def get_option_chain(ticker_symbol: str, expiry_date: str):
    """
    Get option chain for a specific ticker and expiry date.
    Returns (calls, puts) DataFrames.
    """
    try:
        ticker = yf.Ticker(ticker_symbol)
        chain = ticker.option_chain(expiry_date)
        return chain.calls, chain.puts
    except Exception as e:
        print(f"Error fetching option chain: {e}")
        return pd.DataFrame(), pd.DataFrame()

if __name__ == "__main__":
    df = fetch_historical_data("RELIANCE.NS", "1mo", "1d")
    print("Price Data:")
    print(df.head())
    
    expiries = get_option_expiry_dates("RELIANCE.NS")
    if expiries:
        print(f"\nExpiries: {expiries[:3]}")
        calls, puts = get_option_chain("RELIANCE.NS", expiries[0])
        print(f"\nCalls for {expiries[0]}:")
        print(calls.head())
