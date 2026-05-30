import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="AI Portfolio Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding-top: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# ===== SIDEBAR =====
st.sidebar.title("🎯 Portfolio Configuration")

portfolio_type = st.sidebar.selectbox(
    "Select Portfolio Type",
    ["Sample Portfolio", "Custom Portfolio"]
)

# Sample portfolio data
SAMPLE_PORTFOLIO = {
    "AAPL": 10,
    "MSFT": 8,
    "GOOGL": 5,
    "TSLA": 3,
    "BRK.B": 6
}

if portfolio_type == "Sample Portfolio":
    portfolio = SAMPLE_PORTFOLIO
    st.sidebar.info("📈 Using sample portfolio with major tech stocks")
else:
    st.sidebar.write("Enter your portfolio (format: TICKER:QUANTITY)")
    portfolio_input = st.sidebar.text_area(
        "Portfolio",
        value="AAPL:10\nMSFT:8\nGOOGL:5",
        height=150
    )
    portfolio = {}
    try:
        for line in portfolio_input.strip().split('\n'):
            if line:
                ticker, qty = line.split(':')
                portfolio[ticker.strip()] = int(qty)
    except:
        st.sidebar.error("❌ Invalid format. Use TICKER:QUANTITY")
        portfolio = SAMPLE_PORTFOLIO

# Date range
st.sidebar.subheader("📅 Time Range")
days_back = st.sidebar.slider("Days of history", 30, 365, 90)
end_date = datetime.now()
start_date = end_date - timedelta(days=days_back)

# ===== MAIN CONTENT =====
st.title("📊 AI Portfolio Dashboard")
st.markdown("Real-time portfolio analysis and performance tracking")

# Fetch data
@st.cache_data(ttl=3600)
def fetch_data(tickers, start, end):
    data = {}
    for ticker in tickers:
        try:
            df = yf.download(ticker, start=start, end=end, progress=False)
            if not df.empty:
                data[ticker] = df
        except:
            pass
    return data

with st.spinner("📡 Fetching market data..."):
    market_data = fetch_data(list(portfolio.keys()), start_date, end_date)

if not market_data:
    st.error("❌ Could not fetch data. Please check your internet connection.")
    st.stop()

# ===== KEY METRICS =====
st.subheader("📈 Portfolio Metrics")

col1, col2, col3, col4 = st.columns(4)

# Calculate total value
latest_prices = {}
for ticker in portfolio.keys():
    if ticker in market_data:
        latest_prices[ticker] = market_data[ticker]['Close'].iloc[-1]

total_value = sum(latest_prices.get(t, 0) * q for t, q in portfolio.items())
portfolio_value_start = sum(
    market_data[t]['Close'].iloc[0] * portfolio[t] 
    for t in portfolio.keys() if t in market_data
)

gain_loss = total_value - portfolio_value_start
gain_loss_pct = (gain_loss / portfolio_value_start * 100) if portfolio_value_start > 0 else 0

col1.metric("💰 Portfolio Value", f"${total_value:,.2f}")
col2.metric("📊 Total Gain/Loss", f"${gain_loss:,.2f}", f"{gain_loss_pct:.2f}%")
col3.metric("🎯 Holdings", len(portfolio))
col4.metric("⏰ Period", f"{days_back} days")

# ===== PORTFOLIO COMPOSITION =====
st.subheader("🥧 Portfolio Composition")

holdings_value = {}
for ticker, qty in portfolio.items():
    if ticker in latest_prices:
        holdings_value[ticker] = latest_prices[ticker] * qty

fig_pie = go.Figure(data=[go.Pie(
    labels=list(holdings_value.keys()),
    values=list(holdings_value.values()),
    hole=0.3
)])
fig_pie.update_layout(
    title="Portfolio Distribution by Value",
    height=400,
    showlegend=True
)
st.plotly_chart(fig_pie, use_container_width=True)

# ===== PRICE CHARTS =====
st.subheader("📉 Individual Stock Performance")

tabs = st.tabs([f"{t}" for t in portfolio.keys()])

for idx, ticker in enumerate(portfolio.keys()):
    with tabs[idx]:
        if ticker in market_data:
            df = market_data[ticker]
            
            col1, col2, col3 = st.columns(3)
            current_price = df['Close'].iloc[-1]
            start_price = df['Close'].iloc[0]
            ticker_gain = ((current_price - start_price) / start_price * 100)
            
            col1.metric(f"{ticker} Price", f"${current_price:.2f}")
            col2.metric(f"Change", f"{ticker_gain:.2f}%")
            col3.metric(f"Quantity", portfolio[ticker])
            
            # Price chart
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['Close'],
                mode='lines',
                name='Close Price',
                line=dict(color='#1f77b4', width=2)
            ))
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['SMA_20'] if 'SMA_20' in df.columns else df['Close'].rolling(20).mean(),
                mode='lines',
                name='20-Day MA',
                line=dict(color='orange', dash='dash')
            ))
            fig.update_layout(
                title=f"{ticker} Price History",
                xaxis_title="Date",
                yaxis_title="Price ($)",
                height=400,
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)

# ===== PORTFOLIO HOLDINGS TABLE =====
st.subheader("📋 Holdings Summary")

holdings_df = pd.DataFrame([
    {
        "Ticker": ticker,
        "Quantity": portfolio[ticker],
        "Current Price": f"${latest_prices.get(ticker, 0):.2f}",
        "Value": f"${holdings_value.get(ticker, 0):.2f}",
        "% of Portfolio": f"{(holdings_value.get(ticker, 0) / total_value * 100):.1f}%"
    }
    for ticker in portfolio.keys()
])

st.dataframe(holdings_df, use_container_width=True)

# ===== FOOTER =====
st.divider()
st.markdown("""
<div style='text-align: center; color: gray; font-size: 12px;'>
    Last updated: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC") + """<br>
    📊 AI Portfolio Dashboard | Data from Yahoo Finance
</div>
""", unsafe_allow_html=True)
