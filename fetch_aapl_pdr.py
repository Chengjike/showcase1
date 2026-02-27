import pandas_datareader.data as web
import datetime
import os

# Calculate dates
end_date = datetime.datetime.now()
start_date = end_date - datetime.timedelta(days=5*365)

print(f"Fetching AAPL data from Yahoo Finance via pandas-datareader...")
print(f"Date range: {start_date.date()} to {end_date.date()}")

try:
    # Try Yahoo source
    df = web.DataReader("AAPL", "yahoo", start_date, end_date)
except Exception as e:
    print(f"Yahoo failed: {e}")
    # Try Alpha Vantage source using the provided API key
    import pandas_datareader.av.alpha_vantage as av
    # Not straightforward, let's try using web.DataReader with 'av' source
    try:
        df = web.DataReader("AAPL", "av", start_date, end_date, api_key="y9xSKARr6nfp8iszk-p7")
    except Exception as e2:
        print(f"Alpha Vantage failed: {e2}")
        exit(1)

print(f"Retrieved {len(df)} rows")
print(f"Columns: {df.columns.tolist()}")

# Save to CSV
output_file = "AAPL5Y.CSV"
df.to_csv(output_file)
print(f"Data saved to {output_file}")
print(f"File size: {os.path.getsize(output_file)} bytes")

# Show first and last rows
print("\nFirst 5 rows:")
print(df.head())
print("\nLast 5 rows:")
print(df.tail())