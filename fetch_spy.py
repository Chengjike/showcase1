import requests
import pandas as pd
import time
import os
from datetime import datetime

API_KEY = "y9xSKARr6nfp8iszk-p7"
BASE_URL = "https://www.alphavantage.co/query"

def fetch_spy_data():
    """获取SPY ETF的最近100天数据作为基准"""
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": "SPY",
        "apikey": API_KEY,
        "outputsize": "compact"  # 最近100个数据点
    }

    print("正在获取SPY（标普500 ETF）数据作为基准...")
    print(f"API Key: {API_KEY[:8]}...")

    # 添加延迟以避免API限制
    print("等待10秒以避免API限制...")
    time.sleep(10)

    response = requests.get(BASE_URL, params=params)

    if response.status_code != 200:
        print(f"HTTP错误 {response.status_code}")
        print(response.text[:200])
        return None

    data = response.json()

    if "Error Message" in data:
        print(f"API错误: {data['Error Message']}")
        return None

    if "Information" in data:
        print(f"信息: {data['Information']}")
        # 尝试移除outputsize参数
        params.pop("outputsize", None)
        response = requests.get(BASE_URL, params=params)
        data = response.json()

    if "Time Series (Daily)" not in data:
        print("响应格式异常，可能包含:")
        print(list(data.keys())[:5])
        return None

    time_series = data["Time Series (Daily)"]
    rows = []

    for date, values in time_series.items():
        rows.append({
            "symbol": "SPY",
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

    print(f"获取了 {len(df)} 天SPY数据")
    print(f"时间范围: {df['date'].min().date()} 至 {df['date'].max().date()}")

    return df

def main():
    print("=" * 60)
    print("SPY数据获取脚本 - 标普500 ETF基准数据")
    print("=" * 60)

    df = fetch_spy_data()

    if df is None or df.empty:
        print("错误：未能获取SPY数据")
        return

    # 保存为CSV文件
    output_file = "SPY_benchmark.csv"
    df.to_csv(output_file, index=False)

    print(f"\n数据已保存到 {output_file}")
    print(f"文件大小: {os.path.getsize(output_file)} 字节")

    # 显示统计信息
    print("\n📊 SPY数据统计:")
    print("-" * 40)
    print(f"总数据行数: {len(df)}")
    print(f"最新日期: {df['date'].max().date()}")
    print(f"最新收盘价: ${df.iloc[-1]['close']:.2f}")

    # 计算基本统计
    print(f"平均收盘价: ${df['close'].mean():.2f}")
    print(f"价格范围: ${df['close'].min():.2f} - ${df['close'].max():.2f}")
    print(f"平均成交量: {df['volume'].mean():,.0f} 股")

    # 计算收益率
    df['daily_return'] = df['close'].pct_change()
    returns = df['daily_return'].dropna()

    if len(returns) > 0:
        print(f"平均日收益率: {returns.mean()*100:.3f}%")
        print(f"日收益率标准差: {returns.std()*100:.3f}%")
        print(f"最大单日涨幅: {returns.max()*100:.2f}%")
        print(f"最大单日跌幅: {returns.min()*100:.2f}%")

    # 显示前几行数据
    print("\n📋 数据样例（前5行）:")
    print(df.head().to_string(index=False))

    print("\n📋 数据样例（后5行）:")
    print(df.tail().to_string(index=False))

    # 检查与现有数据的时间范围匹配
    print("\n🔍 与现有股票数据时间范围对比:")
    try:
        existing_df = pd.read_csv('stocks_100days.csv')
        existing_df['date'] = pd.to_datetime(existing_df['date'])
        existing_min = existing_df['date'].min()
        existing_max = existing_df['date'].max()

        spy_min = df['date'].min()
        spy_max = df['date'].max()

        print(f"现有股票数据范围: {existing_min.date()} 至 {existing_max.date()}")
        print(f"SPY数据范围: {spy_min.date()} 至 {spy_max.date()}")

        # 检查重叠日期
        spy_dates = set(df['date'].dt.date)
        stock_dates = set(existing_df['date'].dt.date)
        overlap = spy_dates.intersection(stock_dates)

        print(f"共同交易日数量: {len(overlap)}")

        if len(overlap) < min(len(spy_dates), len(stock_dates)):
            print("⚠️  警告: SPY与股票数据日期不完全匹配")

    except FileNotFoundError:
        print("未找到stocks_100days.csv文件")

    print("\n" + "=" * 60)
    print("SPY基准数据获取完成！")
    print(f"文件位置: {os.path.abspath(output_file)}")

if __name__ == "__main__":
    main()