#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import json
from datetime import datetime

print("正在读取数据...")
# 读取数据
df = pd.read_csv('AAPL_100DAYS.CSV')
df['Date'] = pd.to_datetime(df['Date'])
df = df.sort_values('Date')

print("计算基础指标...")
# 1. 基础指标
total_days = len(df)
date_range_start = df['Date'].min().strftime('%Y-%m-%d')
date_range_end = df['Date'].max().strftime('%Y-%m-%d')
date_range = f'{date_range_start} 至 {date_range_end}'

first_close = float(df.iloc[0]['Close'])
last_close = float(df.iloc[-1]['Close'])
ytd_return = (last_close - first_close) / first_close * 100

avg_volume = int(df['Volume'].mean())

# 2. 价格波动指标
max_high = float(df['High'].max())
max_high_date = df.loc[df['High'].idxmax(), 'Date'].strftime('%Y-%m-%d')
min_low = float(df['Low'].min())
min_low_date = df.loc[df['Low'].idxmin(), 'Date'].strftime('%Y-%m-%d')

# 计算日内振幅 (High - Low) / 前日收盘价 × 100%
df['Prev_Close'] = df['Close'].shift(1)
df.loc[df.index[0], 'Prev_Close'] = df.loc[df.index[0], 'Close']  # 第一天用当天收盘价
df['Daily_Amplitude_Pct'] = (df['High'] - df['Low']) / df['Prev_Close'] * 100
avg_daily_amplitude = float(df['Daily_Amplitude_Pct'].mean())

# 涨跌天数
df['Price_Change'] = df['Close'] - df['Open']
up_days = int((df['Price_Change'] > 0).sum())
down_days = int((df['Price_Change'] < 0).sum())
flat_days = total_days - up_days - down_days

print("计算移动平均线...")
# 3. 移动平均线
df['MA5'] = df['Close'].rolling(window=5).mean()
df['MA20'] = df['Close'].rolling(window=20).mean()
current_ma5 = float(df['MA5'].iloc[-1])
current_ma20 = float(df['MA20'].iloc[-1])

print("分析成交量...")
# 4. 成交量分析
df['Volume_Rank'] = df['Volume'].rank(ascending=False, method='first')
top3_volume = df.nlargest(3, 'Volume')[['Date', 'Volume', 'Close', 'Open']].copy()
top3_volume['Date_Str'] = top3_volume['Date'].dt.strftime('%Y-%m-%d')
top3_volume['Daily_Return_Pct'] = (top3_volume['Close'] - top3_volume['Open']) / top3_volume['Open'] * 100

# 准备成交量最大的3天数据用于HTML表格
top3_table_data = []
for idx, row in top3_volume.iterrows():
    top3_table_data.append({
        'date': row['Date_Str'],
        'volume': f"{int(row['Volume']):,}",
        'return_pct': f"{row['Daily_Return_Pct']:.2f}%",
        'close': f"${row['Close']:.2f}"
    })

print("分析近期表现...")
# 5. 最近10个交易日分析
last_10 = df.tail(10).copy()
first_10_close = float(last_10.iloc[0]['Close'])
last_10_close = float(last_10.iloc[-1]['Close'])
last_10_return = (last_10_close - first_10_close) / first_10_close * 100

# 前期对比 (前10个交易日)
if len(df) >= 20:
    prev_10 = df.iloc[-20:-10].copy()
else:
    prev_10 = df.head(10).copy()
prev_10_first_close = float(prev_10.iloc[0]['Close'])
prev_10_last_close = float(prev_10.iloc[-1]['Close'])
prev_10_return = (prev_10_last_close - prev_10_first_close) / prev_10_first_close * 100

print("计算支撑阻力位...")
# 6. 支撑与阻力位
recent_low = float(df.tail(20)['Low'].min())
recent_high = float(df.tail(20)['High'].max())

# 7. 波动较大交易日 (振幅 > 平均振幅+标准差)
amplitude_std = float(df['Daily_Amplitude_Pct'].std())
high_volatility_threshold = avg_daily_amplitude + amplitude_std
high_volatility_days = df[df['Daily_Amplitude_Pct'] > high_volatility_threshold].copy()
high_volatility_days['Date_Str'] = high_volatility_days['Date'].dt.strftime('%Y-%m-%d')

# 获取波动最大的3天
top3_volatility = high_volatility_days.nlargest(3, 'Daily_Amplitude_Pct')[['Date_Str', 'Daily_Amplitude_Pct', 'Close']].copy()

print("判断整体趋势...")
# 8. 整体趋势判断
price_change_pct = ytd_return
if price_change_pct > 2:
    trend = '上涨'
    trend_color = '#10b981'  # 绿色
elif price_change_pct < -2:
    trend = '下跌'
    trend_color = '#ef4444'  # 红色
else:
    trend = '震荡'
    trend_color = '#f59e0b'  # 黄色

# 9. 量价关系分析
df['Price_Change_Pct'] = df['Close'].pct_change() * 100
df['Volume_Change_Pct'] = df['Volume'].pct_change() * 100
# 计算量价相关性 (剔除NaN)
valid_data = df[['Price_Change_Pct', 'Volume_Change_Pct']].dropna()
if len(valid_data) > 1:
    price_volume_corr = float(valid_data['Price_Change_Pct'].corr(valid_data['Volume_Change_Pct']))
else:
    price_volume_corr = 0.0

# 量价关系判断
if price_volume_corr > 0.3:
    price_volume_relation = "正相关（量价齐升）"
elif price_volume_corr < -0.3:
    price_volume_relation = "负相关（量价背离）"
else:
    price_volume_relation = "弱相关（量价关系不明确）"

print("准备图表数据...")
# 准备图表数据
dates = df['Date'].dt.strftime('%Y-%m-%d').tolist()
opens = df['Open'].tolist()
highs = df['High'].tolist()
lows = df['Low'].tolist()
closes = df['Close'].tolist()
volumes = df['Volume'].tolist()
ma5_values = df['MA5'].tolist()
ma20_values = df['MA20'].tolist()
daily_amplitude_pct = df['Daily_Amplitude_Pct'].tolist()

# 确定成交量颜色（上涨红色，下跌绿色）
volume_colors = []
for i in range(len(closes)):
    if i == 0:
        volume_colors.append('#10b981')  # 第一天默认绿色
    else:
        if closes[i] > opens[i]:
            volume_colors.append('#ef4444')  # 上涨红色
        else:
            volume_colors.append('#10b981')  # 下跌绿色

print("生成HTML报告...")
# 生成HTML
html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>苹果公司股价深度洞察报告</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        /* 基础样式 */
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Helvetica', 'Arial', 'Microsoft YaHei', sans-serif;
            background: #ffffff;
            color: #1a1a1a;
            line-height: 1.6;
            padding: 20px;
            min-height: 100vh;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}

        /* 标题区域 */
        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding: 30px;
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
            border-bottom: 4px solid #0047BB;
        }}

        .header h1 {{
            color: #1e293b;
            font-size: 2.5rem;
            margin-bottom: 10px;
            font-weight: 700;
        }}

        .header .subtitle {{
            color: #64748b;
            font-size: 1.1rem;
            margin-bottom: 15px;
        }}

        .header .date-range {{
            background: #f8f9fa;
            padding: 10px 20px;
            border-radius: 8px;
            display: inline-block;
            font-weight: 500;
            color: #666666;
            border: 1px solid #e9ecef;
        }}

        /* 卡片样式 */
        .card-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .card {{
            background: white;
            border-radius: 10px;
            padding: 24px;
            box-shadow: 0 3px 10px rgba(0, 0, 0, 0.04);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            border-top: 4px solid #0047BB;
            border: 1px solid #f0f0f0;
        }}

        .card:hover {{
            transform: translateY(-3px);
            box-shadow: 0 6px 18px rgba(0, 0, 0, 0.08);
            border-color: #0047BB;
        }}

        .card-title {{
            color: #475569;
            font-size: 1.1rem;
            margin-bottom: 15px;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .card-value {{
            font-size: 2.2rem;
            font-weight: 800;
            color: #1e293b;
            margin: 10px 0;
        }}

        .card-unit {{
            color: #64748b;
            font-size: 0.9rem;
            margin-bottom: 5px;
        }}

        .card-desc {{
            color: #94a3b8;
            font-size: 0.9rem;
            margin-top: 8px;
            line-height: 1.5;
        }}

        /* 图表容器 */
        .chart-container {{
            background: white;
            border-radius: 10px;
            padding: 25px;
            margin-bottom: 30px;
            box-shadow: 0 3px 10px rgba(0, 0, 0, 0.04);
            border: 1px solid #f0f0f0;
        }}

        .chart-title {{
            color: #1a1a1a;
            margin-bottom: 20px;
            font-size: 1.4rem;
            font-weight: 600;
            border-left: 4px solid #0047BB;
            padding-left: 15px;
        }}

        .chart {{
            width: 100%;
            height: 500px;
        }}

        /* 分析区域 */
        .analysis-section {{
            background: white;
            border-radius: 10px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 3px 10px rgba(0, 0, 0, 0.04);
            border: 1px solid #f0f0f0;
        }}

        .section-title {{
            color: #1e293b;
            margin-bottom: 25px;
            font-size: 1.6rem;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .section-title::before {{
            content: '';
            width: 6px;
            height: 24px;
            background: #0047BB;
            border-radius: 3px;
        }}

        .analysis-content {{
            font-size: 1.05rem;
            color: #475569;
            line-height: 1.8;
        }}

        .analysis-content p {{
            margin-bottom: 15px;
        }}

        .analysis-content ul, .analysis-content ol {{
            margin: 15px 0 15px 25px;
        }}

        .analysis-content li {{
            margin-bottom: 8px;
        }}

        /* 表格样式 */
        .data-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        }}

        .data-table th {{
            background: #0047BB;
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
        }}

        .data-table td {{
            padding: 15px;
            border-bottom: 1px solid #e2e8f0;
        }}

        .data-table tr:nth-child(even) {{
            background: #f8fafc;
        }}

        .data-table tr:hover {{
            background: #f1f5f9;
        }}

        /* 总结区域 */
        .summary-section {{
            background: linear-gradient(135deg, #0047BB 0%, #003399 100%);
            border-radius: 12px;
            padding: 35px;
            margin-bottom: 30px;
            color: white;
            box-shadow: 0 5px 20px rgba(0, 71, 187, 0.15);
        }}

        .summary-title {{
            font-size: 1.8rem;
            margin-bottom: 25px;
            font-weight: 700;
        }}

        .summary-points {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .summary-point {{
            background: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 10px;
            backdrop-filter: blur(10px);
        }}

        .summary-point h4 {{
            font-size: 1.2rem;
            margin-bottom: 10px;
            color: #dbeafe;
        }}

        .summary-point p {{
            color: #e2e8f0;
            line-height: 1.6;
        }}

        .investment-advice {{
            background: rgba(255, 255, 255, 0.15);
            padding: 25px;
            border-radius: 10px;
            border-left: 5px solid #10b981;
        }}

        .investment-advice h4 {{
            font-size: 1.3rem;
            margin-bottom: 15px;
            color: #ffffff;
        }}

        /* 页脚 */
        .footer {{
            text-align: center;
            padding: 25px;
            color: #64748b;
            font-size: 0.9rem;
            border-top: 1px solid #e2e8f0;
            margin-top: 20px;
        }}

        /* 响应式设计 */
        @media (max-width: 768px) {{
            .card-grid {{
                grid-template-columns: 1fr;
            }}

            .chart {{
                height: 400px;
            }}

            .header h1 {{
                font-size: 2rem;
            }}

            .summary-points {{
                grid-template-columns: 1fr;
            }}
        }}

        /* 工具类 */
        .trend-up {{
            color: #10b981;
            font-weight: 600;
        }}

        .trend-down {{
            color: #ef4444;
            font-weight: 600;
        }}

        .trend-neutral {{
            color: #f59e0b;
            font-weight: 600;
        }}

        .highlight {{
            background: #fef3c7;
            padding: 2px 6px;
            border-radius: 4px;
            font-weight: 600;
        }}

        .badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
            margin-right: 8px;
        }}

        .badge-success {{
            background: #d1fae5;
            color: #065f46;
        }}

        .badge-warning {{
            background: #fef3c7;
            color: #92400e;
        }}

        .badge-danger {{
            background: #fee2e2;
            color: #991b1b;
        }}

        .badge-info {{
            background: #dbeafe;
            color: #1e40af;
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- 标题区域 -->
        <div class="header">
            <h1>🍎 苹果公司股价深度洞察报告</h1>
            <p class="subtitle">基于近100个交易日的多维度数据分析与可视化</p>
            <div class="date-range">分析周期: {date_range}</div>
        </div>

        <!-- 第一行卡片: 基础指标 -->
        <div class="card-grid">
            <div class="card">
                <div class="card-title">📅 总交易天数</div>
                <div class="card-value">{total_days}</div>
                <div class="card-unit">个交易日</div>
                <div class="card-desc">数据覆盖 {date_range_start} 至 {date_range_end}</div>
            </div>

            <div class="card">
                <div class="card-title">📈 YTD收益率</div>
                <div class="card-value">{ytd_return:+.2f}%</div>
                <div class="card-unit">年初至今涨跌幅</div>
                <div class="card-desc">起始: ${first_close:.2f} → 结束: ${last_close:.2f}</div>
            </div>

            <div class="card">
                <div class="card-title">📊 日均成交量</div>
                <div class="card-value">{avg_volume:,}</div>
                <div class="card-unit">股/日</div>
                <div class="card-desc">总成交量: {df['Volume'].sum():,} 股</div>
            </div>

            <div class="card">
                <div class="card-title">🎯 整体趋势</div>
                <div class="card-value" style="color: {trend_color};">{trend}</div>
                <div class="card-unit">价格方向</div>
                <div class="card-desc">累计涨跌幅: <span class="{ 'trend-up' if ytd_return > 0 else 'trend-down' }">{ytd_return:+.2f}%</span></div>
            </div>
        </div>

        <!-- 第二行卡片: 价格波动指标 -->
        <div class="card-grid">
            <div class="card">
                <div class="card-title">📈 区间最高价</div>
                <div class="card-value">${max_high:.2f}</div>
                <div class="card-unit">峰值价格</div>
                <div class="card-desc">发生于 {max_high_date}</div>
            </div>

            <div class="card">
                <div class="card-title">📉 区间最低价</div>
                <div class="card-value">${min_low:.2f}</div>
                <div class="card-unit">底部价格</div>
                <div class="card-desc">发生于 {min_low_date}</div>
            </div>

            <div class="card">
                <div class="card-title">📊 平均日内振幅</div>
                <div class="card-value">{avg_daily_amplitude:.2f}%</div>
                <div class="card-unit">每日波动率</div>
                <div class="card-desc">基于 (最高-最低)/前日收盘价计算</div>
            </div>

            <div class="card">
                <div class="card-title">⚖️ 涨跌天数</div>
                <div class="card-value">{up_days}:{down_days}</div>
                <div class="card-unit">上涨:下跌</div>
                <div class="card-desc">上涨{up_days}天, 下跌{down_days}天, 平盘{flat_days}天</div>
            </div>
        </div>

        <!-- K线图 + 成交量子图 -->
        <div class="chart-container">
            <h2 class="chart-title">📊 K线图与成交量分析</h2>
            <div id="candleChart" class="chart"></div>
        </div>

        <!-- 收盘价分布与波动分析图 -->
        <div class="chart-container">
            <h2 class="chart-title">📈 价格分布与波动分析</h2>
            <div id="distributionChart" class="chart"></div>
        </div>

        <!-- 数据深度分析 -->
        <div class="analysis-section">
            <h2 class="section-title">🔍 数据深度分析</h2>

            <div class="analysis-content">
                <h3>1. 趋势分析</h3>
                <p>
                    在分析周期内，苹果公司股价整体呈现 <span class="highlight">{trend}</span> 趋势，
                    累计收益率为 <span class="{ 'trend-up' if ytd_return > 0 else 'trend-down' }">{ytd_return:+.2f}%</span>。
                </p>

                <p>
                    <strong>近期表现对比:</strong><br>
                    • 最近10个交易日涨跌幅: <span class="{ 'trend-up' if last_10_return > 0 else 'trend-down' }">{last_10_return:+.2f}%</span><br>
                    • 前10个交易日涨跌幅: <span class="{ 'trend-up' if prev_10_return > 0 else 'trend-down' }">{prev_10_return:+.2f}%</span><br>
                    • 对比变化: {last_10_return - prev_10_return:+.2f}%
                </p>

                <p>
                    当前移动平均线状态:<br>
                    • MA5(5日): <span class="highlight">${current_ma5:.2f}</span><br>
                    • MA20(20日): <span class="highlight">${current_ma20:.2f}</span><br>
                    • 短期均线{ '高于' if current_ma5 > current_ma20 else '低于' }长期均线，显示{ '短期动量较强' if current_ma5 > current_ma20 else '短期动量偏弱' }。
                </p>

                <h3>2. 成交量洞察</h3>

                <table class="data-table">
                    <thead>
                        <tr>
                            <th>日期</th>
                            <th>成交量</th>
                            <th>当日涨跌幅</th>
                            <th>收盘价</th>
                            <th>市场信号</th>
                        </tr>
                    </thead>
                    <tbody>'''

# 添加成交量最大的3天数据到表格
for item in top3_table_data:
    return_pct = float(item['return_pct'].replace('%', ''))
    signal_class = 'trend-up' if return_pct > 0 else 'trend-down'
    signal_text = '放量上涨' if return_pct > 0 else '放量下跌'

    html += f'''
                        <tr>
                            <td>{item['date']}</td>
                            <td>{item['volume']}股</td>
                            <td class="{signal_class}">{item['return_pct']}</td>
                            <td>{item['close']}</td>
                            <td>{signal_text}</td>
                        </tr>'''

html += f'''
                    </tbody>
                </table>

                <p>
                    <strong>量价关系分析:</strong><br>
                    量价相关性系数为 <span class="highlight">{price_volume_corr:.3f}</span>，表明{price_volume_relation}。
                </p>

                <h3>3. 支撑与阻力分析</h3>
                <p>
                    基于近期价格走势，识别以下关键价位:
                </p>

                <table class="data-table">
                    <thead>
                        <tr>
                            <th>价位类型</th>
                            <th>价格水平</th>
                            <th>说明</th>
                            <th>强度</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><strong>近期支撑位</strong></td>
                            <td><span class="trend-up">${recent_low:.2f}</span></td>
                            <td>过去20个交易日最低点</td>
                            <td><span class="badge badge-success">强支撑</span></td>
                        </tr>
                        <tr>
                            <td><strong>近期阻力位</strong></td>
                            <td><span class="trend-down">${recent_high:.2f}</span></td>
                            <td>过去20个交易日最高点</td>
                            <td><span class="badge badge-warning">中等阻力</span></td>
                        </tr>
                        <tr>
                            <td><strong>MA5动态支撑</strong></td>
                            <td><span class="trend-up">${current_ma5:.2f}</span></td>
                            <td>5日移动平均线</td>
                            <td><span class="badge badge-info">短期支撑</span></td>
                        </tr>
                        <tr>
                            <td><strong>MA20动态支撑</strong></td>
                            <td><span class="trend-up">${current_ma20:.2f}</span></td>
                            <td>20日移动平均线</td>
                            <td><span class="badge badge-info">中期支撑</span></td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- 总结与观点 -->
        <div class="summary-section">
            <h2 class="summary-title">💡 核心观察与投资建议</h2>

            <div class="summary-points">
                <div class="summary-point">
                    <h4>🎯 观察一：趋势动量</h4>
                    <p>股价在{total_days}个交易日内累计上涨{ytd_return:.2f}%，整体呈现{trend}态势。近期{ '加速上涨' if last_10_return > prev_10_return else '上涨动能减弱' }。</p>
                </div>

                <div class="summary-point">
                    <h4>📊 观察二：量价配合</h4>
                    <p>成交量在关键交易日明显放大，最大单日成交达{top3_table_data[0]['volume']}股。量价相关性{price_volume_corr:.3f}，显示{price_volume_relation}。</p>
                </div>

                <div class="summary-point">
                    <h4>⚖️ 观察三：技术位置</h4>
                    <p>当前价格${last_close:.2f}位于近期区间${recent_low:.2f}-${recent_high:.2f}的{((last_close - recent_low)/(recent_high - recent_low)*100):.1f}%位置，接近MA5(${current_ma5:.2f})支撑。</p>
                </div>
            </div>

            <div class="investment-advice">
                <h4>📈 投资建议</h4>
                <p>
                    基于技术分析，建议关注 <strong>${current_ma5:.2f}</strong> (MA5) 和 <strong>${current_ma20:.2f}</strong> (MA20) 的关键支撑。
                    若股价能维持在MA20上方且成交量配合，则上升趋势有望延续。
                    下方重要支撑位于 <strong>${recent_low:.2f}</strong>，上方阻力关注 <strong>${recent_high:.2f}</strong>。
                </p>
            </div>
        </div>

        <!-- 页脚 -->
        <div class="footer">
            <p>报告生成时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')} • 数据来源: AAPL_100DAYS.CSV</p>
            <p>分析工具: Python + Pandas + Plotly • 本报告仅供分析研究使用，不构成投资建议</p>
        </div>
    </div>

    <script>
        // 图表数据
        const dates = {json.dumps(dates)};
        const opens = {json.dumps(opens)};
        const highs = {json.dumps(highs)};
        const lows = {json.dumps(lows)};
        const closes = {json.dumps(closes)};
        const volumes = {json.dumps(volumes)};
        const ma5Values = {json.dumps(ma5_values)};
        const ma20Values = {json.dumps(ma20_values)};
        const dailyAmplitudePct = {json.dumps(daily_amplitude_pct)};
        const volumeColors = {json.dumps(volume_colors)};

        // 1. K线图 + 成交量子图
        const candlestickTrace = {{
            x: dates,
            open: opens,
            high: highs,
            low: lows,
            close: closes,
            type: 'candlestick',
            name: 'K线图',
            increasing: {{ line: {{ color: '#ef4444' }}, fillcolor: '#ef4444' }},
            decreasing: {{ line: {{ color: '#10b981' }}, fillcolor: '#10b981' }},
            yaxis: 'y'
        }};

        const ma5Trace = {{
            x: dates,
            y: ma5Values,
            type: 'scatter',
            mode: 'lines',
            name: 'MA5 (5日移动平均)',
            line: {{ color: '#0047BB', width: 2 }},
            yaxis: 'y'
        }};

        const ma20Trace = {{
            x: dates,
            y: ma20Values,
            type: 'scatter',
            mode: 'lines',
            name: 'MA20 (20日移动平均)',
            line: {{ color: '#f59e0b', width: 2, dash: 'dash' }},
            yaxis: 'y'
        }};

        const volumeTrace = {{
            x: dates,
            y: volumes,
            type: 'bar',
            name: '成交量',
            marker: {{ color: volumeColors }},
            yaxis: 'y2'
        }};

        const candleLayout = {{
            title: {{
                text: '苹果公司股价K线图与成交量分析',
                font: {{ size: 18, family: 'Microsoft YaHei, sans-serif' }}
            }},
            xaxis: {{
                title: {{ text: '日期', font: {{ family: 'Microsoft YaHei, sans-serif' }} }},
                type: 'date',
                gridcolor: '#e2e8f0',
                rangeslider: {{ visible: false }}
            }},
            yaxis: {{
                title: {{ text: '价格 (美元)', font: {{ family: 'Microsoft YaHei, sans-serif' }} }},
                gridcolor: '#e2e8f0',
                domain: [0.3, 1]
            }},
            yaxis2: {{
                title: {{ text: '成交量 (股)', font: {{ family: 'Microsoft YaHei, sans-serif' }} }},
                gridcolor: '#e2e8f0',
                domain: [0, 0.25],
                anchor: 'x'
            }},
            plot_bgcolor: 'white',
            paper_bgcolor: 'white',
            hovermode: 'x unified',
            showlegend: true,
            legend: {{
                x: 0.02,
                y: 0.98,
                font: {{ family: 'Microsoft YaHei, sans-serif' }}
            }},
            margin: {{ l: 60, r: 30, t: 60, b: 60 }}
        }};

        Plotly.newPlot('candleChart', [candlestickTrace, ma5Trace, ma20Trace, volumeTrace], candleLayout, {{
            responsive: true,
            displayModeBar: true
        }});

        // 2. 收盘价分布与波动分析图
        // 直方图数据
        const histogramTrace = {{
            x: closes,
            type: 'histogram',
            name: '收盘价分布',
            nbinsx: 20,
            marker: {{
                color: '#0047BB',
                line: {{
                    color: '#003399',
                    width: 1
                }}
            }},
            opacity: 0.7,
            xaxis: 'x'
        }};

        // 波动分析图
        const amplitudeTrace = {{
            x: dates,
            y: dailyAmplitudePct,
            type: 'scatter',
            mode: 'markers+lines',
            name: '日内振幅 (%)',
            line: {{ color: '#ef4444', width: 1.5 }},
            marker: {{
                size: 6,
                color: dailyAmplitudePct.map(amp => amp > {high_volatility_threshold} ? '#ef4444' : '#94a3b8')
            }},
            xaxis: 'x2',
            yaxis: 'y2'
        }};

        // 添加高波动区域标注
        const highVolatilityAnnotations = [];
        const highVolatilityDays = {json.dumps([{'date': row['Date_Str'], 'amplitude': float(row['Daily_Amplitude_Pct']), 'close': float(row['Close'])} for _, row in top3_volatility.iterrows()])};

        highVolatilityDays.forEach(day => {{
            highVolatilityAnnotations.push({{
                x: day.date,
                y: day.amplitude,
                xref: 'x2',
                yref: 'y2',
                text: `振幅: ${{day.amplitude.toFixed(2)}}%`,
                showarrow: true,
                arrowhead: 2,
                arrowsize: 1,
                arrowwidth: 2,
                arrowcolor: '#ef4444',
                ax: 0,
                ay: -40,
                bgcolor: 'rgba(239, 68, 68, 0.1)',
                bordercolor: '#ef4444',
                borderwidth: 1,
                borderpad: 4,
                font: {{ size: 12, color: '#ef4444' }}
            }});
        }});

        const distributionLayout = {{
            title: {{
                text: '收盘价分布与日内波动分析',
                font: {{ size: 18, family: 'Microsoft YaHei, sans-serif' }}
            }},
            grid: {{
                rows: 1,
                columns: 2,
                pattern: 'independent'
            }},
            xaxis: {{
                title: {{ text: '收盘价 (美元)', font: {{ family: 'Microsoft YaHei, sans-serif' }} }},
                gridcolor: '#e2e8f0',
                domain: [0, 0.45]
            }},
            yaxis: {{
                title: {{ text: '频数', font: {{ family: 'Microsoft YaHei, sans-serif' }} }},
                gridcolor: '#e2e8f0'
            }},
            xaxis2: {{
                title: {{ text: '日期', font: {{ family: 'Microsoft YaHei, sans-serif' }} }},
                gridcolor: '#e2e8f0',
                domain: [0.55, 1]
            }},
            yaxis2: {{
                title: {{ text: '日内振幅 (%)', font: {{ family: 'Microsoft YaHei, sans-serif' }} }},
                gridcolor: '#e2e8f0',
                side: 'right'
            }},
            plot_bgcolor: 'white',
            paper_bgcolor: 'white',
            showlegend: true,
            legend: {{
                x: 0.5,
                y: 1.1,
                xanchor: 'center',
                font: {{ family: 'Microsoft YaHei, sans-serif' }}
            }},
            annotations: highVolatilityAnnotations,
            margin: {{ l: 60, r: 60, t: 80, b: 60 }}
        }};

        Plotly.newPlot('distributionChart', [histogramTrace, amplitudeTrace], distributionLayout, {{
            responsive: true,
            displayModeBar: true
        }});

        // 窗口调整大小
        window.addEventListener('resize', function() {{
            Plotly.Plots.resize('candleChart');
            Plotly.Plots.resize('distributionChart');
        }});
    </script>
</body>
</html>'''

# 写入文件
output_filename = '苹果公司股价洞察.html'
with open(output_filename, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"✓ 报告已生成: {output_filename}")
print(f"✓ 文件大小: {len(html):,} 字符")
print("✓ 指标统计:")
print(f"  总交易天数: {total_days}")
print(f"  YTD收益率: {ytd_return:.2f}%")
print(f"  日均成交量: {avg_volume:,}")
print(f"  区间最高价: ${max_high:.2f} ({max_high_date})")
print(f"  区间最低价: ${min_low:.2f} ({min_low_date})")
print(f"  平均日内振幅: {avg_daily_amplitude:.2f}%")
print(f"  上涨天数: {up_days}, 下跌天数: {down_days}")
print(f"  当前MA5: ${current_ma5:.2f}, MA20: ${current_ma20:.2f}")