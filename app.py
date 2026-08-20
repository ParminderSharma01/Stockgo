import streamlit as st
import yfinance as yf
import pandas as pd
from pypfopt import expected_returns, risk_models
from pypfopt.efficient_frontier import EfficientFrontier

st.set_page_config(page_title="AI Stock Allocator", layout="centered")
# --- LUXURY UI STYLING ---
luxury_css = """
<style>
/* Hide Streamlit default headers and footers */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Premium Button Styling */
.stButton>button {
    border-radius: 20px;
    background: linear-gradient(135deg, #d4af37 0%, #aa8529 100%);
    color: #000000 !important;
    font-weight: 600;
    border: none;
    padding: 10px 24px;
    box-shadow: 0 4px 15px rgba(212, 175, 55, 0.3);
    transition: all 0.3s ease;
}
.stButton>button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(212, 175, 55, 0.5);
    background: linear-gradient(135deg, #f3cd57 0%, #c59b2f 100%);
}

/* Sleek input boxes */
div[data-baseweb="input"] > div, div[data-baseweb="select"] > div {
    background-color: #1a1a1a;
    border: 1px solid #333333;
    border-radius: 10px;
}
</style>
"""
st.markdown(luxury_css, unsafe_allow_html=True)
# -------------------------
st.title("🤖 AI Time-Horizon Allocator")
st.write("Enter your budget and timeline. The AI will pull live data and calculate the optimal dollar split.")

# --- THE MASTER STOCK LIST ---
# We provide a robust mix of US and Indian market leaders for high reliability
AVAILABLE_STOCKS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "NVDA", "JNJ", "V", "WMT", # US Giants
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "SBIN.NS", "BHARTIARTL.NS", # NSE Leaders
    "KO", "PEP", "MCD", "DIS", "NFLX", "NKE", "SBUX", "INTC", "AMD", "BA" # Global Brands
]

# --- USER INPUTS ---
st.subheader("1. Your Investment Details")
total_investment = st.number_input("Total Amount to Invest:", min_value=100.0, value=5000.0)
time_horizon = st.slider("Time Horizon (Years):", min_value=1, max_value=10, value=3)

# Upgraded UI: Multi-select dropdown instead of typing text
tickers = st.multiselect(
    "Select stocks for the AI to analyze:", 
    options=AVAILABLE_STOCKS, 
    default=["AAPL", "MSFT", "GOOGL", "RELIANCE.NS", "TCS.NS"]
)

if st.button("Run AI Allocation"):
    if len(tickers) < 2:
        st.warning("Please select at least 2 stocks for the AI to compare!")
    else:
        with st.spinner("Fetching live data and running optimization..."):
            try:
                # Pull history based on time horizon (add 1 buffer year for accuracy)
                history_needed = f"{time_horizon + 1}y"
                data = yf.download(tickers, period=history_needed)['Close']
                
                # --- AI MATH ---
                mu = expected_returns.ema_historical_return(data, span=int(252 * time_horizon))
                S = risk_models.sample_cov(data)
                
                ef = EfficientFrontier(mu, S)
                raw_weights = ef.max_sharpe()
                cleaned_weights = ef.clean_weights()
                
                # --- DOLLAR AMOUNTS ---
                portfolio = []
                for ticker, weight in cleaned_weights.items():
                    if weight > 0:
                        amount = weight * total_investment
                        portfolio.append({
                            "Stock": ticker,
                            "Allocation": f"{round(weight * 100, 2)}%",
                            "Amount": round(amount, 2)
                        })
                
                # --- DISPLAY ---
                st.success("Allocation Calculated Successfully!")
                df = pd.DataFrame(portfolio)
                
                st.subheader("Your Recommended Portfolio")
                st.dataframe(df, hide_index=True)
                
                st.write("### Portfolio Breakdown")
                st.bar_chart(df.set_index("Stock")["Amount"])
                
            except Exception as e:
                st.error(f"An error occurred: {e}")
