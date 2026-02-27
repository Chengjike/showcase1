import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import os

# Calculate date 5 years ago
end_date = datetime.now().date()
start_date = end_date - timedelta(days=5*365)

print(f"Fetching AAPL data from {start_date} to {end_date} using yfinance...")

# Download data
ticker = yf.Ticker("AAPL")
data = ticker.history(start=start_date, end=end_date)

if data.empty:
    print("No data retrieved.")
else:
    print(f"Retrieved {len(data)} rows")
    print(f"Columns: {data.columns.tolist()}")

    # Save to CSV
    output_file = "AAPL5Y.CSV"
    data.to_csv(output_file)
    print(f"Data saved to {output_file}")
    print(f"File size: {os.path.getsize(output_file)} bytes")

    # Show first and last few rows
    print("\nFirst 5 rows:")
    print(data.head())
    print("\nLast 5 rows:")
    print(data.tail())

    # Basic statistics
    print("\nSummary statistics:")
    print(data.describe())