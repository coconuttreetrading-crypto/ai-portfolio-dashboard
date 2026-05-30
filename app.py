import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="AI Portfolio Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== SIDEBAR =====
st.sidebar.title("🎯 Portfolio Configuration")

portfolio_type = st.sidebar.selectbox(
    "Select Portfolio Type",
    ["Sample Portfolio", "Custom Portfolio"]
)

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
            if line.strip():
                ticker, qty = line.split(':')
                portfolio[ticker.strip()] = int(qty)
    except:
        st.sidebar.error("❌ Invalid format. Use TICKER:QUANTITY")
        portfolio = SAMPLE_PORTFOLIO

st.sidebar.subheader("📅 Time Range")
days_back = st.sidebar.slider("Days of history", 30, 365, 90)
end_date = datetime.now()
start_date = end_date - timedelta(days=days_back)

# ===== MAIN CONTENT =====
st.title("📊 AI Portfolio Dashboard")
st.markdown("Real-time portfolio analysis and performance tracking")

@st.cache_data(ttl=3600)
def fetch_data(tickers, start, end):
    data = {}
    for ticker in tickers:
        try:
            df = yf.download(ticker, start=start, end=end, progress=False, quiet=True)
            if len(df) > 0:
                data[ticker] = df
        except Exception as e:
            st.warning(f"Could not fetch {ticker}: {str(e)}")
    return data

def generate_sample_data(ticker, days):
    """Generate sample data if real data fails"""
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    np.random.seed(hash(ticker) % 2**32)
    prices = 100 + np.cumsum(np.random.randn(len(dates)) * 2)
    df = pd.DataFrame({
        'Close': prices,
        'High': prices * 1.02,
        'Low': prices * 0.98,
        'Open': prices * 0.99,
        'Volume': np.random.randint(1000000, 10000000, len(dates))
    }, index=dates)
    return df

with st.spinner("📡 Fetching market data..."):
    market_data = fetch_data(list(portfolio.keys()), start_date, end_date)

# Fallback to sample data if fetch failed
if len(market_data) == 0:
    st.warning("⚠️ Could not fetch live data. Using sample data for demonstration.")
    for ticker in portfolio.keys():
        market_data[ticker] = generate_sample_data(ticker, days_back)

# ===== CALCULATE METRICS =====
latest_prices = {}
start_prices = {}

for ticker in portfolio.keys():
    if ticker in market_data:
        df = market_data[ticker]
        latest_prices[ticker] = float(df['Close'].iloc[-1])
        start_prices[ticker] = float(df['Close'].iloc[0])

total_value = 0.0
portfolio_value_start = 0.0

for ticker, qty in portfolio.items():
    if ticker in latest_prices:
        total_value += latest_prices[ticker] * qty
    if ticker in start_prices:
        portfolio_value_start += start_prices[ticker] * qty

gain_loss = total_value - portfolio_value_start
gain_loss_pct = (gain_loss / portfolio_value_start * 100) if portfolio_value_start > 0 else 0.0

# ===== KEY METRICS =====
st.subheader("📈 Portfolio Metrics")
col1, col2, col3, col4 = st.columns(4)

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
fig_pie.update_layout(title="Portfolio Distribution by Value", height=400)
st.plotly_chart(fig_pie, use_container_width=True)

# ===== PRICE CHARTS =====
st.subheader("📉 Individual Stock Performance")
tabs = st.tabs([f"{t}" for t in portfolio.keys()])

for idx, ticker in enumerate(portfolio.keys()):
    with tabs[idx]:
        if ticker in market_data:
            df = market_data[ticker].copy()
            
            current_price = float(df['Close'].iloc[-1])
            start_price = float(df['Close'].iloc[0])
            ticker_gain = ((current_price - start_price) / start_price) * 100
            
            col1, col2, col3 = st.columns(3)
            col1.metric(f"{ticker} Price", f"${current_price:.2f}")
            col2.metric(f"Change", f"{ticker_gain:.2f}%")
            col3.metric(f"Quantity", portfolio[ticker])
            
            # Calculate moving average
            df['SMA_20'] = df['Close'].rolling(window=20).mean()
            
            # Create chart
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df.index, y=df['Close'].values, mode='lines', name='Close Price', line=dict(color='#1f77b4')))
            fig.add_trace(go.Scatter(x=df.index, y=df['SMA_20'].values, mode='lines', name='20-Day MA', line=dict(color='orange', dash='dash')))
            fig.update_layout(title=f"{ticker} Price History", xaxis_title="Date", yaxis_title="Price ($)", height=400, hovermode='x unified')
            st.plotly_chart(fig, use_container_width=True)

# ===== HOLDINGS TABLE =====
st.subheader("📋 Holdings Summary")
holdings_list = []

for ticker in portfolio.keys():
    value = holdings_value.get(ticker, 0.0)
    pct = (value / total_value * 100) if total_value > 0 else 0.0
    holdings_list.append({
        "Ticker": ticker,
        "Quantity": portfolio[ticker],
        "Current Price": f"${latest_prices.get(ticker, 0):.2f}",
        "Value": f"${value:.2f}",
        "% of Portfolio": f"{pct:.1f}%"
    })

holdings_df = pd.DataFrame(holdings_list)
st.dataframe(holdings_df, use_container_width=True)

st.divider()
st.markdown(f"<div style='text-align: center; color: gray; font-size: 12px;'>Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}<br>📊 AI Portfolio Dashboard</div>", unsafe_allow_html=True)
