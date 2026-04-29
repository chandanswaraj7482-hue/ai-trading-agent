import pandas as pd
import ta
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from datetime import timedelta

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
        
        # ATR (Average True Range) for Smart Risk Management
        df['ATR'] = ta.volatility.AverageTrueRange(high=df['High'], low=df['Low'], close=df['Close'], window=14).average_true_range()
        
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
    
    atr = latest.get('ATR', current_price * 0.02)
    if pd.isna(atr):
        atr = current_price * 0.02
        
    score_data = calculate_ai_score(df)
    score = score_data['score']
    
    # Generate Target and Stop Loss based on current price and ATR regardless of strict signal
    buy_target = current_price + (2.0 * atr)
    buy_stop = current_price - (1.5 * atr)
    sell_target = current_price - (2.0 * atr)
    sell_stop = current_price + (1.5 * atr)
    
    if signal == 1 or score >= 60:
        return {
            "action": "BUY 🟢",
            "entry": current_price,
            "target": buy_target,
            "stop_loss": buy_stop,
            "reason": "AI Analysis: Trend positive hai. ATR ke hisaab se Stop-Loss aur Target set kiya gaya hai."
        }
    elif signal == -1 or score <= 40:
        return {
            "action": "SELL 🔴",
            "entry": current_price,
            "target": sell_target, 
            "stop_loss": sell_stop,
            "reason": "AI Analysis: Market mein girawat aane ki sambhavna hai. Bechna safe rahega."
        }
    else:
        return {
            "action": "HOLD ⚪",
            "entry": current_price,
            "target": buy_target, # Give potential levels even for hold
            "stop_loss": buy_stop,
            "reason": "AI Analysis: Market abhi confuse hai. Agar aap risk lena chahte hain to Target/Stop-Loss limits dekh sakte hain."
        }

def predict_future_price(df: pd.DataFrame, days: int = 7) -> dict:
    """
    Predict future price using RandomForestRegressor based on the last 30 days of data.
    """
    if df.empty or len(df) < 30:
        return {"status": "error", "message": "Not enough data for prediction"}
        
    # Use last 30 days to train an advanced Random Forest model
    recent_df = df.tail(30).copy()
    recent_df['DayIndex'] = np.arange(len(recent_df))
    
    X = recent_df[['DayIndex']].values
    y = recent_df['Close'].values
    
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)
    
    # Predict X days into the future
    future_X = np.array([[len(recent_df) + days - 1]])
    predicted_price = model.predict(future_X)[0]
    
    current_price = y[-1]
    trend = "UP 📈" if predicted_price > current_price else "DOWN 📉"
    
    return {
        "status": "success",
        "predicted_price": predicted_price,
        "trend": trend,
        "days": days
    }

def run_backtest(df: pd.DataFrame, initial_capital: float = 10000.0) -> dict:
    """
    Simulate trading over the historical data using the generated signals.
    """
    if df.empty or 'Signal' not in df.columns:
        return {"profit_percentage": 0, "final_capital": initial_capital, "trades": 0}
        
    capital = initial_capital
    position = 0 # 0 means no stock, 1 means holding stock
    buy_price = 0
    trades_executed = 0
    
    for i in range(len(df)):
        signal = df['Signal'].iloc[i]
        price = df['Close'].iloc[i]
        
        # Buy condition
        if signal == 1 and position == 0:
            position = capital / price # Buy as many shares as possible
            capital = 0
            buy_price = price
            trades_executed += 1
            
        # Sell condition
        elif signal == -1 and position > 0:
            capital = position * price # Sell all shares
            position = 0
            trades_executed += 1
            
    # Calculate final value if still holding at the end
    if position > 0:
        capital = position * df['Close'].iloc[-1]
        
    profit = capital - initial_capital
    profit_pct = (profit / initial_capital) * 100
    
    return {
        "initial": initial_capital,
        "final": capital,
        "profit_pct": profit_pct,
        "trades": trades_executed
    }

def calculate_ai_score(df: pd.DataFrame) -> dict:
    """
    Calculate an AI Confidence Score (0-100) based on multiple technical factors.
    """
    if df.empty or len(df) < 5:
        return {"score": 0, "label": "Unknown"}
        
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    
    score = 50 # Start neutral
    
    # Factor 1: Trend (Price vs SMA 50 and SMA 20)
    sma50 = latest.get('SMA_50', 0)
    sma20 = latest.get('SMA_20', 0)
    close = latest['Close']
    
    if not pd.isna(sma50) and not pd.isna(sma20):
        if close > sma20 > sma50: score += 20
        elif close > sma50: score += 10
        elif close < sma20 < sma50: score -= 20
        elif close < sma50: score -= 10
        
    # Factor 2: Momentum (RSI)
    rsi = latest.get('RSI', 50)
    if not pd.isna(rsi):
        if 40 <= rsi <= 60: score += 5
        elif 30 <= rsi < 40: score += 15 # Nearing oversold, good value
        elif rsi < 30: score += 25 # Oversold bounce potential
        elif 60 < rsi <= 70: score -= 5
        elif rsi > 70: score -= 25 # Overbought, risky
        
    # Factor 3: MACD Momentum
    macd = latest.get('MACD', 0)
    macd_sig = latest.get('MACD_Signal', 0)
    if not pd.isna(macd) and not pd.isna(macd_sig):
        if macd > macd_sig: 
            # Is the gap widening?
            prev_macd = prev.get('MACD', 0)
            prev_sig = prev.get('MACD_Signal', 0)
            if (macd - macd_sig) > (prev_macd - prev_sig):
                score += 15 # Strong momentum
            else:
                score += 5 # Weakening momentum
        else:
            score -= 15
            
    # Factor 4: Bollinger Band Position
    bb_low = latest.get('BB_Low', 0)
    bb_high = latest.get('BB_High', 0)
    if not pd.isna(bb_low) and not pd.isna(bb_high) and (bb_high - bb_low) > 0:
        position = (close - bb_low) / (bb_high - bb_low)
        if position < 0.2: score += 10 # Near bottom band
        elif position > 0.8: score -= 10 # Near top band
        
    # Cap score between 0 and 100
    score = max(0, min(100, score))
    
    if score >= 75:
        label = "Strong Buy 🔥"
    elif score >= 60:
        label = "Buy 👍"
    elif score <= 25:
        label = "Strong Sell 🛑"
    elif score <= 40:
        label = "Sell 👎"
    else:
        label = "Hold ⚪"
        
    return {"score": int(score), "label": label}

# --- NEW: OPTIONS MODULE ---
from scipy.stats import norm

def calculate_greeks(S, K, T, v, r=0.07, option_type='call'):
    """
    Calculate Greeks using Black-Scholes model.
    S: Current Price
    K: Strike Price
    T: Time to Expiry (in years)
    v: Volatility (decimal, e.g. 0.20 for 20%)
    r: Risk-free rate (default 7% for India)
    """
    if T <= 0: return {"delta": 0, "theta": 0, "gamma": 0, "vega": 0}
    
    d1 = (np.log(S / K) + (r + 0.5 * v ** 2) * T) / (v * np.sqrt(T))
    d2 = d1 - v * np.sqrt(T)
    
    if option_type == 'call':
        delta = norm.cdf(d1)
        theta = -(S * norm.pdf(d1) * v / (2 * np.sqrt(T))) - r * K * np.exp(-r * T) * norm.cdf(d2)
    else:
        delta = norm.cdf(d1) - 1
        theta = -(S * norm.pdf(d1) * v / (2 * np.sqrt(T))) + r * K * np.exp(-r * T) * norm.cdf(-d2)
        
    gamma = norm.pdf(d1) / (S * v * np.sqrt(T))
    vega = S * norm.pdf(d1) * np.sqrt(T)
    
    return {
        "delta": round(delta, 3),
        "theta": round(theta / 365, 3), # Daily theta
        "gamma": round(gamma, 4),
        "vega": round(vega / 100, 3) # Per 1% change
    }

def suggest_option_strategies(ticker_symbol, current_price, signal_data, ai_score):
    """
    Suggest specific option strategies based on technical signals.
    """
    strategies = []
    
    if "BUY" in signal_data['action'] or ai_score >= 70:
        strategies.append({
            "name": "Bull Call Spread",
            "type": "Bullish (Safe)",
            "setup": f"Buy 1 ITM Call + Sell 1 OTM Call",
            "benefit": "Lower cost, limited risk, works in moderate uptrend."
        })
        strategies.append({
            "name": "Naked Call Buy",
            "type": "Aggressive Bullish",
            "setup": f"Buy ATM Call",
            "benefit": "High profit potential if price jumps quickly."
        })
    elif "SELL" in signal_data['action'] or ai_score <= 30:
        strategies.append({
            "name": "Bear Put Spread",
            "type": "Bearish (Safe)",
            "setup": f"Buy 1 ITM Put + Sell 1 OTM Put",
            "benefit": "Protects against time decay, limited risk."
        })
        strategies.append({
            "name": "Naked Put Buy",
            "type": "Aggressive Bearish",
            "setup": f"Buy ATM Put",
            "benefit": "Profit from fast market fall."
        })
    else:
        strategies.append({
            "name": "Short Strangle",
            "type": "Neutral (Sideways)",
            "setup": "Sell 1 OTM Call + Sell 1 OTM Put",
            "benefit": "Profit from time decay if market stays range-bound."
        })
        
    return strategies

def calculate_pcr(calls, puts):
    """Calculate Put-Call Ratio based on Open Interest."""
    total_call_oi = calls['openInterest'].sum()
    total_put_oi = puts['openInterest'].sum()
    if total_call_oi == 0 or pd.isna(total_call_oi): return 0
    return round(total_put_oi / total_call_oi, 2)

def calculate_max_pain(calls, puts):
    """
    Simplified Max Pain calculation.
    Max Pain is the strike price where the total loss for option buyers is minimum.
    """
    if calls.empty or puts.empty: return 0
    strikes = calls['strike'].values
    losses = []
    
    for strike in strikes:
        call_loss = calls[calls['strike'] < strike].apply(lambda x: (strike - x['strike']) * x['openInterest'] if not pd.isna(x['openInterest']) else 0, axis=1).sum()
        put_loss = puts[puts['strike'] > strike].apply(lambda x: (x['strike'] - strike) * x['openInterest'] if not pd.isna(x['openInterest']) else 0, axis=1).sum()
        losses.append(call_loss + put_loss)
        
    if not losses: return 0
    return strikes[np.argmin(losses)]

def generate_synthetic_option_chain(current_price, volatility=0.20):
    """
    Generate a synthetic option chain for demonstration/analysis when real data is missing.
    """
    atm_strike = round(current_price / 50) * 50 if current_price > 500 else round(current_price / 10) * 10
    strikes = [atm_strike + (i * (50 if current_price > 500 else 10)) for i in range(-10, 11)]
    
    calls_data = []
    puts_data = []
    
    for K in strikes:
        greeks = calculate_greeks(current_price, K, 0.05, volatility, option_type='call')
        # Simple premium approximation
        c_price = max(1.0, (current_price - K) if current_price > K else (K - current_price) * 0.1)
        p_price = max(1.0, (K - current_price) if K > current_price else (current_price - K) * 0.1)
        
        calls_data.append({
            'strike': float(K), 'lastPrice': round(c_price, 2), 'change': 0, 
            'openInterest': int(np.random.randint(1000, 10000)), 'delta': greeks['delta']
        })
        puts_data.append({
            'strike': float(K), 'lastPrice': round(p_price, 2), 'change': 0, 
            'openInterest': int(np.random.randint(1000, 10000)), 'delta': calculate_greeks(current_price, K, 0.05, volatility, option_type='put')['delta']
        })
        
    return pd.DataFrame(calls_data), pd.DataFrame(puts_data)
