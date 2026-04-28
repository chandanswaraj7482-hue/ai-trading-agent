import pandas as pd
import ta
import numpy as np

def add_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add technical indicators using the 'ta' library.
    """
    if df.empty:
        return df

    try:
        # RSI (Relative Strength Index)
        df['RSI'] = ta.momentum.RSIIndicator(close=df['Close'], window=14).rsi()
        
        # MACD (Moving Average Convergence Divergence)
        macd = ta.trend.MACD(close=df['Close'])
        df['MACD'] = macd.macd()
        df['MACD_Signal'] = macd.macd_signal()
        df['MACD_Hist'] = macd.macd_diff()
        
        # Moving Averages
        df['SMA_20'] = ta.trend.SMAIndicator(close=df['Close'], window=20).sma_indicator()
        df['SMA_50'] = ta.trend.SMAIndicator(close=df['Close'], window=50).sma_indicator()
        
        # Bollinger Bands
        bollinger = ta.volatility.BollingerBands(close=df['Close'], window=20, window_dev=2)
        df['BB_High'] = bollinger.bollinger_hband()
        df['BB_Low'] = bollinger.bollinger_lband()
        
    except Exception as e:
        print(f"Error adding indicators: {e}")
        
    return df

def generate_signals(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate Buy/Sell signals based on basic technical analysis rules.
    1 (Buy), -1 (Sell), 0 (Hold)
    """
    if df.empty:
        return df
        
    df['Signal'] = 0
    
    for i in range(1, len(df)):
        # Buy Signal Logic:
        # RSI crosses above 30 (oversold recovery) OR MACD crosses above Signal Line AND Price is above SMA 50
        is_rsi_buy = (df['RSI'].iloc[i-1] < 30) and (df['RSI'].iloc[i] >= 30)
        is_macd_buy = (df['MACD'].iloc[i-1] < df['MACD_Signal'].iloc[i-1]) and (df['MACD'].iloc[i] > df['MACD_Signal'].iloc[i])
        uptrend = df['Close'].iloc[i] > df['SMA_50'].iloc[i]
        
        if is_rsi_buy or (is_macd_buy and uptrend):
            df.iloc[i, df.columns.get_loc('Signal')] = 1
            
        # Sell Signal Logic:
        # RSI crosses below 70 (overbought) OR MACD crosses below Signal Line
        is_rsi_sell = (df['RSI'].iloc[i-1] > 70) and (df['RSI'].iloc[i] <= 70)
        is_macd_sell = (df['MACD'].iloc[i-1] > df['MACD_Signal'].iloc[i-1]) and (df['MACD'].iloc[i] < df['MACD_Signal'].iloc[i])
        
        if is_rsi_sell or is_macd_sell:
            df.iloc[i, df.columns.get_loc('Signal')] = -1
            
    return df

def get_latest_signal(df: pd.DataFrame) -> dict:
    """
    Extract the latest signal and calculate entry/exit levels.
    """
    if df.empty or len(df) < 1:
        return {"action": "HOLD", "reason": "Not enough data"}
        
    latest = df.iloc[-1]
    current_price = latest['Close']
    signal = latest['Signal']
    
    if pd.isna(signal):
        return {"action": "HOLD", "reason": "Calculating indicators..."}
        
    if signal == 1:
        return {
            "action": "BUY 🟢",
            "entry": current_price,
            "target": current_price * 1.05, # 5% profit target
            "stop_loss": current_price * 0.98, # 2% stop loss
            "reason": "AI Analysis: Market ka trend positive hai aur price upar jane ke chances zyada hain. Aap is price par buy kar sakte hain."
        }
    elif signal == -1:
        return {
            "action": "SELL 🔴",
            "entry": current_price,
            "target": current_price * 0.95, 
            "stop_loss": current_price * 1.02,
            "reason": "AI Analysis: Market mein girawat (downtrend) aane ki sambhavna hai. Agar aapne pehle se buy kiya hai, to abhi bechna safe rahega."
        }
    else:
        return {
            "action": "HOLD ⚪",
            "entry": current_price,
            "target": None,
            "stop_loss": None,
            "reason": "AI Analysis: Market abhi confuse hai (na upar ja raha hai na niche). Abhi koi naya trade mat lijiye, thoda wait kijiye."
        }
