# 📊 AI Portfolio Dashboard

A real-time portfolio analysis and performance tracking dashboard built with Streamlit.

## Features

✨ **Real-time Market Data** - Live stock prices from Yahoo Finance
📈 **Portfolio Performance** - Track gains/losses and percentages
🥧 **Portfolio Composition** - Visual breakdown of holdings
📉 **Stock Charts** - Individual stock performance analysis
📋 **Holdings Summary** - Detailed breakdown of all holdings

## Quick Start

### Local Development

```bash
pip install -r requirements.txt
streamlit run app.py
```

Then open your browser to `http://localhost:8501`

### Deploy to Streamlit Cloud

1. Push this repository to GitHub
2. Go to [streamlit.io/cloud](https://streamlit.io/cloud)
3. Click "New app"
4. Select this repository and `app.py` as the main file
5. Click "Deploy"

Your dashboard will be live at `https://your-username-portfolio-dashboard.streamlit.app`

## Configuration

### Add Your Own Portfolio

In the sidebar, select "Custom Portfolio" and enter your holdings in the format:
```
TICKER:QUANTITY
AAPL:10
MSFT:8
GOOGL:5
```

### Adjust Time Range

Use the slider in the sidebar to view 30-365 days of historical data.

## Technologies

- **Streamlit** - Web app framework
- **yfinance** - Stock market data
- **Plotly** - Interactive charts
- **Pandas** - Data analysis
- **Numpy** - Numerical computing

## API Keys

No API keys required for basic functionality. All stock data comes from Yahoo Finance.

## License

MIT License

## Support

For issues or feature requests, create an issue on GitHub.
