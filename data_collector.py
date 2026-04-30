import yfinance as yf
import pandas as pd
import requests
import json
import time

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

# Global session for NSE to maintain cookies
nse_session = requests.Session()
nse_headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br"
}

def init_nse_session():
    try:
        nse_session.get("https://www.nseindia.com", headers=nse_headers, timeout=10)
        # Small delay to ensure cookies are set
        time.sleep(1)
    except:
        pass

def fetch_nse_option_chain(symbol: str):
    """
    Directly fetch option chain from NSE website.
    """
    if symbol in ["^NSEI", "NIFTY"]:
        url = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
    elif symbol in ["^NSEBANK", "BANKNIFTY"]:
        url = "https://www.nseindia.com/api/option-chain-indices?symbol=BANKNIFTY"
    else:
        # Clean ticker for NSE (e.g., RELIANCE.NS -> RELIANCE)
        clean_symbol = symbol.replace(".NS", "")
        url = f"https://www.nseindia.com/api/option-chain-equities?symbol={clean_symbol}"

    try:
        init_nse_session()
        response = nse_session.get(url, headers=nse_headers, timeout=15)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"NSE Fetch Error: {e}")
        return None

def get_option_expiry_dates(ticker_symbol: str):
    """
    Get available option expiry dates for a ticker.
    """
    # Try Yahoo first
    try:
        ticker = yf.Ticker(ticker_symbol)
        expiries = list(ticker.options)
        if expiries:
            return expiries
    except:
        pass
        
    # Fallback to Real NSE Data
    nse_data = fetch_nse_option_chain(ticker_symbol)
    if nse_data and 'records' in nse_data:
        return nse_data['records']['expiryDates']
    
    return []

def get_option_chain(ticker_symbol: str, expiry_date: str):
    """
    Get option chain for a specific ticker and expiry date.
    Returns (calls, puts) DataFrames.
    """
    # Try Yahoo first
    try:
        ticker = yf.Ticker(ticker_symbol)
        chain = ticker.option_chain(expiry_date)
        if not chain.calls.empty:
            return chain.calls, chain.puts
    except:
        pass

    # Fallback to Real NSE Data
    nse_data = fetch_nse_option_chain(ticker_symbol)
    if nse_data and 'records' in nse_data:
        # Filter for selected expiry
        filtered_data = [d for d in nse_data['filtered']['data'] if d['expiryDate'] == expiry_date]
        
        calls_list = []
        puts_list = []
        
        for item in filtered_data:
            strike = item['strikePrice']
            if 'CE' in item:
                ce = item['CE']
                calls_list.append({
                    'strike': strike,
                    'lastPrice': ce.get('lastPrice', 0),
                    'change': ce.get('change', 0),
                    'openInterest': ce.get('openInterest', 0),
                    'volume': ce.get('totalTradedVolume', 0)
                })
            if 'PE' in item:
                pe = item['PE']
                puts_list.append({
                    'strike': strike,
                    'lastPrice': pe.get('lastPrice', 0),
                    'change': pe.get('change', 0),
                    'openInterest': pe.get('openInterest', 0),
                    'volume': pe.get('totalTradedVolume', 0)
                })
        
        return pd.DataFrame(calls_list), pd.DataFrame(puts_list)

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
