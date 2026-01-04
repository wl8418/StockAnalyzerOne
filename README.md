# Regional Bank Stress Analysis (March 2023 Crisis)

## Project Overview
This project conducts a quantitative analysis of regional bank stocks during the volatility surrounding the March 2023 banking crisis (Silicon Valley Bank, Signature Bank). It implements a data pipeline in Python to screen for relative underperformance, serving as a practical simulation of initial crisis detection.

## Methodology
1.  Data Collection: Historical price data was fetched for a basket of regional banks (USB, TFC, PNC, MTB, FITB) and the SPDR S&P Regional Banking ETF (KRE) using the yfinance library.
2.  Core Analysis:
    *   Calculated total absolute returns for the period of March 1-15, 2023.
    *   Calculated relative returns for each bank against the `KRE` ETF to isolate stock-specific (idiosyncratic) performance from sector-wide moves.
3.  Visualization: Generated comparative price charts to visually inspect trends and drawdowns.

## Key Findings & Output
*   Worst Absolute Performer: TFC posted the lowest total return at -31.73% during the period.
*   Worst Relative Performer: TFC underperformed the KRE ETF by -5.8969% , indicating it faced disproportionate stress beyond the general sector decline.
*   Visual Insight: All banks in the basket exhibited high correlation and significant drawdowns coinciding with the SVB failure on March 10, 2023.

## How to Run
1.  Ensure Python 3.7+ is installed along with required packages:
    ```bash
    pip install yfinance pandas matplotlib
    ```
2.  Clone this repository and run the main analysis script:
    ```bash
    python bank_stress_analysis.py
    ```

## Skills Demonstrated
*   Financial Data Analysis: Using APIs (yfinance) to acquire and clean real-world market data.
*   Quantitative Modeling: Implementing calculations for absolute/relative returns to measure risk and performance.
*   Programming & Visualization: Automating analysis with Python (pandas) and creating clear visualizations (matplotlib).
*   Financial Intuition: Building a practical tool to identify outlier underperformance during a market stress event.

## Connection to Broader Work
This analysis mirrors the screening methodology I applied intuitively in the **Arkansas Stock Market Game**, where I identified and shorted Signature Bank prior to its failure. This project formalizes that process into a reproducible, data-driven script.
