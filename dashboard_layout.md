# 美股大盘监控看板 - 布局设计

## 📊 看板布局草图 (Mermaid)

```mermaid
graph TB
    subgraph "美股大盘监控看板 - 布局"
        A["大盘指数走势图<br/>折线图<br/>S&P 500 YTD走势"] --> B
        A --> C
        B["个股表现矩阵<br/>4家公司走势对比"] --> D
        C["关键指标摘要<br/>本月/YTD涨幅 & 成交量"] --> D
        D["成交量分布<br/>饼图<br/>行业成交量占比"] --> E
        E["YOY对比<br/>柱状图<br/>月度收盘价对比"]
    end

    subgraph "详细布局结构"
        Header["📈 美股大盘监控看板 (2026年)"]

        Row1["第1行: 大盘概览"]
        Chart1["📈 大盘指数走势图 (70%宽度)"]
        Metrics1["📊 关键指标 (30%宽度)"]

        Row2["第2行: 个股分析"]
        Chart2["📊 个股表现矩阵 (100%宽度)"]

        Row3["第3行: 成交量分析"]
        Chart3["🥧 成交量分布饼图 (50%宽度)"]
        Chart4["📊 YOY对比柱状图 (50%宽度)"]

        Footer["🔄 最后更新: 2026-02-26 | 数据源: Alpha Vantage"]
    end
```

## 🎨 实际看板网格布局

```mermaid
graph LR
    subgraph "看板网格布局 (4列网格系统)"
        A1["<div style='padding:10px;background:#f0f8ff;border-radius:5px;'><b>图表1: 大盘指数走势</b><br/>S&P 500 YTD折线图</div>"] -- 占据2列 --> A2
        B1["<div style='padding:10px;background:#f0f8ff;border-radius:5px;'><b>指标摘要</b><br/>SPY本月/YTD涨幅</div>"]

        C1["<div style='padding:10px;background:#fff0f5;border-radius:5px;'><b>图表2: 个股表现矩阵</b><br/>4家公司走势对比</div>"] -- 占据4列 --> C2

        D1["<div style='padding:10px;background:#f5f0ff;border-radius:5px;'><b>图表3: 成交量分布</b><br/>行业占比饼图</div>"] -- 占据2列 --> D2
        E1["<div style='padding:10px;background:#f5f0ff;border-radius:5px;'><b>图表4: YOY对比</b><br/>月度柱状图</div>"]
    end
```

## 📱 响应式布局设计

```mermaid
graph TD
    subgraph "桌面端布局 (≥1200px)"
        Col1["Column 1-2: 大盘走势图"]
        Col2["Column 3: 指标摘要"]
        Col3["Column 1-4: 个股矩阵"]
        Col4["Column 1-2: 成交量饼图"]
        Col5["Column 3-4: YOY柱状图"]
    end

    subgraph "平板端布局 (768px-1199px)"
        RowA["Row 1: 大盘走势图"]
        RowB["Row 2: 指标摘要"]
        RowC["Row 3: 个股矩阵"]
        RowD["Row 4: 成交量饼图"]
        RowE["Row 5: YOY柱状图"]
    end

    subgraph "移动端布局 (<768px)"
        Card1["Card 1: 大盘走势图"]
        Card2["Card 2: 指标摘要"]
        Card3["Card 3: 个股矩阵"]
        Card4["Card 4: 成交量饼图"]
        Card5["Card 5: YOY柱状图"]
    end
```

## 🛠️ 技术实现建议

### 布局实现方式
1. **CSS Grid系统** (推荐)
   ```css
   .dashboard-grid {
     display: grid;
     grid-template-columns: repeat(4, 1fr);
     grid-gap: 20px;
     padding: 20px;
   }

   .chart-large { grid-column: span 2; }
   .chart-full { grid-column: span 4; }
   ```

2. **Bootstrap网格** (备选)
   ```html
   <div class="row">
     <div class="col-md-8">大盘走势图</div>
     <div class="col-md-4">指标摘要</div>
   </div>
   ```

3. **Flexbox布局** (简单实现)
   ```css
   .dashboard-container {
     display: flex;
     flex-wrap: wrap;
     justify-content: space-between;
   }
   ```

### 图表库选择
- **主要推荐**: ECharts、Chart.js、Plotly.js
- **企业级**: Highcharts、D3.js (定制化强)
- **轻量级**: ApexCharts、Frappe Charts

### 交互功能
1. **悬停提示**: 显示具体数值
2. **点击钻取**: 从大盘到个股详情
3. **时间筛选**: 切换YTD/MTD/自定义范围
4. **数据导出**: CSV/PNG导出功能

---
*布局设计完成，接下来为每个图表定义详细配置*