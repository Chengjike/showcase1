import quandl
import pandas as pd
from datetime import datetime, timedelta
import os

# Set API key
API_KEY = "y9xSKARr6nfp8iszk-p7"
quandl.ApiConfig.api_key = API_KEY

# Calculate date 5 years ago
end_date = datetime.now().date()
start_date = end_date - timedelta(days=5*365)  # approximate 5 years

# Dataset code for Apple stock (EOD - End of Day)
# Try different dataset codes if needed
dataset_codes = [
    "EOD/AAPL",  # End of Day data
    "WIKI/AAPL", # Wiki dataset (discontinued but may have historical)
    "XNAS/AAPL", # NASDAQ exchange
]

data = None
for code in dataset_codes:
    try:
        print(f"Trying dataset: {code}")
        data = quandl.get(code, start_date=start_date, end_date=end_date)
        if data is not None and not data.empty:
            print(f"Successfully retrieved data from {code}")
            print(f"Data shape: {data.shape}")
            print(f"Columns: {data.columns.tolist()}")
            break
    except Exception as e:
        print(f"Failed with {code}: {e}")
        continue

if data is None or data.empty:
    print("Failed to retrieve data from any dataset.")
    # Try without specifying dataset code, just AAPL
    try:
        data = quandl.get("AAPL", start_date=start_date, end_date=end_date)
        print("Retrieved using just 'AAPL'")
    except Exception as e:
        print(f"Also failed with 'AAPL': {e}")
        exit(1)

# Save to CSV
output_file = "AAPL5Y.CSV"
data.to_csv(output_file)
print(f"Data saved to {output_file}")
print(f"File size: {os.path.getsize(output_file) if os.path.exists(output_file) else 'N/A'} bytes")

# Show first few rows
print("\nFirst 5 rows:")
print(data.head())
print("\nLast 5 rows:")
print(data.tail())