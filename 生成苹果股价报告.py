#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np

# 读取数据
df = pd.read_csv('AAPL_100DAYS.CSV', encoding='utf-8')
df['Date'] = pd.to_datetime(df['Date'])

# 计算指标
total_days = len(df)
date_range = f"{df['Date'].min().strftime('%Y-%m-%d')} - {df['Date'].max().strftime('%Y-%m-%d')}"
date_range_formatted = f"{df['Date'].min().strftime('%Y年%m月%d日')} - {df['Date'].max().strftime('%Y年%m月%d日')}"
first_close = df.iloc[0]['Close']
last_close = df.iloc[-1]['Close']
ytd_return = (last_close - first_close) / first_close * 100
avg_volume = int(df['Volume'].mean())
max_volume = df['Volume'].max()
max_volume_date = df.loc[df['Volume'].idxmax(), 'Date'].strftime('%Y年%m月%d日')
min_close = df['Close'].min()
max_close = df['Close'].max()
price_range = max_close - min_close

# 计算MA5
df['MA5'] = df['Close'].rolling(window=5).mean()

# 准备JavaScript数据
dates_js = df['Date'].dt.strftime('%Y-%m-%d').tolist()
close_js = df['Close'].tolist()
ma5_js = df['MA5'].tolist()
volume_js = df['Volume'].tolist()

# 生成HTML
html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>苹果公司股价分析报告</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'PingFang SC', 'Microsoft YaHei', 'Segoe UI', sans-serif;
        }}
        body {{
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            color: #333;
            line-height: 1.6;
            padding: 20px;
            min-height: 100vh;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        header {{
            text-align: center;
            margin-bottom: 30px;
            padding: 25px;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
            border-bottom: 5px solid #007aff;
        }}
        h1 {{
            color: #1d1d1f;
            font-size: 2.5rem;
            margin-bottom: 10px;
            font-weight: 600;
        }}
        .subtitle {{
            color: #86868b;
            font-size: 1.1rem;
        }}
        .cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .card {{
            background: white;
            border-radius: 16px;
            padding: 25px;
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.06);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            border-left: 5px solid #007aff;
        }}
        .card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 15px 30px rgba(0, 0, 0, 0.1);
        }}
        .card h3 {{
            color: #1d1d1f;
            font-size: 1.2rem;
            margin-bottom: 12px;
            font-weight: 500;
        }}
        .card .value {{
            font-size: 2.2rem;
            font-weight: 700;
            color: #007aff;
            margin: 12px 0;
        }}
        .card .unit {{
            color: #86868b;
            font-size: 0.9rem;
            margin-bottom: 5px;
        }}
        .card .desc {{
            color: #86868b;
            font-size: 0.9rem;
            margin-top: 8px;
        }}
        .chart-container {{
            background: white;
            border-radius: 16px;
            padding: 25px;
            margin-bottom: 30px;
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.06);
        }}
        .chart-title {{
            color: #1d1d1f;
            margin-bottom: 20px;
            font-size: 1.5rem;
            font-weight: 500;
        }}
        .chart {{
            width: 100%;
            height: 500px;
        }}
        .summary {{
            background: white;
            border-radius: 16px;
            padding: 30px;
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.06);
            margin-bottom: 30px;
        }}
        .summary h2 {{
            color: #1d1d1f;
            margin-bottom: 20px;
            font-size: 1.8rem;
            font-weight: 500;
            border-left: 4px solid #007aff;
            padding-left: 15px;
        }}
        .summary p {{
            font-size: 1.1rem;
            color: #515154;
            line-height: 1.8;
            margin-bottom: 15px;
            text-align: justify;
        }}
        .summary ul {{
            font-size: 1.1rem;
            color: #515154;
            line-height: 1.8;
            margin: 15px 0 15px 20px;
        }}
        footer {{
            text-align: center;
            padding: 20px;
            color: #86868b;
            font-size: 0.9rem;
            border-top: 1px solid #e5e5e7;
            margin-top: 20px;
        }}
        @media (max-width: 768px) {{
            .cards {{
                grid-template-columns: 1fr;
            }}
            .chart {{
                height: 400px;
            }}
            h1 {{
                font-size: 2rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🍎 苹果公司股价分析报告</h1>
            <p class="subtitle">基于近100个交易日数据的综合分析 ({date_range_formatted})</p>
        </header>

        <div class="cards">
            <div class="card">
                <h3>分析周期</h3>
                <div class="value">{total_days}</div>
                <div class="unit">个交易日</div>
                <div class="desc">数据范围: {date_range}</div>
            </div>
            <div class="card">
                <h3>YTD收益率</h3>
                <div class="value">{ytd_return:+.2f}%</div>
                <div class="unit">年初至今涨跌幅</div>
                <div class="desc">起始: ${first_close:.2f} → 结束: ${last_close:.2f}</div>
            </div>
            <div class="card">
                <h3>日均成交量</h3>
                <div class="value">{avg_volume:,}</div>
                <div class="unit">股/日</div>
                <div class="desc">总成交量: {df['Volume'].sum():,} 股</div>
            </div>
            <div class="card">
                <h3>价格区间</h3>
                <div class="value">${price_range:.2f}</div>
                <div class="unit">最高-最低价差</div>
                <div class="desc">最低: ${min_close:.2f}<br>最高: ${max_close:.2f}</div>
            </div>
        </div>

        <div class="chart-container">
            <h2 class="chart-title">收盘价走势与5日移动平均线</h2>
            <div id="priceChart" class="chart"></div>
        </div>

        <div class="chart-container">
            <h2 class="chart-title">每日成交量分析</h2>
            <div id="volumeChart" class="chart"></div>
        </div>

        <div class="summary">
            <h2>📈 数据洞察与总结</h2>
            <p>
                在最近100个交易日中（{date_range_formatted}），苹果公司（AAPL）股票整体表现<strong>{'积极' if ytd_return > 0 else '疲软'}</strong>，
                累计收益率为<strong>{ytd_return:+.2f}%</strong>。股价从期初的<strong>${first_close:.2f}</strong>上涨至期末的<strong>${last_close:.2f}</strong>，
                期间最高达到<strong>${max_close:.2f}</strong>，最低跌至<strong>${min_close:.2f}</strong>，价格波动幅度为<strong>${price_range:.2f}</strong>。
            </p>
            <p>
                交易活跃度方面，日均成交量为<strong>{avg_volume:,}</strong>股，总成交量达<strong>{df['Volume'].sum():,}</strong>股。
                成交量峰值出现在<strong>{max_volume_date}</strong>，当日成交<strong>{max_volume:,}</strong>股，显示出显著的市场关注度。
            </p>
            <p>
                <strong>关键观察点：</strong>
            </p>
            <ul>
                <li>5日移动平均线（MA5）反映了短期价格趋势，目前{'' if df['MA5'].iloc[-1] > df['MA5'].iloc[-6] else '未'}呈现上升态势</li>
                <li>股价在${min_close:.2f}至${max_close:.2f}区间内波动，振幅约为{(price_range/first_close*100):.1f}%</li>
                <li>成交量在特定日期（如{max_volume_date}）出现异常放大，可能与公司公告或市场事件相关</li>
                <li>整体成交活跃度维持在较高水平，表明市场对苹果股票持续关注</li>
            </ul>
            <p>
                <strong>投资建议参考：</strong>本报告仅为历史数据分析，不构成投资建议。投资者应结合公司基本面、宏观经济环境及市场情绪等多方面因素进行综合判断。
            </p>
        </div>

        <footer>
            <p>报告生成时间：{pd.Timestamp.now().strftime('%Y年%m月%d日 %H:%M:%S')} • 数据来源：AAPL_100DAYS.CSV</p>
            <p>分析工具：Python + Pandas + Plotly • 本报告仅供分析研究使用</p>
        </footer>
    </div>

    <script>
        // 数据准备
        const dates = {dates_js};
        const closePrices = {close_js};
        const ma5Values = {ma5_js};
        const volumes = {volume_js};

        // 价格图表
        const priceTrace1 = {{
            x: dates,
            y: closePrices,
            type: 'scatter',
            mode: 'lines',
            name: '收盘价',
            line: {{ color: '#007aff', width: 3 }}
        }};
        const priceTrace2 = {{
            x: dates,
            y: ma5Values,
            type: 'scatter',
            mode: 'lines',
            name: 'MA5 (5日移动平均)',
            line: {{ color: '#ff3b30', width: 2.5, dash: 'dash' }}
        }};
        const priceLayout = {{
            title: {{ text: '苹果公司收盘价走势分析', font: {{ size: 18, family: 'Microsoft YaHei' }} }},
            xaxis: {{
                title: {{ text: '日期', font: {{ family: 'Microsoft YaHei' }} }},
                gridcolor: '#f0f0f0',
                tickformat: '%Y-%m-%d'
            }},
            yaxis: {{
                title: {{ text: '价格 (美元)', font: {{ family: 'Microsoft YaHei' }} }},
                gridcolor: '#f0f0f0'
            }},
            plot_bgcolor: 'white',
            paper_bgcolor: 'white',
            hovermode: 'x unified',
            showlegend: true,
            legend: {{
                x: 0.02,
                y: 0.98,
                font: {{ family: 'Microsoft YaHei' }}
            }},
            margin: {{ l: 60, r: 30, t: 60, b: 60 }}
        }};
        Plotly.newPlot('priceChart', [priceTrace1, priceTrace2], priceLayout, {{ responsive: true }});

        // 成交量图表
        const volumeTrace = {{
            x: dates,
            y: volumes,
            type: 'bar',
            name: '成交量',
            marker: {{ color: '#34c759' }}
        }};
        const volumeLayout = {{
            title: {{ text: '苹果公司每日成交量分析', font: {{ size: 18, family: 'Microsoft YaHei' }} }},
            xaxis: {{
                title: {{ text: '日期', font: {{ family: 'Microsoft YaHei' }} }},
                gridcolor: '#f0f0f0',
                tickformat: '%Y-%m-%d'
            }},
            yaxis: {{
                title: {{ text: '成交量 (股)', font: {{ family: 'Microsoft YaHei' }} }},
                gridcolor: '#f0f0f0'
            }},
            plot_bgcolor: 'white',
            paper_bgcolor: 'white',
            hovermode: 'x unified',
            margin: {{ l: 60, r: 30, t: 60, b: 60 }}
        }};
        Plotly.newPlot('volumeChart', [volumeTrace], volumeLayout, {{ responsive: true }});

        // 响应式调整
        window.addEventListener('resize', function() {{
            Plotly.Plots.resize('priceChart');
            Plotly.Plots.resize('volumeChart');
        }});
    </script>
</body>
</html>'''

# 写入文件
output_file = '苹果公司股价分析.html'
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"报告已生成: {output_file}")
print("关键指标:")
print(f"  总天数: {total_days}")
print(f"  日期范围: {date_range}")
print(f"  YTD收益率: {ytd_return:.2f}%")
print(f"  日均成交量: {avg_volume:,}")