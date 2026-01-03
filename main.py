import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd

# The bank stocks whose performance I am interested in
tickers = ["USB", "TFC", "PNC", "MTB", "FITB","KRE"] #KRE is the ticker for a regional bank ETF which I am using to see
                                                    #the impact of the 2023 banking crisis
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
# Plot closing prices for all banks
closes = data.xs("Close", level=0, axis=1)

# Easy plotting
closes.plot(figsize=(12, 6))
plt.title("Regional Bank Closing Prices")
plt.ylabel("Price ($)")
plt.grid(True, alpha=0.3)
plt.show()

