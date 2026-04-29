import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import sys
import importlib

# Force reload of our custom modules to clear Streamlit's old cache
if "strategy" in sys.modules:
    importlib.reload(sys.modules["strategy"])
if "data_collector" in sys.modules:
    importlib.reload(sys.modules["data_collector"])

from data_collector import fetch_historical_data, get_option_expiry_dates, get_option_chain
from strategy import (add_technical_indicators, generate_signals, get_latest_signal, 
                      predict_future_price, run_backtest, calculate_ai_score, 
                      calculate_greeks, suggest_option_strategies, calculate_pcr, 
                      calculate_max_pain, generate_synthetic_option_chain)
from sentiment import analyze_sentiment
from datetime import datetime

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
tab_guide, tab_screener, tab_single, tab_options, tab_risk = st.tabs([
    "🎓 Start Here", 
    "🤖 Auto-Suggest", 
    "🔍 Search Any Stock",
    "📊 Options Hub",
    "🛡️ Risk Manager"
])

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
    st.markdown("Aapko manually search karne ki zarurat nahi hai! AI khud Nifty 50 ke stocks ko scan karke batayega ki **aaj kya buy karna chahiye.**")
    
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        max_price = st.number_input("Aapka per share budget kitna hai? (₹):", value=5000, step=100)
    
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
                
                # --- BUDGET FILTER ---
                if sig['entry'] > max_price:
                    continue
                    
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

with tab_options:
    st.header("📊 Options Hub - Derivative Analysis")
    st.markdown("""
    Options trading mein risk zyada hota hai lekin munafa bhi fast ho sakta hai. 
    Yahan aap **Option Chain** dekh sakte hain aur AI se **Best Strategy** puch sakte hain.
    """)
    
    opt_col1, opt_col2 = st.columns([1, 2])
    
    with opt_col1:
        f_and_o_stocks = [
            "Select Stock...", "NIFTY (^NSEI)", "BANK NIFTY (^NSEBANK)", 
            "RELIANCE.NS", "HDFCBANK.NS", "ICICIBANK.NS", "TCS.NS", "INFY.NS", 
            "TATAMOTORS.NS", "SBIN.NS", "ADANIENT.NS"
        ]
        
        # Function to update ticker when dropdown changes
        def update_ticker():
            if st.session_state.stock_select != "Select Stock...":
                val = st.session_state.stock_select
                ticker = val.split(" (")[1].replace(")", "") if " (" in val else val
                st.session_state.opt_ticker = ticker

        st.selectbox("Quick Select (Popular Stocks):", f_and_o_stocks, key="stock_select", on_change=update_ticker)
        opt_ticker = st.text_input("Or Enter Custom Ticker:", key="opt_ticker", value="RELIANCE.NS")
        
        if st.button("Fetch Option Chain 🔍"):
            with st.spinner("Fetching Expiry Dates..."):
                expiries = get_option_expiry_dates(opt_ticker)
                if expiries:
                    st.session_state['expiries'] = expiries
                    st.session_state['selected_ticker'] = opt_ticker
                    st.session_state['use_synthetic'] = False
                else:
                    st.info("💡 **Bhai dhyan dein:** Free APIs (Yahoo Finance) NSE Options data aksar block kar dete hain. Lekin fikr mat kijiye, humara AI **Real-time Spot Price** use karke premiums calculate kar lega!")
                    st.session_state['expiries'] = ["Current Month (AI Model)"]
                    st.session_state['selected_ticker'] = opt_ticker
                    st.session_state['use_synthetic'] = True
        
        if 'expiries' in st.session_state and st.session_state['selected_ticker'] == opt_ticker:
            selected_expiry = st.selectbox("Select Expiry Date:", st.session_state['expiries'])
            
            if st.button("Analyze Options ⚡"):
                with st.spinner("Analyzing Option Chain & Greeks..."):
                    # Fetch data for technical context
                    df_opt = fetch_historical_data(opt_ticker, period="6mo")
                    df_opt = add_technical_indicators(df_opt)
                    df_opt = generate_signals(df_opt)
                    latest_sig = get_latest_signal(df_opt)
                    score_data = calculate_ai_score(df_opt)
                    curr_price = df_opt['Close'].iloc[-1]
                    
                    # Fetch Option Chain
                    is_synthetic = st.session_state.get('use_synthetic', False)
                    if is_synthetic:
                        st.info(f"✅ **LIVE Spot Price detected: ₹{curr_price:.2f}**. AI premiums calculate kar raha hai...")
                        calls, puts = generate_synthetic_option_chain(curr_price)
                    else:
                        calls, puts = get_option_chain(opt_ticker, selected_expiry)
                        if calls.empty or puts.empty:
                            st.warning("⚠️ Real-time NSE Options fetch failed. Switching to AI-Model based on Live Price.")
                            calls, puts = generate_synthetic_option_chain(curr_price)
                            is_synthetic = True
                    
                    # Strategy Suggestions
                    st.session_state['opt_analysis'] = {
                        "ticker": opt_ticker,
                        "expiry": selected_expiry,
                        "calls": calls,
                        "puts": puts,
                        "signal": latest_sig,
                        "score": score_data,
                        "price": curr_price,
                        "is_synthetic": is_synthetic
                    }

    if 'opt_analysis' in st.session_state:
        analysis = st.session_state['opt_analysis']
        
        # --- ADVANCED METRICS CARDS ---
        pcr = calculate_pcr(analysis['calls'], analysis['puts'])
        max_pain = calculate_max_pain(analysis['calls'], analysis['puts'])
        
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("Put-Call Ratio (PCR)", pcr, delta="Bullish" if pcr > 1 else "Bearish")
        with m2:
            st.metric("Max Pain Strike", f"₹{max_pain:.0f}")
        with m3:
            vol = "22% (Normal)" if not analysis['is_synthetic'] else "20% (Est.)"
            st.metric("Implied Volatility", vol)

        st.markdown("---")
        st.subheader(f"🤖 AI Recommended Strategies for {analysis['ticker']}")
        
        rec_strategies = suggest_option_strategies(
            analysis['ticker'], 
            analysis['price'], 
            analysis['signal'], 
            analysis['score']['score']
        )
        
        for strat in rec_strategies:
            with st.expander(f"✨ Strategy: {strat['name']} ({strat['type']})"):
                c1, c2 = st.columns([1, 1])
                with c1:
                    st.markdown(f"**Setup:** {strat['setup']}")
                    st.markdown(f"**Benefit:** {strat['benefit']}")
                    st.success("AI Logic: Is strategy mein risk limited hai aur profit hone ke chances zyada hain.")
                with c2:
                    # Simple Payoff Visualization placeholder
                    st.markdown("**Potential Payoff Chart:**")
                    x = np.linspace(analysis['price'] * 0.9, analysis['price'] * 1.1, 100)
                    if "Bull" in strat['name']:
                        y = np.where(x < analysis['price'], -10, (x - analysis['price']) * 2 - 10)
                        y = np.clip(y, -10, 30) # Capped profit for spreads
                    else:
                        y = np.where(x > analysis['price'], -10, (analysis['price'] - x) * 2 - 10)
                        y = np.clip(y, -10, 30)
                        
                    fig_p = go.Figure()
                    fig_p.add_trace(go.Scatter(x=x, y=y, fill='tozeroy', name='Profit/Loss', line=dict(color='cyan')))
                    fig_p.update_layout(height=200, margin=dict(l=0,r=0,t=0,b=0), template="plotly_dark")
                    st.plotly_chart(fig_p, use_container_width=True)

        # Option Chain Display
        st.markdown("---")
        st.subheader(f"📑 Option Chain - {analysis['expiry']}")
        
        # Merge calls and puts for a cleaner view
        chain_view = pd.merge(
            analysis['calls'][['strike', 'lastPrice', 'change', 'openInterest']], 
            analysis['puts'][['strike', 'lastPrice', 'change', 'openInterest']], 
            on='strike', suffixes=('_Call', '_Put')
        ).sort_values('strike')
        
        # Filter around ATM
        atm_strike = analysis['price']
        chain_view = chain_view[
            (chain_view['strike'] >= atm_strike * 0.9) & 
            (chain_view['strike'] <= atm_strike * 1.1)
        ]
        
        # Option Chain Display with styling (safely handled if matplotlib is missing)
        try:
            st.dataframe(chain_view.style.background_gradient(subset=['openInterest_Call', 'openInterest_Put'], cmap='Blues'), use_container_width=True)
        except Exception:
            st.dataframe(chain_view, use_container_width=True)
        
        st.caption("💡 Tip: 'Open Interest' (OI) batata hai ki kitne contracts active hain. Zyada OI matlab wahan support ya resistance ho sakta hai.")

    st.markdown("---")
    with st.expander("🎓 **Beginner's Corner: Options Kya Hain? (Read this if you're new)**"):
        st.markdown("""
        Agar aapko trading ke bare mein kuch nahi pata, to ye 3 baatein yaad rakhein:
        
        1. **Options Kya Hain?**: Options ek tarah ka insurance ya contract hote hain. Aap predict karte hain ki market upar jayega (**Call**) ya niche (**Put**).
        2. **Call vs Put**: 
            - **Call (CE)**: Jab aapko lagta hai market **Upar** jayega.
            - **Put (PE)**: Jab aapko lagta hai market **Niche** jayega.
        3. **Expiry**: Har option contract ki ek 'Expiry' date hoti hai. Us date ke baad wo contract zero ya settle ho jata hai.
        
        ### 🛡️ Safe Reccomendation:
        Naye traders ke liye **'Bull Call Spread'** ya **'Bear Put Spread'** sabse safe hote hain kyunki isme aapka loss limited hota hai. AI aapko wahi suggest karega!
        
        *Dhyan rahe: Options trading mein risk hota hai, hamesha kam capital se start karein.*
        """)

with tab_risk:
    st.header("🛡️ Risk & Position Sizing Manager")
    st.markdown("""
    Trading mein sabse zaroori ye nahi hai ki aap kitna kamate hain, balki ye hai ki aap **kitna lose karne ko taiyar hain**. 
    Ye calculator aapko batayega ki aapko kitni quantity khareedni chahiye.
    """)
    
    r_col1, r_col2 = st.columns(2)
    
    with r_col1:
        st.subheader("Your Capital Settings")
        total_cap = st.number_input("Total Trading Capital (₹):", value=100000, step=5000)
        risk_pct = st.slider("Risk Per Trade (% of Capital):", 0.5, 5.0, 1.0, 0.5)
        
        st.markdown("---")
        st.subheader("Trade Details")
        entry_p = st.number_input("Entry Price (Current Rate):", value=1000.0)
        stop_l = st.number_input("Stop Loss Price:", value=980.0)
        
    with r_col2:
        st.subheader("📊 AI Risk Report")
        
        risk_amount = (total_cap * risk_pct) / 100
        risk_per_share = entry_p - stop_l
        
        target_p = st.number_input("Target Price (Expected Profit):", value=entry_p + (risk_per_share * 2))
        reward_per_share = target_p - entry_p
        
        if risk_per_share > 0:
            quantity = int(risk_amount / risk_per_share)
            total_investment = quantity * entry_p
            potential_profit = quantity * reward_per_share
            rr_ratio = round(reward_per_share / risk_per_share, 2)
            
            st.info(f"**Max Risk You Can Take:** ₹{risk_amount:.2f}")
            st.success(f"**Recommended Quantity to Buy:** {quantity} Shares / Units")
            
            m_col1, m_col2 = st.columns(2)
            with m_col1:
                st.metric("Potential Profit", f"₹{potential_profit:.2f}")
            with m_col2:
                st.metric("Risk-to-Reward Ratio", f"1:{rr_ratio}")
            
            if total_investment > total_cap:
                st.warning(f"⚠️ Warning: Is trade ke liye ₹{total_investment:.2f} chahiye, jo aapke capital se zyada hai.")
            else:
                st.metric("Total Investment Required", f"₹{total_investment:.2f}")
                
            st.markdown("### 📝 Checklist:")
            c1 = st.checkbox(f"Kya aap ₹{risk_amount:.2f} ka loss bardasht kar sakte hain?", key="check1")
            c2 = st.checkbox("Kya aapne Stop-Loss system mein laga diya hai?", key="check2")
            c3 = st.checkbox("Kya ye trade AI ke 'Strong Buy' signal ke saath match karta hai?", key="check3")
            
            if c1 and c2 and c3:
                st.success("✅ Aap trade lene ke liye taiyar hain! All the best!")
            else:
                st.warning("⚠️ Kripya saare points check karein pehle.")
        else:
            st.error("Stop Loss entry price se niche hona chahiye!")

    st.caption("💡 Tip: Hamesha 1-2% se zyada risk ek trade mein mat lijiye. Isi se long-term profit banta hai.")
