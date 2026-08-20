import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# 1. Setup the website look
st.set_page_config(page_title="AI Stock Allocator", layout="centered")
st.title("📈 AI Portfolio Allocator")
st.write("Tell us how much you want to invest, and the AI will calculate the best way to split it based on the past year of data.")

# 2. Get inputs from the user
investment = st.number_input("Total Money to Invest ($):", min_value=10.0, value=1000.0)
tickers_input = st.text_input("Enter Stocks (comma-separated, e.g., AAPL, MSFT, GOOGL):", "AAPL, MSFT, GOOGL")

# 3. The magic happens when they click the button
if st.button("Run AI Allocation"):
    tickers = [t.strip().upper() for t in tickers_input.split(",")]
    
    if len(tickers) < 2:
        st.warning("Please enter at least 2 stocks!")
    else:
        with st.spinner("Downloading free data from Yahoo Finance..."):
            # Get Data
            data = yf.download(tickers, period="1y")['Close']
            
            # Math/AI: Calculate Growth vs Risk
            daily_returns = data.pct_change().dropna()
            annual_return = daily_returns.mean() * 252
            annual_risk = daily_returns.std() * np.sqrt(252)
            
            # Score = Growth divided by Risk
            score = annual_return / annual_risk
            score = score[score > 0] # Remove losing stocks
            
            if score.empty:
                st.error("These stocks had a negative trend this year. Try others!")
            else:
                # Calculate percentages
                weights = score / score.sum()
                
                # Show the results
                st.success("Analysis Complete!")
                
                df = pd.DataFrame({
                    "Stock": weights.index,
                    "Weight (%)": (weights * 100).round(2),
                    "Amount ($)": (weights * investment).round(2)
                })
                
                st.dataframe(df, hide_index=True)
                st.write("### Visual Breakdown")
                st.bar_chart(df.set_index("Stock")["Amount ($)"])
