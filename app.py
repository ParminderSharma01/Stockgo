import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from pypfopt import expected_returns, risk_models
from pypfopt.efficient_frontier import EfficientFrontier

# --- PAGE CONFIG ---
st.set_page_config(page_title="StockGo | AI Portfolio", layout="wide", initial_sidebar_state="collapsed")

# --- CSS INJECTION (LUXURY UI & ANIMATION) ---
luxury_css = """
<style>
/* Hide Streamlit elements */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* The Animated Background Ticker */
.stock-ticker-background {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    z-index: -999;
    background-color: #050505;
    overflow: hidden;
    opacity: 0.15; 
    font-family: 'Courier New', Courier, monospace;
    font-weight: bold;
    color: #d4af37; 
    font-size: 28px;
    display: flex;
    flex-direction: column;
    justify-content: space-around;
}
.ticker-row { white-space: nowrap; animation: scroll-left linear infinite; }
.ticker-fast { animation-duration: 25s; }
.ticker-slow { animation-duration: 40s; animation-direction: reverse; }
@keyframes scroll-left { 0% { transform: translateX(100%); } 100% { transform: translateX(-100%); } }

/* Frosted Glass Container */
.block-container {
    background: rgba(15, 15, 15, 0.85);
    backdrop-filter: blur(15px);
    -webkit-backdrop-filter: blur(15px);
    border-radius: 20px;
    padding: 3rem;
    border: 1px solid rgba(212, 175, 55, 0.3);
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.6);
    max-width: 900px;
}

/* Premium Buttons */
.stButton>button {
    border-radius: 12px;
    background: linear-gradient(135deg, #d4af37 0%, #aa8529 100%);
    color: #000000 !important;
    font-weight: 700;
    font-size: 16px;
    border: none;
    padding: 12px 30px;
    box-shadow: 0 4px 15px rgba(212, 175, 55, 0.3);
    transition: all 0.3s ease;
    width: 100%;
}
.stButton>button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(212, 175, 55, 0.5);
    background: linear-gradient(135deg, #f3cd57 0%, #c59b2f 100%);
}
.stButton>button:active { transform: translateY(0px); }

/* Table Styling */
.stDataFrame { border-radius: 10px; overflow: hidden; }
</style>

<div class="stock-ticker-background">
   <div class="ticker-row ticker-fast">AAPL 150.25 ▲ 1.2% &nbsp;&nbsp; MSFT 310.10 ▼ 0.5% &nbsp;&nbsp; TSLA 220.50 ▲ 2.1% &nbsp;&nbsp; NVDA 450.00 ▲ 3.5% &nbsp;&nbsp; RELIANCE 2500.00 ▲ 1.0%</div>
   <div class="ticker-row ticker-slow">GOOGL 135.20 ▲ 0.8% &nbsp;&nbsp; AMZN 140.50 ▼ 1.1% &nbsp;&nbsp; META 300.20 ▲ 1.5% &nbsp;&nbsp; JNJ 160.00 ▼ 0.2% &nbsp;&nbsp; V 240.10 ▲ 0.9%</div>
   <div class="ticker-row ticker-fast" style="animation-duration: 20s;">TCS 3400.15 ▲ 0.5% &nbsp;&nbsp; INFY 1450.80 ▲ 1.2% &nbsp;&nbsp; HDFC 1600.00 ▼ 0.4% &nbsp;&nbsp; NFLX 400.20 ▲ 2.2% &nbsp;&nbsp; INTC 35.10 ▼ 1.5%</div>
</div>
"""
st.markdown(luxury_css, unsafe_allow_html=True)

# --- STATE MANAGEMENT ---
if 'page' not in st.session_state:
    st.session_state.page = "input"
if 'results' not in st.session_state:
    st.session_state.results = None
if 'df' not in st.session_state:
    st.session_state.df = None

AVAILABLE_STOCKS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "NVDA", "JNJ", "V", "WMT", 
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "SBIN.NS", "BHARTIARTL.NS"
]

# ==========================================
# PAGE 1: INPUT SCREEN
# ==========================================
if st.session_state.page == "input":
    st.title("📈 StockGo")
    st.markdown("### AI Wealth Allocation Engine")
    st.write("Configure your investment parameters. Our optimization matrix will determine the most mathematically sound portfolio.")
    
    st.write("---")
    
    col1, col2 = st.columns(2)
    with col1:
        total_investment = st.number_input("Capital Commitment ($):", min_value=100.0, value=10000.0, step=1000.0)
    with col2:
        time_horizon = st.slider("Investment Horizon (Years):", min_value=1, max_value=10, value=3)

    tickers = st.multiselect(
        "Select Assets for Analysis:", 
        options=AVAILABLE_STOCKS, 
        default=["AAPL", "MSFT", "NVDA", "RELIANCE.NS", "TCS.NS"]
    )

    st.write("") # Spacer
    if st.button("INITIALIZE OPTIMIZATION"):
        if len(tickers) < 2:
            st.warning("Analysis requires a minimum of 2 assets.")
        else:
            with st.spinner("Compiling live market data and calculating Efficient Frontier..."):
                try:
                    # AI Math
                    history_needed = f"{time_horizon + 1}y"
                    data = yf.download(tickers, period=history_needed)['Close']
                    
                    mu = expected_returns.ema_historical_return(data, span=int(252 * time_horizon))
                    S = risk_models.sample_cov(data)
                    
                    ef = EfficientFrontier(mu, S)
                    raw_weights = ef.max_sharpe()
                    cleaned_weights = ef.clean_weights()
                    
                    # Formatting Data
                    portfolio = []
                    for ticker, weight in cleaned_weights.items():
                        if weight > 0:
                            amount = weight * total_investment
                            portfolio.append({
                                "Asset": ticker,
                                "Weight": weight, # Raw decimal for Plotly
                                "Allocation": f"{round(weight * 100, 2)}%",
                                "Capital ($)": round(amount, 2)
                            })
                    
                    # Save to state and switch page
                    df = pd.DataFrame(portfolio)
                    st.session_state.df = df.sort_values(by="Capital ($)", ascending=False)
                    st.session_state.page = "results"
                    st.rerun()
                    
                except Exception as e:
                    st.error("Market data unavailable for selected assets. Please try again.")

# ==========================================
# PAGE 2: RESULTS SCREEN
# ==========================================
elif st.session_state.page == "results":
    st.title("📊 Optimization Complete")
    st.write("Based on Modern Portfolio Theory, here is your mathematically optimized capital distribution.")
    st.write("---")
    
    df = st.session_state.df
    
    # Authentic Plotly Donut Chart
    fig = px.pie(
        df, 
        values='Capital ($)', 
        names='Asset', 
        hole=0.6,
        color_discrete_sequence=px.colors.sequential.YlOrBr # Luxury Gold/Brown palette
    )
    fig.update_traces(
        textposition='outside', 
        textinfo='percent+label',
        marker=dict(line=dict(color='#000000', width=2))
    )
    fig.update_layout(
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#f8f9fa', size=14),
        margin=dict(t=10, b=10, l=10, r=10),
        annotations=[dict(text='StockGo', x=0.5, y=0.5, font_size=20, showarrow=False, font_color="#d4af37")]
    )
    
    col1, col2 = st.columns([1, 1.2])
    with col1:
        st.write("#### Capital Distribution")
        # Format the display table without the raw 'Weight' column
        display_df = df.drop(columns=['Weight'])
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    with col2:
        st.plotly_chart(fig, use_container_width=True)

    st.write("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("← CONFIGURE NEW PORTFOLIO"):
            st.session_state.page = "input"
            st.rerun()
