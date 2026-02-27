#!/usr/bin/env python3
import pandas as pd
import numpy as np
import os

# Read CSV
df = pd.read_csv('AAPL_100DAYS.CSV')
df['Date'] = pd.to_datetime(df['Date'])

# Calculate metrics
total_days = len(df)
date_range = f"{df['Date'].min().strftime('%Y-%m-%d')} - {df['Date'].max().strftime('%Y-%m-%d')}"
first_close = df.iloc[0]['Close']
last_close = df.iloc[-1]['Close']
ytd_return = (last_close - first_close) / first_close * 100
avg_volume = int(df['Volume'].mean())

# Calculate MA5
df['MA5'] = df['Close'].rolling(window=5).mean()

# Prepare data for JavaScript
dates_js = df['Date'].dt.strftime('%Y-%m-%d').tolist()
close_js = df['Close'].tolist()
ma5_js = df['MA5'].tolist()
volume_js = df['Volume'].tolist()

# Generate HTML
html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AAPL 100-Day Stock Analysis Report</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', system-ui, sans-serif;
        }}
        body {{
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
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
            padding: 20px;
            background: rgba(255, 255, 255, 0.9);
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
        }}
        h1 {{
            color: #2c3e50;
            font-size: 2.5rem;
            margin-bottom: 10px;
        }}
        .subtitle {{
            color: #7f8c8d;
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
            border-left: 5px solid #3498db;
        }}
        .card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 15px 30px rgba(0, 0, 0, 0.1);
        }}
        .card h3 {{
            color: #2c3e50;
            font-size: 1.2rem;
            margin-bottom: 10px;
        }}
        .card .value {{
            font-size: 2.2rem;
            font-weight: 700;
            color: #2980b9;
            margin: 10px 0;
        }}
        .card .unit {{
            color: #7f8c8d;
            font-size: 0.9rem;
        }}
        .card .desc {{
            color: #95a5a6;
            font-size: 0.9rem;
        }}
        .chart-container {{
            background: white;
            border-radius: 16px;
            padding: 25px;
            margin-bottom: 30px;
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.06);
        }}
        .chart-title {{
            color: #2c3e50;
            margin-bottom: 20px;
            font-size: 1.5rem;
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
            color: #2c3e50;
            margin-bottom: 15px;
            font-size: 1.8rem;
        }}
        .summary p {{
            font-size: 1.1rem;
            color: #555;
            line-height: 1.8;
        }}
        footer {{
            text-align: center;
            padding: 20px;
            color: #7f8c8d;
            font-size: 0.9rem;
        }}
        @media (max-width: 768px) {{
            .cards {{
                grid-template-columns: 1fr;
            }}
            .chart {{
                height: 400px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📈 AAPL 100-Day Stock Analysis</h1>
            <p class="subtitle">Comprehensive report on Apple Inc. (AAPL) stock performance over 100 trading days</p>
        </header>

        <div class="cards">
            <div class="card">
                <h3>Total Days</h3>
                <div class="value">{total_days}</div>
                <div class="unit">trading days</div>
                <div class="desc">Period: {date_range}</div>
            </div>
            <div class="card">
                <h3>Date Range</h3>
                <div class="value">{df['Date'].min().strftime('%b %d, %Y')}</div>
                <div class="unit">to</div>
                <div class="value">{df['Date'].max().strftime('%b %d, %Y')}</div>
                <div class="desc">100 consecutive trading days</div>
            </div>
            <div class="card">
                <h3>YTD Return</h3>
                <div class="value">{ytd_return:.2f}%</div>
                <div class="unit">since first day</div>
                <div class="desc">First: ${first_close:.2f} → Last: ${last_close:.2f}</div>
            </div>
            <div class="card">
                <h3>Avg Daily Volume</h3>
                <div class="value">{avg_volume:,}</div>
                <div class="unit">shares per day</div>
                <div class="desc">Total volume: {df['Volume'].sum():,} shares</div>
            </div>
        </div>

        <div class="chart-container">
            <h2 class="chart-title">Closing Price with 5-Day Moving Average</h2>
            <div id="priceChart" class="chart"></div>
        </div>

        <div class="chart-container">
            <h2 class="chart-title">Daily Trading Volume</h2>
            <div id="volumeChart" class="chart"></div>
        </div>

        <div class="summary">
            <h2>📊 Summary & Insights</h2>
            <p>
                Apple's stock over the 100-day period from {df['Date'].min().strftime('%B %d, %Y')} to {df['Date'].max().strftime('%B %d, %Y')}
                showed an overall <strong>{'positive' if ytd_return > 0 else 'negative'}</strong> trend with a total return of <strong>{ytd_return:.2f}%</strong>.
                The stock reached its lowest closing price of <strong>${df['Close'].min():.2f}</strong> and highest closing price of <strong>${df['Close'].max():.2f}</strong>,
                representing a range of <strong>${df['Close'].max() - df['Close'].min():.2f}</strong>.
            </p>
            <p>
                Trading activity averaged <strong>{avg_volume:,}</strong> shares per day, with peak volume reaching <strong>{df['Volume'].max():,}</strong> shares
                on {df.loc[df['Volume'].idxmax(), 'Date'].strftime('%B %d, %Y')}. The 5-day moving average (MA5) shows short-term momentum,
                {'' if df['MA5'].iloc[-1] > df['MA5'].iloc[-6] else 'not '}currently trending upward compared to five days prior.
            </p>
            <p>
                This report provides a snapshot of AAPL's recent market performance. Investors should consider this alongside broader market
                conditions and company fundamentals for informed decision-making.
            </p>
        </div>

        <footer>
            <p>Generated on {pd.Timestamp.now().strftime('%B %d, %Y %H:%M:%S')} • Data source: AAPL_100DAYS.CSV</p>
            <p>Report generated with Python & Plotly • For educational purposes only</p>
        </footer>
    </div>

    <script>
        // Data from Python
        const dates = {dates_js};
        const closePrices = {close_js};
        const ma5Values = {ma5_js};
        const volumes = {volume_js};

        // Price Chart
        const priceTrace1 = {{
            x: dates,
            y: closePrices,
            type: 'scatter',
            mode: 'lines',
            name: 'Close Price',
            line: {{ color: '#3498db', width: 3 }}
        }};
        const priceTrace2 = {{
            x: dates,
            y: ma5Values,
            type: 'scatter',
            mode: 'lines',
            name: 'MA5',
            line: {{ color: '#e74c3c', width: 2.5, dash: 'dash' }}
        }};
        const priceLayout = {{
            title: {{ text: 'AAPL Closing Price Trend', font: {{ size: 18 }} }},
            xaxis: {{ title: 'Date', gridcolor: '#f0f0f0' }},
            yaxis: {{ title: 'Price (USD)', gridcolor: '#f0f0f0' }},
            plot_bgcolor: 'white',
            paper_bgcolor: 'white',
            hovermode: 'x unified',
            showlegend: true,
            legend: {{ x: 0.02, y: 0.98 }},
            margin: {{ l: 60, r: 30, t: 60, b: 60 }}
        }};
        Plotly.newPlot('priceChart', [priceTrace1, priceTrace2], priceLayout, {{ responsive: true }});

        // Volume Chart
        const volumeTrace = {{
            x: dates,
            y: volumes,
            type: 'bar',
            name: 'Volume',
            marker: {{ color: '#2ecc71' }}
        }};
        const volumeLayout = {{
            title: {{ text: 'AAPL Daily Trading Volume', font: {{ size: 18 }} }},
            xaxis: {{ title: 'Date', gridcolor: '#f0f0f0' }},
            yaxis: {{ title: 'Volume (Shares)', gridcolor: '#f0f0f0' }},
            plot_bgcolor: 'white',
            paper_bgcolor: 'white',
            hovermode: 'x unified',
            margin: {{ l: 60, r: 30, t: 60, b: 60 }}
        }};
        Plotly.newPlot('volumeChart', [volumeTrace], volumeLayout, {{ responsive: true }});

        // Handle window resize
        window.addEventListener('resize', function() {{
            Plotly.Plots.resize('priceChart');
            Plotly.Plots.resize('volumeChart');
        }});
    </script>
</body>
</html>'''

# Write to file
with open('AAPL_report.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"Report generated: AAPL_report.html")
print(f"Total days: {total_days}")
print(f"Date range: {date_range}")
print(f"YTD return: {ytd_return:.2f}%")
print(f"Avg volume: {avg_volume:,}")