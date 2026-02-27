import quandl

API_KEY = "y9xSKARr6nfp8iszk-p7"
quandl.ApiConfig.api_key = API_KEY

# Search for AAPL datasets
print("Searching for AAPL datasets...")
results = quandl.search("AAPL", page=1)
print(f"Found {len(results)} results")
for i, result in enumerate(results[:10]):
    print(f"{i+1}. {result.get('dataset_code', 'N/A')} - {result.get('name', 'N/A')}")
    print(f"   Database: {result.get('database_code', 'N/A')}")
    print()