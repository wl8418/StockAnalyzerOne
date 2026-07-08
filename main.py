import sys
if "/Users/warrenli/Library/Python/3.9/lib/python/site-packages" not in sys.path:
    sys.path.append("/Users/warrenli/Library/Python/3.9/lib/python/site-packages")

import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta

# ==========================================
# MACRO ECONOMY BENCHMARKS
# ==========================================
# ^GSPC = S&P 500, ^IXIC = Nasdaq Composite, ^RUT = Russell 2000
economy_benchmark_tickers = ["^GSPC", "^IXIC", "^RUT"]

# ==========================================
# SECTOR BENCHMARKS & INDIVIDUAL STOCKS
# ==========================================

# FINANCE: JPMorgan, Bank of America, Wells Fargo, US Bank, PNC, Truist, Citigroup
finance_benchmark_tickers = ["KRE", "KBWB", "XLF", "JPM", "BAC", "WFC", "USB", "PNC", "TFC", "C"]

# TECHNOLOGY: Apple, Microsoft, Nvidia, Alphabet (Google), AMD, Salesforce, Adobe
technology_benchmark_tickers = ["XLK", "VGT", "AAPL", "MSFT", "NVDA", "GOOGL", "AMD", "CRM", "ADBE","IBM"]

# HEALTHCARE: Johnson & Johnson, UnitedHealth, Eli Lilly, Pfizer, Merck, AbbVie, Thermo Fisher
healthcare_benchmark_tickers = ["XLV", "VHT", "JNJ", "UNH", "LLY", "PFE", "MRK", "ABBV", "TMO"]

# GROCERIES / STAPLES: Walmart, Costco, Kroger, Target, Sysco, General Mills, Sprouts Farmer's Market
groceries_benchmark_tickers = ["XLP", "PBJ", "WMT", "COST", "KR", "TGT", "SYY", "GIS", "SFM"]

# UTILITIES: NextEra Energy, Duke Energy, Southern Company, Dominion, Exelon, Am. Electric, Sempra
utilities_benchmark_tickers = ["XLU", "VPU", "NEE", "DUK", "SO", "D", "EXC", "AEP", "SRE"]

# AUTOMOTIVE / MFG: Tesla, Ford, Gen. Motors, Toyota, Caterpillar, Deere, General Electric
automotive_manufacturing_benchmark_tickers = ["XLI", "CARZ", "TSLA", "F", "GM", "TM", "CAT", "DE", "GE"]

# SUPPLY CHAIN / LOGISTICS: UPS, FedEx, Union Pacific, CSX, Norfolk Southern, Old Dominion, Expeditors, JB Hunt
supply_chain_benchmark_tickers = ["IYT", "UPS", "FDX", "UNP", "CSX", "NSC", "ODFL", "EXPD", "JBHT", "CSX","CNI", "CP"]

# DEFENSE: Lockheed Martin, RTX (Raytheon), General Dynamics, Northrop Grumman, Huntington Ingalls, L3Harris, Textron
defense_benchmark_tickers = ["ITA", "XAR", "LMT", "RTX", "GD", "NOC", "HII", "LHX", "TXT"]

# Combine all lists for one single bulk download
all_benchmarks = (
    economy_benchmark_tickers + 
    finance_benchmark_tickers + 
    technology_benchmark_tickers + 
    healthcare_benchmark_tickers + 
    groceries_benchmark_tickers + 
    utilities_benchmark_tickers + 
    automotive_manufacturing_benchmark_tickers + 
    supply_chain_benchmark_tickers + 
    defense_benchmark_tickers
)

# Map the sectors into a dictionary for the automated loop
benchmark_dictionary = {
    "finance": finance_benchmark_tickers, 
    "technology": technology_benchmark_tickers, 
    "healthcare": healthcare_benchmark_tickers, 
    "groceries": groceries_benchmark_tickers, 
    "utilities": utilities_benchmark_tickers, 
    "automotive_manufacturing": automotive_manufacturing_benchmark_tickers, 
    "supply_chain": supply_chain_benchmark_tickers, 
    "defense": defense_benchmark_tickers
}

# ==========================================
# 1. CALCULATE DATE RANGE & DOWNLOAD DATA
# ==========================================
end_date = datetime.today()
start_date = end_date - timedelta(days=5*365)  # Exact 5 years back
# Convert dates to strings for yfinance
start_date_str = start_date.strftime("%Y-%m-%d")
end_date_str = end_date.strftime("%Y-%m-%d")

print("Downloading historical data... This may take a moment.")
data = yf.download(all_benchmarks, start=start_date_str, end=end_date_str, actions = True, progress=False)
print("Download complete.\n")

# Use Adjusted Close to account for dividends across sectors
closes = data['Close']

# ==========================================
# 2. CALCULATE TOTAL RETURNS
# ==========================================
total_returns = (closes.iloc[-1] - closes.iloc[0]) / closes.iloc[0]

print("=== MACRO MARKET BENCHMARK PERFORMANCE ===")
for macro in economy_benchmark_tickers:
    print(f"{macro}: {total_returns[macro]:.2%}")
# Outlier detection method
def stock_price_drop(stock_series, benchmark_series):
    """
    Analyzes daily returns to find isolated drops > 5%.
    Ignores drops if the benchmark also dropped > 2% (market crash).
    """
    # 1. Calculate daily percentage changes for both
    stock_returns = stock_series.pct_change()
    benchmark_returns = benchmark_series.pct_change()
    
    # 2. Find days where the stock crashed by more than 5%
    stock_crashes = stock_returns <= -0.05
    
    # 3. Find days where the market crashed by more than 2%
    market_crashes = benchmark_returns <= -0.02
    
    # 4. Filter for days where the stock crashed BUT the market was fine
    # The '~' symbol means "NOT" in Pandas logic
    isolated_crashes = stock_crashes & (~market_crashes)
    
    # 5. Extract the actual percentage drops on those specific penalty days
    penalty_days = stock_returns[isolated_crashes]
    
    # Return the series of bad days (can be used to count or sum penalties)
    return penalty_days

#dividend tracker
def track_dividends(dividend_series, price_series):
    """
    Returns a sequence representing the annual change in dividends.
    Also evaluates if the stock price beat the 3% annual inflation threshold.
    """
    # DEFENSIVE CHECK: If the stock has no dividend data, or the price data failed to download, exit safely.
    if dividend_series.empty or dividend_series.isna().all() or price_series.dropna().empty:
        return pd.Series(dtype=float), False
        
    # 1. Group the daily dividend data by year and sum it up
    # 'YE' stands for Year-End in modern Pandas
    annual_dividends = dividend_series.resample('YE').sum()
    
    # 2. Calculate the year-over-year percentage change
    # We use .clip(upper=1.0) to ensure the number is less than or equal to 1 
    # (This prevents massive spikes if a company issues a rare "special dividend")
    div_change = annual_dividends.pct_change().clip(upper=1.0).dropna()
    
    # 3. Check the 3% annualized price growth rule
    total_price_return = (price_series.dropna().iloc[-1] - price_series.dropna().iloc[0]) / price_series.dropna().iloc[0]
    
    # Calculate the annualized return over our 5-year window
    annualized_return = (1 + total_price_return) ** (1/5) - 1
    beat_inflation = annualized_return >= 0.03
    
    return div_change, beat_inflation
# value growth reader
def market_share(ticker_symbol):
    """
    Acts as a proxy for market share by calculating annual revenue growth.
    Returns a sequence representing the YoY change in revenue (capped at 1.0).
    """
    stock = yf.Ticker(ticker_symbol)
    
    try:
        # Pull the annual income statement
        income_stmt = stock.income_stmt
        
        # Check if the company has revenue data reported
        if 'Total Revenue' in income_stmt.index:
            revenue = income_stmt.loc['Total Revenue']
        else:
            # If no revenue data exists (e.g., it's an ETF), return an empty sequence
            return pd.Series(dtype=float)
            
        # yfinance returns dates descending (newest first). 
        # We must sort oldest to newest so our percentage math works forward in time.
        revenue = revenue.sort_index(ascending=True)
        
        # Calculate Year-over-Year change and cap it at 1.0
        revenue_change = revenue.pct_change().clip(upper=1.0).dropna()
        
        return revenue_change
        
    except Exception as e:
        # Failsafe: if Yahoo Finance blocks the request or data is missing, return empty
        return pd.Series(dtype=float)
def get_dividend_yield(dividend_series, price_series):
    """
    Calculates the average annual dividend yield over the 5-year period.
    Returns the yield as a percentage (e.g., 2.5 for 2.5%) so it scales 
    properly with the rest of the scoring algorithm.
    """
    if dividend_series.empty or dividend_series.isna().all() or price_series.dropna().empty:
        return 0.0
        
    # Calculate the total dividends paid each year
    annual_divs = dividend_series.resample('YE').sum()
    
    # Calculate the average stock price for each year
    annual_prices = price_series.resample('YE').mean()
    
    # Divide dividends by price to get the yield for each year
    annual_yields = annual_divs / annual_prices
    
    # Return the average yield across the 5 years, multiplied by 100 
    avg_yield_percentage = annual_yields.mean() * 100
    
    # Failsafe for NaN values
    if pd.isna(avg_yield_percentage):
        return 0.0
        
    return avg_yield_percentage
# ==========================================
# 3. QUANTITATIVE SCORING ALGORITHM
# ==========================================
print("\n=== EXECUTING QUANTITATIVE GRADING ALGORITHM ===")

# We will store the final scores in a dictionary to easily sort the winners
stock_scores = {}

for sector_name, sector_tickers in benchmark_dictionary.items():
    print(f"\nAnalyzing {sector_name.upper()} sector...")
    
    # In your dictionary, the first ticker is the sector benchmark
    benchmark_ticker = sector_tickers[0]
    benchmark_series = closes[benchmark_ticker]
    
    # We will grade every ticker in the list against the benchmark
    for ticker in sector_tickers:
        print(f"  --> Grading {ticker}...")
        stock_series = closes[ticker]
        
        # 1. PRICE DROPS (Penalty)
        # Summing the negative percentage drops naturally subtracts from the score
        penalty_days = stock_price_drop(stock_series, benchmark_series)
        drop_score = penalty_days.sum() 
        
        # 2. DIVIDENDS
        # Extract dividends for this specific ticker, fallback to empty if none exist
        if 'Dividends' in data.columns and ticker in data['Dividends'].columns:
            div_series = data['Dividends'][ticker]
        else:
            div_series = pd.Series(dtype=float)
            
        div_change, beat_inflation = track_dividends(div_series, stock_series)
        div_score = div_change.sum()
        
        # Apply your logic: if they increased dividends but failed the 3% price growth, 
        # it's a bad sign. We cancel out their dividend reward.
        if div_score > 0 and not beat_inflation:
            div_score = 0
            
        # [Existing Code] ...
        # 3. MARKET SHARE (Revenue proxy)
        rev_change = market_share(ticker)
        #benchmark_rev_change =
        rev_score = rev_change.sum()
        
        # ================= NEW CODE HERE =================
        # 4. DIVIDEND YIELD
        yield_score = get_dividend_yield(div_series, stock_series)
        
        # 5. FINAL CALCULATION
        # Return sum of values dividends + market_share + stock_price_drop + yield
        total_score = div_score + rev_score + drop_score + .2*yield_score
        
        # Save to our dictionary (Now including Yield Score)
        stock_scores[ticker] = {
            "Sector": sector_name.capitalize(),
            "Div Score": round(div_score, 2),
            "Yield Score": round(yield_score, 2),
            "Rev Score": round(rev_score, 2),
            "Drop Penalty": round(drop_score, 2),
            "Total Score": round(total_score, 2)
        }

# ==========================================
# 4. DISPLAY THE FINAL LEADERBOARD
# ==========================================
# Pandas makes it incredibly easy to print dictionaries as beautiful tables
scores_df = pd.DataFrame.from_dict(stock_scores, orient='index')

print("\n=== FINAL STOCK GRADES (BEST TO WORST) ===")
# Sort the dataframe so the highest score is at the very top
print(scores_df.sort_values(by="Total Score", ascending=False))