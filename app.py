import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import random
from pypfopt import expected_returns, risk_models
from pypfopt.efficient_frontier import EfficientFrontier

# --- PAGE CONFIG ---
st.set_page_config(page_title="StockGo | AI Portfolio", layout="wide", initial_sidebar_state="collapsed")

# --- DYNAMIC BACKGROUND GENERATOR ---
# Removed cache to ensure it renders on every page switch
def get_floating_background():
    tickers_pool = [
        "AAPL 150.25", "MSFT 310.10", "TSLA 220.50", "NVDA 450.00", "RELIANCE 2500.00", 
        "GOOGL 135.20", "AMZN 140.50", "META 300.20", "JNJ 160.00", "V 240.10", 
        "TCS 3400.15", "INFY 1450.80", "HDFC 1600.00", "NFLX 400.20", "INTC 35.10"
    ]
    
    html = '<div class="stock-ticker-background">'
    for _ in range(75):
        t = random.choice(tickers_pool)
        
        is_up = random.choice([True, False])
        is_blue = random.choice([True, False])
        arrow = "▲" if is_up else "▼"
        color = "#3b82f6" if is_blue else "#ef4444" 
        pct = round(random.uniform(0.1, 5.5), 1)
        
        colored_arrow = f'<span style="color: {color}; text-shadow: 0 0 5px {color}80;">{arrow} {pct}%</span>'
        
        left = random.randint(-10, 100)
        top = random.randint(-10, 100)
        dur = random.randint(25, 60)
        delay = random.randint(0, 40)
        anim = random.choice(['float-1', 'float-2', 'float-3', 'float-4'])
        size = random.choice(['14px', '18px', '24px', '32px']) 
        target_op = random.choice(['0.1', '0.15', '0.2'])
        
        style = f"left: {left}vw; top: {top}vh; --target-opacity: {target_op}; font-size: {size}; animation: {anim} {dur}s linear infinite -{delay}s, fade {dur}s linear infinite -{delay}s;"
        html += f'<div class="floating-ticker" style="{style}">{t} {colored_arrow}</div>'
        
    html += '</div>'
    return html

# --- CSS INJECTION (DEAD-CENTER, NO-SCROLL) ---
luxury_css = f"""
<style>
/* 1. LOCK THE VIEWPORT */
html, body, [data-testid="stAppViewContainer"] {{
    overflow: hidden !important; 
    height: 100vh !important;
    width: 100vw !important;
    margin: 0; padding: 0;
    background-color: #050505 !important;
}}

/* Hide Streamlit default padding and menus */
#MainMenu {{visibility: hidden;}}
footer {{visibility: hidden;}}
header {{visibility: hidden;}}
.css-18e3th9 {{padding: 0 !important;}} 

/* 2. DEAD-CENTER THE FROSTED GLASS CONTAINER */
div[data-testid="stAppViewBlockContainer"] {{
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 100%;
    max-width: 950px !important;
    padding: 2.5rem 3rem !important; 
    background: rgba(15, 15, 15, 0.85);
    backdrop-filter: blur(15px);
    -webkit-backdrop-filter: blur(15px);
    border-radius: 20px;
    border: 1px solid rgba(212, 175, 55, 0.3);
    box-shadow: 0 15px 50px rgba(0, 0, 0, 0.8);
    max-height: 95vh; 
    overflow: hidden !important;
    z-index: 10; /* Pulls the glass panel to the very front */
}}

/* Particle Background Setup */
.stock-ticker-background {{
    position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
    z-index: 0; /* Put it right behind the glass panel, not behind Streamlit's canvas */
    pointer-events: none; /* Prevents the invisible background from blocking clicks */
    background-color: #050505; overflow: hidden;
}}
.floating-ticker {{
    position: absolute; font-family: 'Courier New', Courier, monospace;
    font-weight: bold; color: #d4af37; white-space: nowrap; opacity: 0; 
}}

/* Random Drift Animations */
@keyframes float-1 {{ 0% {{ transform: translate(0, 0) scale(1); }} 100% {{ transform: translate(15vw, -15vh) scale(1.1); }} }}
@keyframes float-2 {{ 0% {{ transform: translate(0, 0) scale(1); }} 100% {{ transform: translate(-15vw, -20vh) scale(1.1); }} }}
@keyframes float-3 {{ 0% {{ transform: translate(0, 0) scale(1); }} 100% {{ transform: translate(20vw, 15vh) scale(0.9); }} }}
@keyframes float-4 {{ 0% {{ transform: translate(0, 0) scale(1); }} 100% {{ transform: translate(-20vw, 15vh) scale(0.9); }} }}
@keyframes fade {{ 0% {{ opacity: 0; }} 15% {{ opacity: var(--target-opacity); }} 85% {{ opacity: var(--target-opacity); }} 100% {{ opacity: 0; }} }}

/* Premium Buttons */
.stButton>button {{
    border-radius: 12px; background: linear-gradient(135deg, #d4af37 0%, #aa8529 100%);
    color: #000000 !important; font-weight: 700; font-size: 16px; border: none;
    padding: 10px 30px; box-shadow: 0 4px 15px rgba(212, 175, 55, 0.3);
    transition: all 0.3s ease; width: 100%; margin-top: 5px;
}}
.stButton>button:hover {{
    transform: translateY(-2px); box-shadow: 0 6px 20px rgba(212, 175, 55, 0.5);
    background: linear-gradient(135deg, #f3cd57 0%, #c59b2f 100%);
}}
.stButton>button:active {{ transform: translateY(0px); }}

/* Table Styling */
.stDataFrame {{ border-radius: 10px; overflow: hidden; }}

/* --- LUXURY TYPOGRAPHY --- */
.gradient-text {{
    background: linear-gradient(135deg, #d4af37 0%, #fefaa0 50%, #d4af37 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    font-size: 2.6rem !important; font-weight: 800;
    margin-bottom: -10px; padding-bottom: 10px;
}}
.engine-text {{
    font-size: 1.2rem; color: #ffffff; font-weight: 600;
    letter-spacing: 1px; margin-bottom: 10px;
}}
.motivational-subtext {{
    font-size: 1.05rem; color: #b3b3b3; font-weight: 300;
    letter-spacing: 0.5px; line-height: 1.4;
    border-left: 3px solid #d4af37; padding-left: 15px; margin-bottom: 15px; 
}}
</style>
"""
st.markdown(luxury_css + get_floating_background(), unsafe_allow_html=True)

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
    st.markdown('''
        <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 5px;">
            <svg width="45" height="45" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <defs>
                    <linearGradient id="gold-grad" x1="0%" y1="100%" x2="100%" y2="0%">
                        <stop offset="0%" stop-color="#aa8529" />
                        <stop offset="50%" stop-color="#fefaa0" />
                        <stop offset="100%" stop-color="#d4af37" />
                    </linearGradient>
                </defs>
                <path d="M3 21L10 13L14.5 17L22 6" stroke="url(#gold-grad)" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M15 6H22V13" stroke="url(#gold-grad)" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
                <circle cx="10" cy="13" r="1.5" fill="url(#gold-grad)"/>
                <circle cx="14.5" cy="17" r="1.5" fill="url(#gold-grad)"/>
            </svg>
            <p class="gradient-text" style="margin-bottom: 0; padding-bottom: 0;">StockGo</p>
        </div>
    ''', unsafe_allow_html=True)
    st.markdown('<p class="engine-text">AI Wealth Allocation Engine</p>', unsafe_allow_html=True)
    
    st.markdown('''
        <p class="motivational-subtext">
        Step into the future of wealth building. Tell us your financial vision, 
        and let our intelligent engine craft a resilient, growth-focused portfolio 
        designed entirely around your timeline.
        </p>
    ''', unsafe_allow_html=True)
    
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

    if st.button("INITIALIZE OPTIMIZATION"):
        if len(tickers) < 2:
            st.warning("Analysis requires a minimum of 2 assets.")
        else:
            with st.spinner("Compiling live market data and calculating Efficient Frontier..."):
                try:
                    history_needed = f"{time_horizon + 1}y"
                    data = yf.download(tickers, period=history_needed)['Close']
                    
                    mu = expected_returns.ema_historical_return(data, span=int(252 * time_horizon))
                    S = risk_models.sample_cov(data)
                    
                    ef = EfficientFrontier(mu, S)
                    raw_weights = ef.max_sharpe()
                    cleaned_weights = ef.clean_weights()
                    
                    portfolio = []
                    for ticker, weight in cleaned_weights.items():
                        if weight > 0:
                            amount = weight * total_investment
                            portfolio.append({
                                "Asset": ticker,
                                "Weight": weight, 
                                "Allocation": f"{round(weight * 100, 2)}%",
                                "Capital ($)": round(amount, 2)
                            })
                    
                    df = pd.DataFrame(portfolio)
                    st.session_state.df = df.sort_values(by="Capital ($)", ascending=False)
                    st.session_state.page = "results"
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Market data unavailable for selected assets. Error: {e}")

# ==========================================
# PAGE 2: RESULTS SCREEN
# ==========================================
elif st.session_state.page == "results":
    st.markdown('''
        <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 5px;">
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <defs>
                    <linearGradient id="gold-grad-2" x1="0%" y1="100%" x2="100%" y2="0%">
                        <stop offset="0%" stop-color="#aa8529" />
                        <stop offset="50%" stop-color="#fefaa0" />
                        <stop offset="100%" stop-color="#d4af37" />
                    </linearGradient>
                </defs>
                <path d="M3 21L10 13L14.5 17L22 6" stroke="url(#gold-grad-2)" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M15 6H22V13" stroke="url(#gold-grad-2)" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <p class="gradient-text" style="margin-bottom: 0; padding-bottom: 0; font-size: 2.2rem !important;">Optimization Complete</p>
        </div>
    ''', unsafe_allow_html=True)
    
    st.markdown('''
        <p class="motivational-subtext" style="margin-bottom: 10px;">
        <b>Your Wealth Blueprint is ready.</b> We have optimized every dollar to maximize 
        returns while mathematically guarding against market volatility.
        </p>
    ''', unsafe_allow_html=True)
    
    df = st.session_state.df
    
    fig = px.pie(
        df, values='Capital ($)', names='Asset', hole=0.6,
        color_discrete_sequence=px.colors.sequential.YlOrBr 
    )
    fig.update_traces(
        textposition='outside', textinfo='percent+label',
        marker=dict(line=dict(color='#000000', width=2))
    )
    fig.update_layout(
        height=280, 
        showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#f8f9fa', size=12), margin=dict(t=0, b=0, l=0, r=0),
        annotations=[dict(text='StockGo', x=0.5, y=0.5, font_size=18, showarrow=False, font_color="#d4af37")]
    )
    
    col1, col2 = st.columns([1, 1.2])
    with col1:
        display_df = df.drop(columns=['Weight'])
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    with col2:
        st.plotly_chart(fig, use_container_width=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("← CONFIGURE NEW PORTFOLIO"):
            st.session_state.page = "input"
            st.rerun()
