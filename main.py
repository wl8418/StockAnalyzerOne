import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd

# The bank stocks whose performance I am interested in
tickers = ["USB", "TFC", "PNC", "MTB", "FITB","KRE"] #KRE is the ticker for a regional bank ETF which I am using to see
                                                    #the impact of the 2023 banking crisis
start_date = "2023-03-01"
end_date = "2023-03-15"
# Download historical data
print("Downloading data... This may take a moment.")
# Download with progress bar disabled for cleaner output
data = yf.download(tickers, start=start_date, end=end_date, progress=False)
print("Download complete.\n")


# Check what I got
print(data.head())
print(f"\nColumns structure: {data.columns.nlevels} levels")

# Test each ticker individually for validity
for ticker in tickers:
    stock = yf.Ticker(ticker)
    info = stock.info
    print(f"{ticker}: {info.get('longName', 'Not found')} | Sector: {info.get('sector', 'N/A')}")



# 1. EXTRACT CLOSING PRICES
closes = data.xs("Close", level=0, axis=1)
print("First few rows of closing prices:")
print(closes.head())

# 2. CALCULATE TOTAL RETURNS OVER THE ENTIRE PERIOD
# Formula: (Last Price - First Price) / First Price
total_returns = (closes.iloc[-1] - closes.iloc[0]) / closes.iloc[0]

print("\n=== TOTAL RETURN ANALYSIS ===")
print("Return from", start_date, "to", end_date)
print(total_returns.sort_values())  # Sorts from worst to best performer

# 3. IDENTIFY THE WORST PERFORMER
worst_ticker = total_returns.idxmin()
worst_return = total_returns.min()
print(f"\nWorst performer: {worst_ticker} at {worst_return:.2%}")

# 4. CALCULATE RELATIVE PERFORMANCE vs. the ETF (KRE)
# This shows which banks underperformed or beat the sector.
print("\n=== RELATIVE PERFORMANCE vs. KRE (ETF) ===")
etf_return = total_returns["KRE"]
relative_perf = total_returns - etf_return  # Positive = beat the ETF, Negative = lagged
print(relative_perf.sort_values())

# Plot the data to have a visual
closes.plot(figsize=(12, 6))
plt.title("Regional Bank Closing Prices")
plt.ylabel("Price ($)")
plt.grid(True, alpha=0.3)
plt.show()




