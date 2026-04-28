import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sys
import importlib

# Force reload of our custom modules to clear Streamlit's old cache
if "strategy" in sys.modules:
    importlib.reload(sys.modules["strategy"])
if "data_collector" in sys.modules:
    importlib.reload(sys.modules["data_collector"])

from data_collector import fetch_historical_data
from strategy import add_technical_indicators, generate_signals, get_latest_signal, predict_future_price, run_backtest, calculate_ai_score
from sentiment import analyze_sentiment

# Setup page configuration
st.set_page_config(page_title="AI Trading Pro", layout="wide", page_icon="⚡")

# Custom CSS for Professional Premium Look
st.markdown("""
<style>
    /* Hide Streamlit Default Menu and Footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Better Fonts and Padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        font-family: 'Inter', sans-serif;
    }
    
    /* Style for Metrics / Cards */
    div[data-testid="metric-container"] {
        background-color: #001e36;
        border: 1px solid #31a8ff;
        padding: 1rem 2rem;
        border-radius: 0.5rem;
        box-shadow: 0 0 10px rgba(49, 168, 255, 0.2);
    }
    
    /* Custom Titles */
    .main-title {
        font-size: 2.8rem;
        font-weight: 800;
        background: -webkit-linear-gradient(45deg, #ff3366, #ff9a00);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    .sub-text {
        color: #A0AEC0;
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
    }
    
    /* Developer Tag */
    .dev-tag {
        font-size: 0.9rem;
        color: #ff3366;
        font-weight: 600;
        letter-spacing: 1px;
        margin-bottom: 2rem;
        display: inline-block;
        padding: 4px 12px;
        border: 1px solid #ff3366;
        border-radius: 20px;
        background-color: rgba(255, 51, 102, 0.1);
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-title">⚡ AI Trading Pro</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-text">Advanced Market Scanner & Signal Generator</p>', unsafe_allow_html=True)
st.markdown('<div class="dev-tag">Developed by CS Chandan</div>', unsafe_allow_html=True)

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
tab_guide, tab_screener, tab_single = st.tabs(["🎓 Start Here (For Beginners)", "🤖 Auto-Suggest (Best Stocks)", "🔍 Search Any Stock"])

with tab_guide:
    st.header("Trading mein naye hain? Koi baat nahi! 🤗")
    st.markdown("""
    Agar aapko trading ka 'T' bhi nahi aata, to ghabrane ki zaroorat nahi hai. Yeh AI aapka personal assistant hai jo aapke liye sabse mushkil kaam (Data Analysis) khud karega.
    
    ### 💸 Paise Kaise Kamayein? (Sirf 3 Steps Mein)
    
    **Step 1: Apna Trading Account Kholein (Demat Account)**
    - Share khareedne ke liye aapko ek app chahiye hota hai. Aap apne phone mein **Groww, Zerodha (Kite), Upstox, ya AngelOne** mein se koi bhi free app download karke apna account bana lijiye.
    
    **Step 2: AI se Puchiye Aaj Kya Khareedein?**
    - Upar diye gaye **"🤖 Auto-Suggest (Best Stocks)"** tab par click karein.
    - **"Scan Market Now"** button dabayein.
    - AI khud batayega ki aaj market mein sabse accha stock (share) kaunsa hai.
    
    **Step 3: Khareedein aur Target/Stop-Loss Lagayein**
    - Jo stock AI ne bataya, use apne Groww/Zerodha app mein search karein.
    - **Buy (Khareedein):** Jo "Current Price" AI ne bataya hai, us rate par buy karein.
    - **Target Price:** Yeh wo rate hai jispar pahunchte hi aapko apna share bechkar **Profit (Munafa)** nikal lena hai.
    - **Stop Loss:** Yeh sabse zaroori hai! Agar by-chance market girta hai, to ye rate aate hi share apne aap bik jayega taaki aapka **bada nuksan na ho**.
    
    ---
    💡 **Golden Rule:** Kabhi bhi apna saara paisa ek hi share mein mat lagaiye. Shuruwat mein chhote amount (jaise ₹500 ya ₹1000) se start karein taaki aap system samajh sakein!
    """)

with tab_single:
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
    
                # --- NEW: AI CONFIDENCE SCORE ---
                ai_score_data = calculate_ai_score(df)
                st.markdown(f"### 🎯 AI Confidence Score: {ai_score_data['score']}/100 ({ai_score_data['label']})")
                st.progress(ai_score_data['score'])
                
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
    
                # --- SUPER POWERS (Forecasting & Backtesting) ---
                st.markdown("---")
                st.subheader("⚡ AI Super Powers (Advanced Analysis)")
                
                # Run Prediction & Backtest
                prediction = predict_future_price(df, days=7)
                backtest = run_backtest(df, initial_capital=10000)
                
                sp_col1, sp_col2 = st.columns(2)
                
                with sp_col1:
                    st.markdown("**🔮 7-Day Price Prediction:**")
                    if prediction['status'] == 'success':
                        st.info(f"AI ka manna hai ki agle 7 din mein trend **{prediction['trend']}** rahega.")
                        st.success(f"**Predicted Price:** {currency_symbol}{prediction['predicted_price']:.2f}")
                    else:
                        st.warning("Prediction ke liye data kam hai.")
                        
                with sp_col2:
                    st.markdown("**⏳ Backtesting (Trust Score):**")
                    st.info(f"Agar is AI ki baat maankar aapne shuru mein **{currency_symbol}10,000** lagaye hote, to aaj aapke paas hote:")
                    
                    bt_color = "normal" if backtest['profit_pct'] > 0 else "inverse"
                    st.metric(label="Final Amount (Simulated)", value=f"{currency_symbol}{backtest['final']:.2f}", delta=f"{backtest['profit_pct']:.2f}% Profit")
                    st.caption(f"Total Trades Executed: {backtest['trades']}")

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

with tab_screener:
    st.header("🤖 Top Investment Suggestions")
    st.markdown("Aapko manually search karne ki zarurat nahi hai! AI khud Nifty 50 ke top stocks ko analyze karke batayega ki **aaj kya buy karna chahiye.**")
    
    # List of Nifty 50 stocks to scan
    top_stocks = [
        "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS", 
        "TATAMOTORS.NS", "ITC.NS", "SBIN.NS", "BHARTIARTL.NS", "LT.NS",
        "BAJFINANCE.NS", "ASIANPAINT.NS", "HCLTECH.NS", "MARUTI.NS", "SUNPHARMA.NS", 
        "ULTRACEMCO.NS", "WIPRO.NS", "KOTAKBANK.NS", "TITAN.NS", "ONGC.NS",
        "TATASTEEL.NS", "NTPC.NS", "POWERGRID.NS", "M&M.NS", "BAJAJFINSV.NS",
        "ADANIENT.NS", "ADANIPORTS.NS", "COALINDIA.NS", "APOLLOHOSP.NS", "BRITANNIA.NS",
        "CIPLA.NS", "DRREDDY.NS", "EICHERMOT.NS", "GRASIM.NS", "HDFCLIFE.NS",
        "HEROMOTOCO.NS", "HINDALCO.NS", "HINDUNILVR.NS", "INDUSINDBK.NS", "JSWSTEEL.NS",
        "NESTLEIND.NS", "TECHM.NS", "TATACHEM.NS", "TATACONSUM.NS"
    ]
    
    if st.button("Scan Market Now 🚀", key="scan_btn"):
        progress_text = st.empty()
        progress_bar = st.progress(0)
        
        all_results = []
        
        for i, stock in enumerate(top_stocks):
            # Update UI to show AI is working
            progress_text.markdown(f"**🔍 AI Brain is analyzing:** `{stock}` ({i+1}/{len(top_stocks)})...")
            progress_bar.progress((i + 1) / len(top_stocks))
            
            df_scan = fetch_historical_data(stock, period="1y")
            if not df_scan.empty:
                df_scan = add_technical_indicators(df_scan)
                df_scan = generate_signals(df_scan)
                sig = get_latest_signal(df_scan)
                score_data = calculate_ai_score(df_scan)
                
                all_results.append({
                    "Stock": stock.replace(".NS", ""),
                    "AI Score": f"{score_data['score']}/100 ({score_data['label']})",
                    "Raw_Score": score_data['score'], # Hidden column for sorting
                    "Current Price": f"₹{sig['entry']:.2f}",
                    "Target (ATR)": f"₹{sig['target']:.2f}" if sig['target'] else "-",
                    "Stop Loss (ATR)": f"₹{sig['stop_loss']:.2f}" if sig['stop_loss'] else "-"
                })
                
        progress_text.success("✅ Nifty 50 Deep Scan Complete!")
        
        if all_results:
            # Sort by AI Score descending
            all_results = sorted(all_results, key=lambda x: x['Raw_Score'], reverse=True)
            
            # Remove the hidden score column
            for res in all_results:
                del res['Raw_Score']
                
            # Get Top 10 Best Opportunities
            top_10 = all_results[:10]
            
            st.success(f"🎉 AI ne Nifty 50 ko scan karke ye **Top 10 Best Stocks** nikale hain aaj ke liye!")
            # Show as a table
            st.table(pd.DataFrame(top_10))
            st.info("💡 Note: Jis stock ka AI Score sabse zyada hai (jaise Strong Buy 🔥), usme invest karna sabse safe hai.")
        else:
            st.warning("Data fetch karne mein problem aayi. Kripya baad mein try karein.")
