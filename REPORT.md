# AAPL 股价数据获取报告

## 执行时间
2026-02-27

## 用户请求
使用 Quandl 获取苹果公司 (AAPL) 最近5年的每日股价数据，保存到 AAPL5Y.CSV 文件。
提供的 API Key: `y9xSKARr6nfp8iszk-p7`

## 执行结果

### 1. Quandl API 测试结果
- 测试了多个 Quandl 数据集 (EOD/AAPL, WIKI/AAPL, XNAS/AAPL, FRED/GDP)
- 所有请求返回 HTTP 403 错误
- 结论：提供的 API Key 对 Quandl 服务无效或已过期

### 2. API Key 验证
- 发现该 API Key 实际上是 **Alpha Vantage** 的免费版 Key
- Alpha Vantage 免费版限制：
  - 只能获取最近100天的每日数据
  - 无法获取完整5年历史数据（需要升级到付费版）

### 3. 已获取的数据
- 使用 Alpha Vantage 免费 API 获取了 **最近100天的 AAPL 股价数据**
- 保存文件：`AAPL_100DAYS.CSV`
- 数据时间范围：2025-10-03 至 2026-02-26
- 数据列：Date, Open, High, Low, Close, Volume

### 4. 尝试其他数据源

#### Yahoo Finance
- 尝试直接调用 Yahoo Finance API：返回 403 错误（请求限制）
- 尝试使用 pandas-datareader：返回 "Too Many Requests" 错误
- 尝试安装 yfinance 库：依赖包 curl_cffi 哈希校验失败（网络镜像问题）

#### Alpha Vantage 完整数据
- 免费版不支持获取5年完整数据
- 需要升级到付费计划才能使用 `outputsize=full` 参数

## 生成的文件

1. `AAPL_100DAYS.CSV` - 最近100天的 AAPL 股价数据（实际获取）
2. `AAPL5Y.CSV` - **未生成**（因无法获取5年完整数据）
3. 多个脚本文件：
   - `fetch_aapl.py` - Quandl 尝试脚本
   - `fetch_aapl_yfinance.py` - yfinance 脚本（未运行）
   - `fetch_aapl_yahoo_api.py` - Yahoo API 脚本
   - `fetch_aapl_alpha.py` - Alpha Vantage 脚本（成功运行）
   - `fetch_aapl_pdr.py` - pandas-datareader 脚本

## 建议的后续步骤

### 选项1：使用现有数据
- 接受现有的100天数据 (`AAPL_100DAYS.CSV`)
- 重命名为 `AAPL5Y.CSV`（但数据不是5年）

### 选项2：获取完整5年数据的方法
1. **升级 Alpha Vantage 账户**（付费）
   - 使用同一 API Key 升级到付费计划
   - 然后可以获取完整历史数据

2. **使用其他免费数据源**（需要解决技术问题）
   - 解决 yfinance 安装问题（修复 curl_cffi 哈希问题）
   - 或使用其他金融数据 API（如 IEX Cloud、Tiingo 等）

3. **手动下载数据**
   - 从 Yahoo Finance、Google Finance 等网站手动导出 CSV
   - 然后进行格式处理

### 选项3：验证 API Key 用途
- 确认此 API Key 是否确实用于 Quandl 服务
- 如果是，请检查 Quandl 账户权限和订阅状态

## 下一步操作建议

请指示您希望：
1. 接受现有的100天数据（重命名为 AAPL5Y.CSV）
2. 尝试修复 yfinance 安装问题以获取 Yahoo 数据
3. 使用其他方法获取完整5年数据
4. 其他要求

---

*报告生成：Claude Code*