import requests
import pandas as pd
import os

API_KEY = "y9xSKARr6nfp8iszk-p7"
url = "https://www.alphavantage.co/query"
params = {
    "function": "TIME_SERIES_DAILY",
    "symbol": "AAPL",
    "apikey": API_KEY,
    "outputsize": "compact"  # last 100 days
}

print("Fetching AAPL data from Alpha Vantage (last 100 days)...")
response = requests.get(url, params=params)
if response.status_code != 200:
    print(f"HTTP error: {response.status_code}")
    exit(1)

data = response.json()
if "Error Message" in data:
    print(f"API error: {data['Error Message']}")
    exit(1)
if "Information" in data:
    print(f"Information: {data['Information']}")
    # might be premium feature
    # try without outputsize
    params.pop("outputsize", None)
    response = requests.get(url, params=params)
    data = response.json()

if "Time Series (Daily)" not in data:
    print("Unexpected response format:")
    print(data)
    exit(1)

time_series = data["Time Series (Daily)"]
rows = []
for date, values in time_series.items():
    rows.append({
        "Date": date,
        "Open": float(values["1. open"]),
        "High": float(values["2. high"]),
        "Low": float(values["3. low"]),
        "Close": float(values["4. close"]),
        "Volume": int(values["5. volume"])
    })

df = pd.DataFrame(rows)
df.sort_values("Date", inplace=True)
print(f"Retrieved {len(df)} days of data")
print(f"Date range: {df['Date'].min()} to {df['Date'].max()}")

# Save to CSV
output_file = "AAPL_100DAYS.CSV"
df.to_csv(output_file, index=False)
print(f"Data saved to {output_file}")
print(f"File size: {os.path.getsize(output_file)} bytes")

print("\nFirst 5 rows:")
print(df.head())
print("\nLast 5 rows:")
print(df.tail())