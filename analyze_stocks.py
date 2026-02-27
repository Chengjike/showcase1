import pandas as pd
import numpy as np

# 读取数据
df = pd.read_csv('stocks_100days.csv')
df['date'] = pd.to_datetime(df['date'])

print("📊 数据集结构分析")
print("=" * 60)

# 基本信息
print("1. 数据基本信息:")
print(f"   总行数: {len(df)}")
print(f"   数据列: {', '.join(df.columns.tolist())}")
print(f"   时间范围: {df['date'].min().date()} 至 {df['date'].max().date()}")

# 股票统计
print(f"\n2. 股票分布:")
stock_counts = df['symbol'].value_counts()
for symbol, count in stock_counts.items():
    print(f"   {symbol}: {count} 天数据")

# 数据完整性检查
print(f"\n3. 数据完整性:")
for symbol in df['symbol'].unique():
    symbol_data = df[df['symbol'] == symbol]
    date_range = symbol_data['date'].max() - symbol_data['date'].min()
    trading_days = len(symbol_data)
    print(f"   {symbol}: {trading_days} 个交易日，跨度 {date_range.days} 天")

# 基本统计
print(f"\n4. 价格统计（所有股票）:")
price_cols = ['open', 'high', 'low', 'close']
for col in price_cols:
    print(f"   {col.capitalize()}: ${df[col].mean():.2f} (平均) | ${df[col].min():.2f} (最低) | ${df[col].max():.2f} (最高)")

print(f"\n5. 成交量统计:")
print(f"   平均成交量: {df['volume'].mean():,.0f} 股")
print(f"   总成交量: {df['volume'].sum():,.0f} 股")

# 各股票最新价格
print(f"\n6. 最新股价（{df['date'].max().date()}）:")
latest_prices = {}
for symbol in df['symbol'].unique():
    latest = df[df['symbol'] == symbol].sort_values('date').iloc[-1]
    latest_prices[symbol] = latest['close']
    print(f"   {symbol}: ${latest['close']:.2f}")

# 计算日收益率（为后续分析准备）
df['daily_return'] = df.groupby('symbol')['close'].pct_change()

print(f"\n7. 收益率统计:")
for symbol in df['symbol'].unique():
    symbol_returns = df[df['symbol'] == symbol]['daily_return'].dropna()
    if len(symbol_returns) > 0:
        print(f"   {symbol}: 平均日收益率 {symbol_returns.mean()*100:.3f}% | 标准差 {symbol_returns.std()*100:.3f}%")

# 数据质量检查
print(f"\n8. 数据质量检查:")
print(f"   缺失值数量:")
for col in df.columns:
    missing = df[col].isnull().sum()
    if missing > 0:
        print(f"     {col}: {missing} 个缺失值")

# 检查重复数据
duplicates = df.duplicated(subset=['symbol', 'date']).sum()
print(f"   重复数据行: {duplicates}")

print("\n" + "=" * 60)
print("分析完成！基于以上数据可以进行多种金融分析。")