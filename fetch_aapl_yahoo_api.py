import requests
import pandas as pd
from datetime import datetime, timedelta
import json
import os

# Yahoo Finance API endpoint
url = "https://query1.finance.yahoo.com/v8/finance/chart/AAPL"
params = {
    "range": "5y",
    "interval": "1d",
    "includePrePost": "false"
}
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

print("Fetching AAPL data from Yahoo Finance...")
response = requests.get(url, params=params, headers=headers)
if response.status_code != 200:
    print(f"Error: HTTP {response.status_code}")
    print(response.text[:200])
    exit(1)

data = response.json()
print("Data retrieved.")

# Parse the JSON structure
chart = data.get("chart", {})
if chart.get("error"):
    print(f"Error from Yahoo: {chart['error']}")
    exit(1)

result = chart.get("result", [])
if not result:
    print("No result found")
    exit(1)

first = result[0]
timestamps = first.get("timestamp", [])
indicators = first.get("indicators", {})
quote = indicators.get("quote", [{}])[0]
adjclose = indicators.get("adjclose", [{}])[0]

# Extract columns
open_prices = quote.get("open", [])
high_prices = quote.get("high", [])
low_prices = quote.get("low", [])
close_prices = quote.get("close", [])
volume = quote.get("volume", [])
adjclose_prices = adjclose.get("adjclose", [])

# Create DataFrame
df = pd.DataFrame({
    "Date": [datetime.fromtimestamp(ts) for ts in timestamps],
    "Open": open_prices,
    "High": high_prices,
    "Low": low_prices,
    "Close": close_prices,
    "Adj Close": adjclose_prices,
    "Volume": volume
})

# Remove rows with all NaN
df.dropna(subset=["Open", "High", "Low", "Close"], how="all", inplace=True)

print(f"Retrieved {len(df)} rows")
print(f"Date range: {df['Date'].min()} to {df['Date'].max()}")

# Save to CSV
output_file = "AAPL5Y.CSV"
df.to_csv(output_file, index=False)
print(f"Data saved to {output_file}")
print(f"File size: {os.path.getsize(output_file)} bytes")

# Show first and last few rows
print("\nFirst 5 rows:")
print(df.head())
print("\nLast 5 rows:")
print(df.tail())