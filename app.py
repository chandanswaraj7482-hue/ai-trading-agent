import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from data_collector import fetch_historical_data
from strategy import add_technical_indicators, generate_signals, get_latest_signal
from sentiment import analyze_sentiment

# Setup page configuration
st.set_page_config(page_title="AI Trading Pro", layout="wide", page_icon="⚡")

# Custom CSS for Professional Premium Look
st.markdown("""
<style>
    /* Hide Streamlit Default Menu and Footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Better Fonts and Padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        font-family: 'Inter', sans-serif;
    }
    
    /* Style for Metrics / Cards */
    div[data-testid="metric-container"] {
        background-color: #1E1E1E;
        border: 1px solid #333;
        padding: 1rem 2rem;
        border-radius: 0.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    
    /* Custom Titles */
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        background: -webkit-linear-gradient(45deg, #00C6FF, #0072FF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    .sub-text {
        color: #A0AEC0;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-title">⚡ AI Trading Assistant Pro</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-text">Advanced Market Scanner & Signal Generator</p>', unsafe_allow_html=True)

# Sidebar for inputs
with st.sidebar:
    st.header("Asset Settings")
    
    asset_types = [
        "Indian Stocks", 
        "US Stocks", 
        "Crypto", 
        "Forex (Currencies)", 
        "Commodities (Gold, Oil)", 
        "Mutual Funds (SIP)"
    ]
    asset_type = st.selectbox("Market Type:", asset_types)
    
    if asset_type == "Indian Stocks":
        st.info("Indian Stocks ke aage '.NS' lagayein (e.g., RELIANCE.NS, TCS.NS)")
        ticker = st.text_input("Enter Ticker:", value="RELIANCE.NS")
    elif asset_type == "US Stocks":
        st.info("US Stocks ka direct naam likhein (e.g., AAPL, TSLA, GOOGL)")
        ticker = st.text_input("Enter Ticker:", value="AAPL")
    elif asset_type == "Crypto":
        st.info("Crypto pairs likhein (e.g., BTC-USD, ETH-USD)")
        ticker = st.text_input("Enter Ticker:", value="BTC-USD")
    elif asset_type == "Forex (Currencies)":
        st.info("Forex pairs ke aage '=X' lagayein (e.g., EURUSD=X, INR=X)")
        ticker = st.text_input("Enter Ticker:", value="EURUSD=X")
    elif asset_type == "Commodities (Gold, Oil)":
        st.info("Gold: GC=F, Silver: SI=F, Crude Oil: CL=F")
        ticker = st.text_input("Enter Ticker:", value="GC=F")
    elif asset_type == "Mutual Funds (SIP)":
        st.info("Mutual Fund ka ticker likhein (e.g., 0P0000XW8F.BO - Parag Parikh Flexi Cap)")
        ticker = st.text_input("Enter Ticker:", value="0P0000XW8F.BO")
        
    period = st.selectbox("Time Period:", ["1mo", "3mo", "6mo", "1y", "2y", "5y", "10y"], index=3)
    
    analyze_button = st.button("Analyze Now 🚀")

# Create Tabs
tab1, tab2 = st.tabs(["Single Asset Analysis", "Auto-Suggest (Screener)"])

with tab1:
    if analyze_button:
        with st.spinner('Fetching Data & Running AI Analysis...'):
            # 1. Fetch Data
            df = fetch_historical_data(ticker, period=period)
            
            if df.empty:
                st.error("Data fetch karne mein problem aayi. Ticker symbol check karein.")
            else:
                # 2. Run Strategy (Indicators & Signals)
                df = add_technical_indicators(df)
                df = generate_signals(df)
                signal_data = get_latest_signal(df)
                
                # 3. Fetch Sentiment
                sentiment_data = analyze_sentiment(ticker)
                
                # Layout: Top Cards for Signals
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    currency_symbol = "₹" if asset_type in ["Indian Stocks", "Mutual Funds (SIP)"] else "$"
                    st.metric(label="Current Price", value=f"{currency_symbol}{df['Close'].iloc[-1]:.2f}")
                    
                with col2:
                    # Signal Color Formatting
                    sig_color = "green" if "BUY" in signal_data['action'] else ("red" if "SELL" in signal_data['action'] else "gray")
                    st.markdown(f"### Action: <span style='color:{sig_color}'>{signal_data['action']}</span>", unsafe_allow_html=True)
                    
                with col3:
                    sent_color = "green" if "POSITIVE" in sentiment_data['label'] else ("red" if "NEGATIVE" in sentiment_data['label'] else "gray")
                    st.markdown(f"### News Sentiment: <span style='color:{sent_color}'>{sentiment_data['label']}</span>", unsafe_allow_html=True)
    
                # Details
                st.markdown("<br>", unsafe_allow_html=True)
                st.subheader("💡 Trade Execution Plan")
                r_col1, r_col2 = st.columns(2)
                
                with r_col1:
                    st.markdown("**🤖 AI Technical Reasoning:**")
                    st.info(signal_data['reason'])
                    if signal_data['target']:
                        st.success(f"🎯 **Target Price (Take Profit):** {signal_data['target']:.2f}")
                        st.error(f"🛡️ **Stop Loss (Risk Limit):** {signal_data['stop_loss']:.2f}")
                        
                with r_col2:
                    st.markdown("**📰 Market News & Sentiment:**")
                    st.warning(f"**Sentiment Score:** {sentiment_data['score']} / 1.0")
                    with st.expander("Read Latest Market Headlines"):
                        st.write(sentiment_data['news'])
    
                # Plot Chart
                st.markdown("---")
                st.subheader("📊 Technical Chart (Price & Signals)")
                
                fig = go.Figure()
                
                # Candlestick
                fig.add_trace(go.Candlestick(
                    x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='Price'
                ))
                
                # Moving Averages
                fig.add_trace(go.Scatter(x=df.index, y=df['SMA_20'], line=dict(color='blue', width=1), name='SMA 20'))
                fig.add_trace(go.Scatter(x=df.index, y=df['SMA_50'], line=dict(color='orange', width=1), name='SMA 50'))
                
                # Buy/Sell Markers
                buy_signals = df[df['Signal'] == 1]
                sell_signals = df[df['Signal'] == -1]
                
                fig.add_trace(go.Scatter(
                    x=buy_signals.index, y=buy_signals['Close'], mode='markers',
                    marker=dict(symbol='triangle-up', size=12, color='green'), name='Buy Signal'
                ))
                
                fig.add_trace(go.Scatter(
                    x=sell_signals.index, y=sell_signals['Close'], mode='markers',
                    marker=dict(symbol='triangle-down', size=12, color='red'), name='Sell Signal'
                ))
                
                fig.update_layout(height=600, xaxis_rangeslider_visible=False, template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.header("🤖 Top Investment Suggestions")
    st.markdown("Aapko manually search karne ki zarurat nahi hai! AI khud Nifty 50 ke top stocks ko analyze karke batayega ki **aaj kya buy karna chahiye.**")
    
    # List of top Indian stocks to scan
    top_stocks = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS", "TATAMOTORS.NS", "ITC.NS", "SBIN.NS", "BHARTIARTL.NS", "L&T.NS"]
    
    if st.button("Scan Market Now 🚀", key="scan_btn"):
        with st.spinner("AI is analyzing multiple stocks... (Isme 10-15 seconds lag sakte hain)"):
            buy_suggestions = []
            
            for stock in top_stocks:
                df_scan = fetch_historical_data(stock, period="1y")
                if not df_scan.empty:
                    df_scan = add_technical_indicators(df_scan)
                    df_scan = generate_signals(df_scan)
                    sig = get_latest_signal(df_scan)
                    
                    if "BUY" in sig['action']:
                        buy_suggestions.append({
                            "Stock": stock.replace(".NS", ""),
                            "Current Price": f"₹{sig['entry']:.2f}",
                            "Target": f"₹{sig['target']:.2f}",
                            "Stop Loss": f"₹{sig['stop_loss']:.2f}",
                            "Reason": "Uptrend detected (RSI & MACD)"
                        })
            
            if buy_suggestions:
                st.success(f"🎉 AI ne {len(buy_suggestions)} stocks dhunde hain jismein abhi invest kiya ja sakta hai!")
                # Show as a table
                st.table(pd.DataFrame(buy_suggestions))
                st.info("💡 Note: Yeh sirf AI ki suggestion hai. Invest karne se pehle apni research zaroor karein.")
            else:
                st.warning("Abhi kisi bhi top stock mein clear 'BUY' signal nahi dikh raha hai. Market shayad volatile hai, kripya baad mein try karein.")
