import yfinance as yf
import pandas as pd

# The bank stocks whose performance I am interested in
tickers = ["USB", "TFC", "PNC", "MTB", "FITB"]
# Download historical data
data = yf.download(tickers, start="2023-03-01", end="2023-03-15")

# Check what I got
print(data.head())
print(f"\nColumns structure: {data.columns.nlevels} levels")

# Test each ticker individually for validity
for ticker in tickers:
    stock = yf.Ticker(ticker)
    info = stock.info
    print(f"{ticker}: {info.get('longName', 'Not found')} | Sector: {info.get('sector', 'N/A')}")