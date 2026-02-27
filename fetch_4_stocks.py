import requests
import pandas as pd
import time
import os
from datetime import datetime

API_KEY = "y9xSKARr6nfp8iszk-p7"
BASE_URL = "https://www.alphavantage.co/query"

# 股票代码列表
stocks = ["NVDA", "AAPL", "CRM", "IBM"]

def fetch_stock_data(symbol):
    """获取单只股票的最近100天数据"""
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol,
        "apikey": API_KEY,
        "outputsize": "compact"  # 最近100个数据点
    }

    print(f"正在获取 {symbol} 数据...")
    response = requests.get(BASE_URL, params=params)

    if response.status_code != 200:
        print(f"  {symbol}: HTTP错误 {response.status_code}")
        return None

    data = response.json()

    if "Error Message" in data:
        print(f"  {symbol}: API错误 - {data['Error Message']}")
        return None

    if "Information" in data:
        print(f"  {symbol}: 信息 - {data['Information']}")
        return None

    if "Time Series (Daily)" not in data:
        print(f"  {symbol}: 响应格式异常")
        return None

    time_series = data["Time Series (Daily)"]
    rows = []

    for date, values in time_series.items():
        rows.append({
            "symbol": symbol,
            "date": date,
            "open": float(values["1. open"]),
            "high": float(values["2. high"]),
            "low": float(values["3. low"]),
            "close": float(values["4. close"]),
            "volume": int(values["5. volume"])
        })

    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"])
    df.sort_values("date", inplace=True)

    print(f"  {symbol}: 获取了 {len(df)} 天数据 ({df['date'].min().date()} 至 {df['date'].max().date()})")
    return df

def main():
    print("开始获取4家公司股价数据...")
    print("=" * 50)

    all_data = []

    for i, symbol in enumerate(stocks):
        df = fetch_stock_data(symbol)
        if df is not None:
            all_data.append(df)

        # 避免API限制，每次请求间隔15秒（Alpha Vantage免费版限制：5次/分钟）
        if i < len(stocks) - 1:
            print(f"等待15秒以避免API限制...")
            time.sleep(15)

    if not all_data:
        print("错误：未能获取任何数据")
        return

    # 合并所有数据
    combined_df = pd.concat(all_data, ignore_index=True)

    # 保存为单个CSV文件
    output_file = "stocks_100days.csv"
    combined_df.to_csv(output_file, index=False)

    print("\n" + "=" * 50)
    print(f"数据已保存到 {output_file}")
    print(f"文件大小: {os.path.getsize(output_file)} 字节")
    print(f"总数据行数: {len(combined_df)}")

    # 显示统计信息
    print("\n📊 数据统计:")
    print("-" * 30)
    for symbol in stocks:
        symbol_data = combined_df[combined_df["symbol"] == symbol]
        if len(symbol_data) > 0:
            latest = symbol_data.iloc[-1]
            print(f"{symbol}: {len(symbol_data)} 天数据，最新收盘价: ${latest['close']:.2f}")
        else:
            print(f"{symbol}: 无数据")

    # 显示前几行数据
    print("\n📋 数据样例（前10行）:")
    print(combined_df.head(10).to_string(index=False))

    # 保存为Excel文件（可选）
    try:
        excel_file = "stocks_100days.xlsx"
        combined_df.to_excel(excel_file, index=False)
        print(f"\n📁 同时保存为Excel文件: {excel_file}")
    except Exception as e:
        print(f"\n⚠️ 无法保存Excel文件: {e}")

if __name__ == "__main__":
    main()