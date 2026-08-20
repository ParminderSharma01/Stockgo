import streamlit as st
import yfinance as yf
import pandas as pd
from pypfopt import expected_returns, risk_models
from pypfopt.efficient_frontier import EfficientFrontier

st.set_page_config(page_title="AI Stock Allocator", layout="centered")
st.title("🤖 AI Time-Horizon Allocator")
st.write("Enter your budget and timeline. The AI will pull live data from Yahoo Finance and calculate the optimal dollar split.")

# --- USER INPUTS ---
st.subheader("1. Your Investment Details")
total_investment = st.number_input("Total Amount to Invest ($):", min_value=100.0, value=5000.0)
time_horizon = st.slider("Time Horizon (Years):", min_value=1, max_value=10, value=3)
tickers_input = st.text_input("Stocks to consider (comma-separated):", "AAPL, MSFT, JNJ, PG, GOOGL")

if st.button("Run AI Allocation"):
    tickers = [t.strip().upper() for t in tickers_input.split(",")]
    
    if len(tickers) < 2:
        st.warning("Please enter at least 2 stocks!")
    else:
        with st.spinner("Fetching live data from yfinance..."):
            try:
                # --- FETCH DATA WITH YFINANCE ---
                # We pull history based on how long they want to invest
                data = yf.download(tickers, period="5y")['Close']
                
                # --- AI MATH (Portfolio Optimization) ---
                # Calculate expected returns scaled to their time horizon
                mu = expected_returns.ema_historical_return(data, span=int(252 * time_horizon))
                S = risk_models.sample_cov(data)
                
                # Optimize for the best return vs risk
                ef = EfficientFrontier(mu, S)
                raw_weights = ef.max_sharpe()
                cleaned_weights = ef.clean_weights()
                
                # --- CALCULATE DOLLAR AMOUNTS ---
                portfolio = []
                for ticker, weight in cleaned_weights.items():
                    # Only show stocks that the AI decided to put money into
                    if weight > 0:
                        amount = weight * total_investment
                        portfolio.append({
                            "Stock": ticker,
                            "Allocation": f"{round(weight * 100, 2)}%",
                            "Amount ($)": round(amount, 2)
                        })
                
                # --- DISPLAY RESULTS ---
                st.success("Allocation Calculated Successfully!")
                df = pd.DataFrame(portfolio)
                
                st.subheader("Your Recommended Portfolio")
                st.dataframe(df, hide_index=True)
                
                st.write("### Portfolio Breakdown")
                st.pie_chart(df.set_index("Stock")["Amount ($)"])
                
            except Exception as e:
                st.error(f"An error occurred: {e}")
