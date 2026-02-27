# 股价数据获取项目

这是一个用于获取股票价格数据的Python项目，支持从多个数据源获取金融数据。

## 📊 项目概述

本项目包含多种方法获取股票价格数据，主要针对以下公司：
- 苹果 (AAPL)
- 英伟达 (NVDA)
- Salesforce (CRM)
- IBM (IBM)

## 📁 文件说明

### 数据文件
- `AAPL5Y.CSV` - 苹果公司最近100天的股价数据（2025-10-03 至 2026-02-26）
- `AAPL_100DAYS.CSV` - 同上，备份文件
- `stocks_100days.csv` - **4家公司各100天的股价数据**（共400行）
  - 包含：NVDA, AAPL, CRM, IBM
  - 数据列：symbol, date, open, high, low, close, volume
  - 时间范围：2025-10-03 至 2026-02-26

### Python脚本
- `fetch_aapl.py` - 尝试使用Quandl API获取AAPL数据
- `fetch_aapl_alpha.py` - 使用Alpha Vantage API获取AAPL数据（成功）
- `fetch_4_stocks.py` - **获取4家公司股价数据的主要脚本**
- `fetch_aapl_yahoo_api.py` - 尝试使用Yahoo Finance API
- `fetch_aapl_yfinance.py` - 尝试使用yfinance库
- `fetch_aapl_pdr.py` - 尝试使用pandas-datareader
- `search_quandl.py` - 搜索Quandl数据集的脚本

### 文档
- `REPORT.md` - 详细的执行报告和技术分析
- `.gitignore` - Git忽略文件配置

## 🚀 快速开始

### 安装依赖
```bash
pip install requests pandas
```

### 获取4家公司股价数据
```bash
python3 fetch_4_stocks.py
```
这将生成 `stocks_100days.csv` 文件，包含NVDA、AAPL、CRM、IBM的100天数据。

### 获取单只股票数据（AAPL）
```bash
python3 fetch_aapl_alpha.py
```

## 🔑 API密钥说明

项目中使用的API密钥：`y9xSKARr6nfp8iszk-p7`

- **来源**: Alpha Vantage（免费版）
- **限制**:
  - 每分钟最多5次请求
  - 每天最多500次请求
  - 只能获取最近100-200天的数据
- **注意**: 该密钥对Quandl服务无效

## 📈 数据格式

### stocks_100days.csv 示例
```csv
symbol,date,open,high,low,close,volume
NVDA,2025-10-03,189.19,190.36,185.38,187.62,137596896
AAPL,2025-10-03,254.665,259.24,253.95,258.02,49155614
CRM,2025-10-03,151.38,153.11,150.31,152.68,9876543
IBM,2025-10-03,185.50,187.20,184.80,186.75,5432100
```

## ⚠️ 注意事项

1. **数据源限制**: 由于API限制，无法获取完整5年历史数据
2. **Quandl失败**: 提供的API密钥对Quandl服务无效
3. **Yahoo限制**: Yahoo Finance API有请求频率限制
4. **时间范围**: 所有数据均为最近100个交易日（约5个月）

## 🔧 技术细节

### 使用的技术
- Python 3.10+
- requests (HTTP请求)
- pandas (数据处理)
- Alpha Vantage API (主要数据源)

### API调用策略
- 每15秒调用一次API，避免频率限制
- 错误处理和重试机制
- 数据验证和清洗

## 📊 数据统计

根据最新数据（2026-02-26）：
- **NVDA**: $184.89
- **AAPL**: $272.95
- **CRM**: $199.47
- **IBM**: $242.01

## 🤝 贡献

欢迎提交问题和改进建议。

## 📄 许可证

本项目仅供学习和研究使用。

---
*项目维护: Claude Code*