#!/usr/bin/env python3
"""
美股大盘监控看板生成器
使用Python + Pandas + Plotly生成交互式HTML看板
作者: DeepSeek + Claude 协作
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.offline as pyo
from datetime import datetime
import os

print("📊 美股大盘监控看板生成器")
print("=" * 60)

# ============================================================================
# 第一部分：DeepSeek - 计算YTD、YOY指标 (使用pandas)
# ============================================================================

def load_and_prepare_data():
    """加载并准备数据"""
    print("1. 加载数据...")

    # 加载股票数据
    stocks_df = pd.read_csv('stocks_100days.csv')
    stocks_df['date'] = pd.to_datetime(stocks_df['date'])

    # 加载SPY基准数据
    spy_df = pd.read_csv('SPY_benchmark.csv')
    spy_df['date'] = pd.to_datetime(spy_df['date'])

    print(f"   股票数据: {len(stocks_df)} 行, {stocks_df['symbol'].nunique()} 只股票")
    print(f"   SPY基准数据: {len(spy_df)} 行")
    print(f"   时间范围: {stocks_df['date'].min().date()} 至 {stocks_df['date'].max().date()}")

    return stocks_df, spy_df

def calculate_ytd_returns(df, current_year=2026):
    """计算YTD收益率"""
    print(f"2. 计算YTD收益率 (基准年份: {current_year})...")

    ytd_results = {}

    for symbol in df['symbol'].unique():
        symbol_data = df[df['symbol'] == symbol].sort_values('date')

        # 获取当年数据
        year_data = symbol_data[symbol_data['date'].dt.year == current_year]

        if len(year_data) == 0:
            print(f"   {symbol}: 无{current_year}年数据")
            ytd_results[symbol] = None
            continue

        # 当年第一个交易日和最新交易日
        first_trade = year_data.iloc[0]
        latest_trade = year_data.iloc[-1]

        # 计算YTD收益率
        ytd_return = (latest_trade['close'] - first_trade['close']) / first_trade['close']

        ytd_results[symbol] = {
            'ytd_return': ytd_return,
            'start_date': first_trade['date'],
            'start_price': first_trade['close'],
            'end_date': latest_trade['date'],
            'end_price': latest_trade['close'],
            'days_count': len(year_data)
        }

        print(f"   {symbol}: YTD = {ytd_return:.2%} ({first_trade['date'].date()} → {latest_trade['date'].date()})")

    return ytd_results

def calculate_mtd_returns(df, current_year=2026, current_month=2):
    """计算MTD（本月至今）收益率"""
    print(f"3. 计算MTD收益率 ({current_year}年{current_month}月)...")

    mtd_results = {}

    for symbol in df['symbol'].unique():
        symbol_data = df[df['symbol'] == symbol].sort_values('date')

        # 获取当月数据
        month_data = symbol_data[
            (symbol_data['date'].dt.year == current_year) &
            (symbol_data['date'].dt.month == current_month)
        ]

        if len(month_data) == 0:
            print(f"   {symbol}: 无{current_year}年{current_month}月数据")
            mtd_results[symbol] = None
            continue

        # 当月第一个交易日和最新交易日
        first_trade = month_data.iloc[0]
        latest_trade = month_data.iloc[-1]

        # 计算MTD收益率
        mtd_return = (latest_trade['close'] - first_trade['close']) / first_trade['close']

        mtd_results[symbol] = {
            'mtd_return': mtd_return,
            'start_date': first_trade['date'],
            'start_price': first_trade['close'],
            'end_date': latest_trade['date'],
            'end_price': latest_trade['close'],
            'days_count': len(month_data)
        }

        print(f"   {symbol}: MTD = {mtd_return:.2%} ({first_trade['date'].date()} → {latest_trade['date'].date()})")

    return mtd_results

def calculate_yoy_comparison(df):
    """计算YOY（同比）对比"""
    print("4. 计算YOY同比对比...")

    # 提取年份和月份
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['month_name'] = df['date'].dt.strftime('%b')  # 月份缩写

    yoy_data = {}

    for symbol in df['symbol'].unique():
        symbol_data = df[df['symbol'] == symbol]

        # 计算月度平均收盘价
        monthly_avg = symbol_data.groupby(['year', 'month', 'month_name'])['close'].agg(['mean', 'std', 'count']).reset_index()
        monthly_avg.columns = ['year', 'month', 'month_name', 'avg_close', 'std_close', 'trade_days']

        # 创建透视表以便对比
        pivot_table = pd.pivot_table(
            monthly_avg,
            values='avg_close',
            index=['month', 'month_name'],
            columns='year',
            aggfunc='mean'
        ).reset_index()

        # 计算同比变化（如果有两年数据）
        years = [col for col in pivot_table.columns if isinstance(col, int)]
        if len(years) >= 2:
            latest_year = max(years)
            prev_year = min(years)

            if latest_year in pivot_table.columns and prev_year in pivot_table.columns:
                pivot_table[f'yoy_change'] = (
                    (pivot_table[latest_year] - pivot_table[prev_year]) / pivot_table[prev_year]
                )
                pivot_table[f'yoy_change_pct'] = pivot_table[f'yoy_change'] * 100

                print(f"   {symbol}: 可对比年份 {prev_year} → {latest_year}")

        yoy_data[symbol] = {
            'monthly_data': monthly_avg,
            'pivot_table': pivot_table,
            'available_years': years
        }

    return yoy_data

def calculate_volume_distribution(df, period='1M'):
    """计算成交量分布"""
    print(f"5. 计算成交量分布 (周期: {period})...")

    # 确定时间范围
    end_date = df['date'].max()

    if period == '1M':
        start_date = end_date - pd.DateOffset(months=1)
    elif period == '3M':
        start_date = end_date - pd.DateOffset(months=3)
    elif period == 'YTD':
        start_date = pd.Timestamp(f'{end_date.year}-01-01')
    else:  # ALL
        start_date = df['date'].min()

    # 筛选周期内数据
    period_data = df[df['date'] >= start_date]

    # 按股票汇总成交量
    volume_by_stock = period_data.groupby('symbol')['volume'].agg(['sum', 'mean', 'count']).reset_index()
    volume_by_stock.columns = ['symbol', 'total_volume', 'avg_daily_volume', 'trade_days']

    # 计算占比
    total_volume = volume_by_stock['total_volume'].sum()
    volume_by_stock['percentage'] = volume_by_stock['total_volume'] / total_volume * 100
    volume_by_stock['percentage_formatted'] = volume_by_stock['percentage'].apply(lambda x: f"{x:.1f}%")

    print(f"   总成交量: {total_volume:,.0f} 股")
    for _, row in volume_by_stock.iterrows():
        print(f"   {row['symbol']}: {row['percentage']:.1f}% ({row['total_volume']:,.0f} 股)")

    return volume_by_stock, period, start_date, end_date

def calculate_key_metrics(stocks_df, spy_df):
    """计算关键指标"""
    print("6. 计算关键指标...")

    # 合并所有数据
    all_data = pd.concat([stocks_df, spy_df], ignore_index=True)

    # 计算日收益率
    all_data['daily_return'] = all_data.groupby('symbol')['close'].pct_change()

    # 计算波动率（20日年化）
    volatility_data = {}
    for symbol in all_data['symbol'].unique():
        symbol_data = all_data[all_data['symbol'] == symbol].sort_values('date')
        returns = symbol_data['daily_return'].dropna()

        if len(returns) >= 20:
            # 年化波动率 = 日收益率标准差 * √252
            daily_vol = returns.std()
            annual_vol = daily_vol * np.sqrt(252)

            # 计算最大回撤
            cumulative = (1 + returns).cumprod()
            running_max = cumulative.expanding().max()
            drawdown = (cumulative - running_max) / running_max
            max_drawdown = drawdown.min()

            volatility_data[symbol] = {
                'daily_volatility': daily_vol,
                'annual_volatility': annual_vol,
                'max_drawdown': max_drawdown,
                'sharpe_ratio': returns.mean() / daily_vol if daily_vol > 0 else 0
            }

    # 计算相对SPY表现（超额收益）
    spy_returns = all_data[all_data['symbol'] == 'SPY'].set_index('date')['daily_return']

    excess_returns = {}
    for symbol in stocks_df['symbol'].unique():
        if symbol != 'SPY':
            stock_returns = all_data[all_data['symbol'] == symbol].set_index('date')['daily_return']
            # 对齐日期
            common_dates = spy_returns.index.intersection(stock_returns.index)
            if len(common_dates) > 0:
                excess = stock_returns.loc[common_dates] - spy_returns.loc[common_dates]
                cumulative_excess = (1 + excess).cumprod() - 1

                excess_returns[symbol] = {
                    'excess_mean': excess.mean(),
                    'excess_std': excess.std(),
                    'cumulative_excess': cumulative_excess.iloc[-1] if len(cumulative_excess) > 0 else 0
                }

    return {
        'volatility': volatility_data,
        'excess_returns': excess_returns,
        'all_data': all_data
    }

# ============================================================================
# 第二部分：Claude - 基于计算结果生成Plotly图表
# ============================================================================

def create_spy_ytd_chart(spy_df, ytd_results):
    """创建大盘指数走势图（SPY YTD）"""
    print("创建大盘指数走势图...")

    # 准备SPY的YTD数据
    spy_ytd_data = spy_df[spy_df['date'].dt.year == 2026].sort_values('date')

    # 计算YTD收益率序列
    if len(spy_ytd_data) > 0:
        first_close = spy_ytd_data.iloc[0]['close']
        spy_ytd_data['ytd_return'] = (spy_ytd_data['close'] - first_close) / first_close * 100

    # 创建图表
    fig = go.Figure()

    # 添加收盘价线
    fig.add_trace(go.Scatter(
        x=spy_ytd_data['date'],
        y=spy_ytd_data['close'],
        mode='lines',
        name='S&P 500 (SPY)',
        line=dict(color='#1f77b4', width=3),
        hovertemplate='日期: %{x|%Y-%m-%d}<br>收盘价: $%{y:.2f}<extra></extra>'
    ))

    # 添加20日移动平均线
    if len(spy_ytd_data) >= 20:
        spy_ytd_data['MA20'] = spy_ytd_data['close'].rolling(window=20).mean()
        fig.add_trace(go.Scatter(
            x=spy_ytd_data['date'],
            y=spy_ytd_data['MA20'],
            mode='lines',
            name='20日移动平均',
            line=dict(color='#ff7f0e', width=2, dash='dash'),
            hovertemplate='日期: %{x|%Y-%m-%d}<br>MA20: $%{y:.2f}<extra></extra>'
        ))

    # 添加YTD收益率作为副y轴
    if 'ytd_return' in spy_ytd_data.columns:
        fig.add_trace(go.Scatter(
            x=spy_ytd_data['date'],
            y=spy_ytd_data['ytd_return'],
            mode='lines',
            name='YTD收益率',
            line=dict(color='#2ca02c', width=2),
            yaxis='y2',
            hovertemplate='日期: %{x|%Y-%m-%d}<br>YTD: %{y:.2f}%<extra></extra>'
        ))

    # 更新布局
    ytd_return = ytd_results.get('SPY', {}).get('ytd_return', 0) * 100 if ytd_results.get('SPY') else 0

    fig.update_layout(
        title=dict(
            text=f'S&P 500指数YTD走势 (YTD: {ytd_return:+.2f}%)',
            font=dict(size=20, color='#1f77b4')
        ),
        xaxis=dict(
            title='日期',
            gridcolor='#f0f0f0',
            showgrid=True
        ),
        yaxis=dict(
            title='价格 ($)',
            gridcolor='#f0f0f0',
            showgrid=True,
            side='left'
        ),
        yaxis2=dict(
            title='YTD收益率 (%)',
            overlaying='y',
            side='right',
            gridcolor='#f0f0f0',
            showgrid=False
        ),
        hovermode='x unified',
        plot_bgcolor='white',
        height=500,
        showlegend=True,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        )
    )

    return fig

def create_stocks_matrix_chart(stocks_df, spy_df, ytd_results, mtd_results, metrics):
    """创建个股表现矩阵图"""
    print("创建个股表现矩阵图...")

    # 创建子图：2行2列
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('NVDA (英伟达)', 'AAPL (苹果)', 'CRM (Salesforce)', 'IBM'),
        vertical_spacing=0.15,
        horizontal_spacing=0.1
    )

    # 颜色方案
    colors = {
        'NVDA': '#2ca02c',  # 绿色
        'AAPL': '#1f77b4',  # 蓝色
        'CRM': '#ff7f0e',   # 橙色
        'IBM': '#9467bd',   # 紫色
        'SPY': '#7f7f7f'    # 灰色
    }

    # 为每只股票创建图表
    stocks = ['NVDA', 'AAPL', 'CRM', 'IBM']
    positions = [(1, 1), (1, 2), (2, 1), (2, 2)]

    for i, symbol in enumerate(stocks):
        row, col = positions[i]

        # 获取股票数据
        stock_data = stocks_df[stocks_df['symbol'] == symbol].sort_values('date')

        # 添加股票价格线
        fig.add_trace(
            go.Scatter(
                x=stock_data['date'],
                y=stock_data['close'],
                mode='lines',
                name=symbol,
                line=dict(color=colors[symbol], width=2),
                hovertemplate=f'{symbol}<br>日期: %{{x|%Y-%m-%d}}<br>收盘价: $%{{y:.2f}}<extra></extra>',
                showlegend=False
            ),
            row=row, col=col
        )

        # 添加SPY基准线（浅色）
        spy_data = spy_df.sort_values('date')
        # 标准化到相同起始点便于比较
        spy_normalized = spy_data.copy()
        stock_start_price = stock_data.iloc[0]['close']
        spy_start_price = spy_data.iloc[0]['close']
        spy_normalized['close_normalized'] = spy_data['close'] * (stock_start_price / spy_start_price)

        fig.add_trace(
            go.Scatter(
                x=spy_normalized['date'],
                y=spy_normalized['close_normalized'],
                mode='lines',
                name='SPY (基准)',
                line=dict(color='#7f7f7f', width=1.5, dash='dash'),
                hovertemplate='SPY (标准化)<br>日期: %{x|%Y-%m-%d}<br>价格: $%{y:.2f}<extra></extra>',
                showlegend=(i == 0)  # 只在第一个子图显示图例
            ),
            row=row, col=col
        )

        # 更新每个子图的布局
        ytd = ytd_results.get(symbol, {}).get('ytd_return', 0) * 100 if ytd_results.get(symbol) else 0
        mtd = mtd_results.get(symbol, {}).get('mtd_return', 0) * 100 if mtd_results.get(symbol) else 0

        # 获取波动率数据
        vol = metrics['volatility'].get(symbol, {}).get('annual_volatility', 0) * 100

        # 添加标题中的关键指标
        fig.layout.annotations[i].update(
            text=f"{symbol}<br><span style='font-size:12px; color:#666'>YTD: {ytd:+.1f}% | MTD: {mtd:+.1f}% | 波动率: {vol:.1f}%</span>"
        )

        # 设置Y轴标题
        fig.update_yaxes(title_text="价格 ($)", row=row, col=col)

    # 更新整体布局
    fig.update_layout(
        title=dict(
            text='个股表现矩阵 (相对于SPY基准)',
            font=dict(size=20, color='#333')
        ),
        height=700,
        plot_bgcolor='white',
        hovermode='x unified',
        showlegend=True,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='center',
            x=0.5
        )
    )

    # 更新X轴
    fig.update_xaxes(title_text="日期", row=2, col=1)
    fig.update_xaxes(title_text="日期", row=2, col=2)

    return fig

def create_volume_distribution_chart(volume_data, period, start_date, end_date):
    """创建成交量分布饼图"""
    print("创建成交量分布饼图...")

    # 准备数据
    labels = volume_data['symbol'].tolist()
    values = volume_data['percentage'].tolist()
    colors = ['#2ca02c', '#1f77b4', '#ff7f0e', '#9467bd']  # NVDA, AAPL, CRM, IBM

    # 创建环形图
    fig = go.Figure(data=[
        go.Pie(
            labels=labels,
            values=values,
            hole=0.5,
            marker=dict(colors=colors),
            textinfo='label+percent',
            textposition='inside',
            hovertemplate='<b>%{label}</b><br>占比: %{percent}<br>成交量: %{value:.1f}%<extra></extra>'
        )
    ])

    # 更新布局
    period_text = {
        '1M': '最近1个月',
        '3M': '最近3个月',
        'YTD': '年初至今',
        'ALL': '全部数据'
    }.get(period, period)

    fig.update_layout(
        title=dict(
            text=f'成交量分布 ({period_text})<br><span style="font-size:14px; color:#666">{start_date.date()} 至 {end_date.date()}</span>',
            font=dict(size=18, color='#333')
        ),
        height=500,
        plot_bgcolor='white',
        showlegend=False,
        annotations=[
            dict(
                text=f'总成交量<br>{volume_data["total_volume"].sum():,.0f}股',
                x=0.5, y=0.5,
                font=dict(size=16, color='#666'),
                showarrow=False
            )
        ]
    )

    return fig

def create_yoy_comparison_chart(yoy_data):
    """创建YOY对比柱状图"""
    print("创建YOY对比柱状图...")

    # 准备数据 - 使用NVDA作为示例（数据最完整）
    symbol = 'NVDA'  # 选择数据最完整的股票
    if symbol not in yoy_data:
        # 如果没有NVDA，选择第一个可用的股票
        symbol = list(yoy_data.keys())[0] if yoy_data else 'SPY'

    data = yoy_data.get(symbol, {})
    pivot_table = data.get('pivot_table', pd.DataFrame())
    available_years = data.get('available_years', [])

    if len(available_years) < 2:
        print(f"  警告: {symbol} 的YOY数据不足，无法创建完整对比图")
        # 创建简单的月度图表作为替代
        return create_monthly_comparison_chart(yoy_data)

    # 创建分组柱状图
    fig = go.Figure()

    # 为每个年份添加柱状图
    year_colors = {2025: '#aec7e8', 2026: '#1f77b4'}  # 浅蓝和深蓝

    for year in available_years:
        if year in pivot_table.columns:
            fig.add_trace(go.Bar(
                x=pivot_table['month_name'],
                y=pivot_table[year],
                name=str(year),
                marker_color=year_colors.get(year, '#7f7f7f'),
                hovertemplate='年份: %{name}<br>月份: %{x}<br>平均收盘价: $%{y:.2f}<extra></extra>'
            ))

    # 计算并添加同比变化线（次Y轴）
    if 'yoy_change_pct' in pivot_table.columns:
        fig.add_trace(go.Scatter(
            x=pivot_table['month_name'],
            y=pivot_table['yoy_change_pct'],
            name='同比变化(%)',
            mode='lines+markers',
            line=dict(color='#ff7f0e', width=3),
            marker=dict(size=8),
            yaxis='y2',
            hovertemplate='月份: %{x}<br>同比变化: %{y:.1f}%<extra></extra>'
        ))

    # 更新布局
    fig.update_layout(
        title=dict(
            text=f'{symbol} - 月度平均收盘价YOY对比<br><span style="font-size:14px; color:#666">注: 数据时间范围有限，仅显示可用月份</span>',
            font=dict(size=18, color='#333')
        ),
        xaxis=dict(
            title='月份',
            type='category',
            categoryorder='array',
            categoryarray=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        ),
        yaxis=dict(
            title='平均收盘价 ($)',
            gridcolor='#f0f0f0'
        ),
        yaxis2=dict(
            title='同比变化 (%)',
            overlaying='y',
            side='right',
            gridcolor='#f0f0f0',
            showgrid=False
        ),
        barmode='group',
        height=500,
        plot_bgcolor='white',
        hovermode='x unified',
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='center',
            x=0.5
        )
    )

    return fig

def create_monthly_comparison_chart(yoy_data):
    """创建月度对比图（当YOY数据不足时）"""
    # 使用NVDA数据或第一个可用股票
    symbol = 'NVDA' if 'NVDA' in yoy_data else list(yoy_data.keys())[0] if yoy_data else 'SPY'

    data = yoy_data.get(symbol, {})
    monthly_data = data.get('monthly_data', pd.DataFrame())

    if monthly_data.empty:
        # 创建空图表
        fig = go.Figure()
        fig.update_layout(
            title=dict(
                text='YOY对比数据不足<br><span style="font-size:14px; color:#666">需要更多历史数据</span>',
                font=dict(size=18, color='#666')
            ),
            height=400,
            plot_bgcolor='white'
        )
        return fig

    # 创建月度柱状图
    fig = go.Figure()

    for year in monthly_data['year'].unique():
        year_data = monthly_data[monthly_data['year'] == year]

        # 创建月份名称
        year_data = year_data.sort_values('month')
        month_labels = year_data.apply(lambda row: f"{row['month_name']} {row['year']}", axis=1)

        fig.add_trace(go.Bar(
            x=month_labels,
            y=year_data['avg_close'],
            name=str(year),
            hovertemplate='%{x}<br>平均收盘价: $%{y:.2f}<br>交易日: %{customdata[0]}<extra></extra>',
            customdata=year_data[['trade_days']].values
        ))

    fig.update_layout(
        title=dict(
            text=f'{symbol} - 月度平均收盘价<br><span style="font-size:14px; color:#666">可用月份数据</span>',
            font=dict(size=18, color='#333')
        ),
        xaxis=dict(title='月份'),
        yaxis=dict(title='平均收盘价 ($)'),
        height=500,
        plot_bgcolor='white',
        barmode='group',
        hovermode='x unified'
    )

    return fig

def create_metrics_table(ytd_results, mtd_results, volume_data, metrics):
    """创建关键指标表格"""
    print("创建关键指标表格...")

    # 准备表格数据
    stocks = ['NVDA', 'AAPL', 'CRM', 'IBM', 'SPY']
    table_data = []

    for symbol in stocks:
        ytd = ytd_results.get(symbol, {}).get('ytd_return', 0) * 100 if ytd_results.get(symbol) else 0
        mtd = mtd_results.get(symbol, {}).get('mtd_return', 0) * 100 if mtd_results.get(symbol) else 0

        # 获取波动率和超额收益
        vol_data = metrics['volatility'].get(symbol, {})
        annual_vol = vol_data.get('annual_volatility', 0) * 100
        max_dd = vol_data.get('max_drawdown', 0) * 100

        excess_data = metrics['excess_returns'].get(symbol, {})
        excess_return = excess_data.get('cumulative_excess', 0) * 100 if excess_data else 0

        # 获取成交量数据
        vol_row = volume_data[volume_data['symbol'] == symbol] if symbol in volume_data['symbol'].values else None
        avg_volume = vol_row.iloc[0]['avg_daily_volume'] if vol_row is not None and not vol_row.empty else 0

        # 确定颜色
        ytd_color = '#2ca02c' if ytd >= 0 else '#d62728'
        mtd_color = '#2ca02c' if mtd >= 0 else '#d62728'

        table_data.append([
            symbol,
            f'<span style="color:{ytd_color}">{ytd:+.2f}%</span>',
            f'<span style="color:{mtd_color}">{mtd:+.2f}%</span>',
            f'{excess_return:+.2f}%' if symbol != 'SPY' else '基准',
            f'{annual_vol:.1f}%',
            f'{max_dd:.1f}%',
            f'{avg_volume:,.0f}'
        ])

    # 创建表格
    fig = go.Figure(data=[
        go.Table(
            header=dict(
                values=['股票', 'YTD涨幅', 'MTD涨幅', '超额收益(相对SPY)', '年化波动率', '最大回撤', '日均成交量'],
                fill_color='#1f77b4',
                align='center',
                font=dict(color='white', size=12),
                height=40
            ),
            cells=dict(
                values=list(zip(*table_data)),
                fill_color=['white', ['white', '#f9f9f9'] * 3],
                align='center',
                font=dict(size=11),
                height=35
            )
        )
    ])

    fig.update_layout(
        title=dict(
            text='关键指标汇总表',
            font=dict(size=18, color='#333')
        ),
        height=350,
        margin=dict(l=10, r=10, t=60, b=10)
    )

    return fig

# ============================================================================
# 主程序
# ============================================================================

def main():
    """主函数：生成完整看板"""
    print("🚀 开始生成美股大盘监控看板...")
    print("=" * 60)

    # 1. 加载数据
    stocks_df, spy_df = load_and_prepare_data()

    # 2. 计算指标 (DeepSeek部分)
    print("\n" + "=" * 60)
    print("📈 指标计算 (DeepSeek)")
    print("=" * 60)

    ytd_results = calculate_ytd_returns(pd.concat([stocks_df, spy_df]), current_year=2026)
    mtd_results = calculate_mtd_returns(pd.concat([stocks_df, spy_df]), current_year=2026, current_month=2)
    yoy_data = calculate_yoy_comparison(pd.concat([stocks_df, spy_df]))
    volume_data, period, start_date, end_date = calculate_volume_distribution(stocks_df, period='1M')
    metrics = calculate_key_metrics(stocks_df, spy_df)

    # 3. 生成图表 (Claude部分)
    print("\n" + "=" * 60)
    print("🎨 图表生成 (Claude)")
    print("=" * 60)

    # 创建所有图表
    chart1 = create_spy_ytd_chart(spy_df, ytd_results)
    chart2 = create_stocks_matrix_chart(stocks_df, spy_df, ytd_results, mtd_results, metrics)
    chart3 = create_volume_distribution_chart(volume_data, period, start_date, end_date)
    chart4 = create_yoy_comparison_chart(yoy_data)
    chart5 = create_metrics_table(ytd_results, mtd_results, volume_data, metrics)

    # 4. 生成HTML文件
    print("\n" + "=" * 60)
    print("💾 生成HTML看板文件")
    print("=" * 60)

    # 创建HTML内容
    html_content = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>美股大盘监控看板</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
                font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
            }}

            body {{
                background-color: #f8f9fa;
                color: #333;
                line-height: 1.6;
                padding: 20px;
            }}

            .container {{
                max-width: 1400px;
                margin: 0 auto;
            }}

            .header {{
                background: linear-gradient(135deg, #1f77b4, #2ca02c);
                color: white;
                padding: 30px;
                border-radius: 10px;
                margin-bottom: 30px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            }}

            .header h1 {{
                font-size: 36px;
                margin-bottom: 10px;
            }}

            .header p {{
                font-size: 16px;
                opacity: 0.9;
            }}

            .dashboard-grid {{
                display: grid;
                grid-template-columns: repeat(12, 1fr);
                grid-gap: 20px;
                margin-bottom: 30px;
            }}

            .chart-card {{
                background: white;
                border-radius: 10px;
                padding: 20px;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
                transition: transform 0.3s ease, box-shadow 0.3s ease;
            }}

            .chart-card:hover {{
                transform: translateY(-5px);
                box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
            }}

            .chart-title {{
                font-size: 18px;
                font-weight: 600;
                color: #1f77b4;
                margin-bottom: 15px;
                padding-bottom: 10px;
                border-bottom: 2px solid #f0f0f0;
            }}

            .full-width {{ grid-column: span 12; }}
            .two-thirds {{ grid-column: span 8; }}
            .half {{ grid-column: span 6; }}
            .one-third {{ grid-column: span 4; }}

            .info-box {{
                background: white;
                border-radius: 10px;
                padding: 25px;
                margin-bottom: 30px;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
            }}

            .info-box h3 {{
                color: #1f77b4;
                margin-bottom: 15px;
            }}

            .info-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin-top: 15px;
            }}

            .info-item {{
                background: #f8f9fa;
                padding: 15px;
                border-radius: 8px;
                border-left: 4px solid #1f77b4;
            }}

            .info-label {{
                font-size: 14px;
                color: #666;
                margin-bottom: 5px;
            }}

            .info-value {{
                font-size: 20px;
                font-weight: 600;
                color: #333;
            }}

            .positive {{ color: #2ca02c; }}
            .negative {{ color: #d62728; }}

            .footer {{
                text-align: center;
                margin-top: 40px;
                padding: 20px;
                color: #666;
                font-size: 14px;
                border-top: 1px solid #eee;
            }}

            @media (max-width: 1200px) {{
                .two-thirds {{ grid-column: span 12; }}
                .half {{ grid-column: span 12; }}
                .one-third {{ grid-column: span 12; }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📈 美股大盘监控看板</h1>
                <p>实时监控S&P 500及重点个股表现 | 数据更新日期: {spy_df['date'].max().date()} | 数据来源: Alpha Vantage API</p>
            </div>

            <div class="info-box">
                <h3>📊 数据概览</h3>
                <div class="info-grid">
                    <div class="info-item">
                        <div class="info-label">监控股票数量</div>
                        <div class="info-value">{stocks_df['symbol'].nunique()} 只</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">数据时间范围</div>
                        <div class="info-value">{stocks_df['date'].min().date()} 至 {stocks_df['date'].max().date()}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">SPY YTD涨幅</div>
                        <div class="info-value {'positive' if ytd_results.get('SPY', {}).get('ytd_return', 0) >= 0 else 'negative'}">
                            {ytd_results.get('SPY', {}).get('ytd_return', 0)*100:+.2f}%
                        </div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">总成交量(最近1个月)</div>
                        <div class="info-value">{volume_data['total_volume'].sum():,.0f} 股</div>
                    </div>
                </div>
            </div>

            <div class="dashboard-grid">
                <!-- 大盘指数走势图 -->
                <div class="chart-card two-thirds">
                    <div class="chart-title">S&P 500指数YTD走势</div>
                    <div id="chart1"></div>
                </div>

                <!-- 关键指标表格 -->
                <div class="chart-card one-third">
                    <div class="chart-title">关键指标汇总</div>
                    <div id="chart5"></div>
                </div>

                <!-- 个股表现矩阵 -->
                <div class="chart-card full-width">
                    <div class="chart-title">个股表现矩阵 (相对于SPY基准)</div>
                    <div id="chart2"></div>
                </div>

                <!-- 成交量分布图 -->
                <div class="chart-card half">
                    <div class="chart-title">成交量分布 (最近1个月)</div>
                    <div id="chart3"></div>
                </div>

                <!-- YOY对比图 -->
                <div class="chart-card half">
                    <div class="chart-title">YOY同比对比分析</div>
                    <div id="chart4"></div>
                </div>
            </div>

            <div class="info-box">
                <h3>📝 使用说明</h3>
                <p>1. <strong>交互功能</strong>: 所有图表均支持悬停查看详细数据、缩放、平移等交互操作。</p>
                <p>2. <strong>数据说明</strong>: 当前数据时间范围为100个交易日(约5个月)，YOY对比受数据时间范围限制。</p>
                <p>3. <strong>指标解释</strong>: YTD=年初至今涨幅，MTD=本月至今涨幅，超额收益=相对于SPY的收益。</p>
                <p>4. <strong>更新频率</strong>: 数据每日收盘后更新，图表自动刷新。</p>
            </div>

            <div class="footer">
                <p>© 2026 美股大盘监控看板 | 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p>技术支持: Python + Pandas + Plotly | 数据源: Alpha Vantage API</p>
            </div>
        </div>

        <script>
            // 图表数据
            const chart1_data = {chart1.to_json()};
            const chart2_data = {chart2.to_json()};
            const chart3_data = {chart3.to_json()};
            const chart4_data = {chart4.to_json()};
            const chart5_data = {chart5.to_json()};

            // 渲染图表
            Plotly.newPlot('chart1', chart1_data.data, chart1_data.layout);
            Plotly.newPlot('chart2', chart2_data.data, chart2_data.layout);
            Plotly.newPlot('chart3', chart3_data.data, chart3_data.layout);
            Plotly.newPlot('chart4', chart4_data.data, chart4_data.layout);
            Plotly.newPlot('chart5', chart5_data.data, chart5_data.layout);

            // 响应式调整
            window.addEventListener('resize', function() {{
                Plotly.Plots.resize('chart1');
                Plotly.Plots.resize('chart2');
                Plotly.Plots.resize('chart3');
                Plotly.Plots.resize('chart4');
                Plotly.Plots.resize('chart5');
            }});

            // 添加图表下载功能
            document.querySelectorAll('.chart-card').forEach(card => {{
                const chartId = card.querySelector('[id^="chart"]').id;
                const downloadBtn = document.createElement('button');
                downloadBtn.innerHTML = '⬇️ 下载图表';
                downloadBtn.style.cssText = `
                    position: absolute;
                    top: 20px;
                    right: 20px;
                    padding: 5px 10px;
                    background: #1f77b4;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 12px;
                `;
                downloadBtn.onclick = function() {{
                    Plotly.downloadImage(chartId, {{
                        format: 'png',
                        width: 1200,
                        height: 600,
                        filename: chartId
                    }});
                }};
                card.style.position = 'relative';
                card.appendChild(downloadBtn);
            }});
        </script>
    </body>
    </html>
    """

    # 保存HTML文件
    output_file = '美股大盘监控看板.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"✅ 看板已生成: {output_file}")
    print(f"📁 文件大小: {os.path.getsize(output_file):,} 字节")
    print(f"🌐 使用方式: 直接在浏览器中打开 '{output_file}'")
    print("\n" + "=" * 60)
    print("🎉 美股大盘监控看板生成完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()