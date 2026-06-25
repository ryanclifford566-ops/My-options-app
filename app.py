import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="Fast Alpha Options",
    page_icon="⚡",
    layout="wide"
)

# Mobile UI Framework Layout
st.markdown("""
<style>
    .block-container {
        padding-top: 0.8rem !important;
        padding-bottom: 0.8rem !important;
        padding-left: 0.4rem !important;
        padding-right: 0.4rem !important;
    }
    .stButton>button {
        width: 100% !important;
        height: 55px !important;
        font-size: 18px !important;
        font-weight: bold !important;
        background-color: #00FF66 !important;
        color: black !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("⚡ Fast-Track $0.01 Options Scanner")
st.write("Filters for a bare-minimum $5+ profit potential sorted by the fastest expected move speed.")

TICKERS = ["AAPL", "MSFT", "NVDA", "AMD", "TSLA", "META", "AMZN", "NFLX", "COIN", "PLTR", "SOFI", "UBER"]

if st.button("🚀 Scan for Immediate Momentum"):
    with st.spinner("Analyzing shortest-timeframe volatility spikes..."):
        
        tier_1_5 = []      # $1 - $5 strikes
        tier_10_25 = []    # $10 - $25 strikes
        tier_26_100 = []   # $26 - $100 strikes
        
        today = datetime.now()
        
        for ticker in TICKERS:
            try:
                stock = yf.Ticker(ticker)
                expirations = stock.options
                
                if not expirations:
                    continue
                
                # Look at the closest 3 expiration dates for the shortest possible timeframe
                short_expirations = expirations[:3]
                
                stock_history = stock.history(period="1d")
                current_stock_price = stock_history['Close'].iloc[-1]
                
                for exp in short_expirations:
                    exp_date = datetime.strptime(exp, "%Y-%m-%d")
                    days_to_expiry = (exp_date - today).days
                    if days_to_expiry <= 0:
                        days_to_expiry = 1
                        
                    opt_chain = stock.option_chain(exp)
                    calls = opt_chain.calls
                    
                    if calls.empty:
                        continue
                    
                    cheap_calls = calls[(calls['ask'] == 0.01) & (calls['openInterest'] > 2)]
                    
                    for _, row in cheap_calls.iterrows():
                        strike = row['strike']
                        iv = row['impliedVolatility'] * 100
                        
                        min_exit_value = 0.06 
                        potential_profit = (min_exit_value - 0.01) * 100
                        
                        contract_info = {
                            "Ticker (Copy)": ticker,
                            "Stock Price": f"${current_stock_price:.2f}",
                            "Strike": strike,
                            "Days Left": days_to_expiry,
                            "Implied Volatility": iv,
                            "Min Potential Profit": f"${potential_profit:.2f}+",
                            "Contract Cost": "$1.00",
                            "Open Interest": int(row['openInterest'])
                        }
                        
                        if 1.00 <= strike <= 5.00:
                            tier_1_5.append(contract_info)
                        elif 10.00 <= strike <= 25.00:
                            tier_10_25.append(contract_info)
                        elif 25.01 <= strike <= 100.00:
                            tier_26_100.append(contract_info)
            except Exception:
                continue

        # DISPLAY OUTPUTS - AUTO-SORTED BY HIGHEST IV
        st.markdown("### 🪵 Tier 1: Micro Price Levels ($1 - $5)")
        if tier_1_5:
            df1 = pd.DataFrame(tier_1_5).sort_values(by="Implied Volatility", ascending=False)
            df1["Strike"] = df1["Strike"].map("${:,.2f}".format)
            df1["Implied Volatility"] = df1["Implied Volatility"].map("{:.0f}%".format)
            st.dataframe(df1, use_container_width=True, hide_index=True)
        else:
            st.info("No hyper-volatility $1-$5 strike setups available right now.")
            
        st.markdown("### 🚀 Tier 2: Mid-Level Milestones ($10 - $25)")
        if tier_10_25:
            df2 = pd.DataFrame(tier_10_25).sort_values(by="Implied Volatility", ascending=False)
            df2["Strike"] = df2["Strike"].map("${:,.2f}".format)
            df2["Implied Volatility"] = df2["Implied Volatility"].map("{:.0f}%".format)
            st.dataframe(df2, use_container_width=True, hide_index=True)
        else:
            st.info("No hyper-volatility $10-$25 strike setups available right now.")
            
        st.markdown("### 🏆 Tier 3: Macro Targets ($25 - $100)")
        if tier_26_100:
            df3 = pd.DataFrame(tier_26_100).sort_values(by="Implied Volatility", ascending=False)
            df3["Strike"] = df3["Strike"].map("${:,.2f}".format)
            df3["Implied Volatility"] = df3["Implied Volatility"].map("{:.0f}%".format)
            st.dataframe(df3, use_container_width=True, hide_index=True)
        else:
            st.info("No hyper-volatility $25-$100 strike setups available right now.")

        st.caption("📋 **Mobile Workflow:** Sort columns instantly by clicking the column headers on your screen.")
