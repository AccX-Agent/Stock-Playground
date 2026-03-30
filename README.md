# stock-playground V3

A 股模拟交易 Playground V3 - 时间推进、持仓分析、沪深300基准

## ✨ V3 新特性（时间推进版）

### ⏰ 真实时间推进系统
- **逐日推进**：点击「下一交易日」按钮，体验真实的交易时间线
- **不能穿越未来**：最多推进到数据的最后一天
- **动态价格更新**：持仓盈亏随日期实时更新
- **进度追踪**：顶部显示当前日期和进度条

### 📊 持仓回测分析
每笔买入后，可以查看详细分析：
- **收益曲线**：从买入日到当前日期的收益走势
- **最大盈利/亏损**：持仓期间的历史极值
- **最佳卖出点**：错过的最佳卖出时机和收益
- **最大回撤**：持仓期间的最大回撤百分比
- **沪深300对比**：与大盘基准的相对表现
- **超额收益(α)**：跑赢/跑输大盘多少

### 📈 沪深300基准
- 自动生成沪深300指数数据
- 作为持仓对比的基准
- 也可单独导出分析

---

## V2 特性回顾

### 📊 更多股票
- **50+ 只 A 股**，覆盖 10 大行业
- 每只股票有独特的波动特性

### 📈 更多数据维度
- **换手率** - 交易活跃度
- **市盈率 (PE)** - 估值水平
- **市值** - 公司规模
- **振幅** - 日内波动
- **成交额** - 交易金额

### 🕐 更长历史 & 多周期
- 支持 **1-10 年** 历史数据
- 支持 **日线 / 周线 / 月线** 切换

### 🎯 股票对比
- 多股票收益对比
- 支持沪深300基准对比

### 💾 数据导出
- 导出 CSV / JSON
- 支持单股、全部股票或沪深300

---

## 快速开始

```bash
cd stock-playground
pip install -r requirements.txt
```

### Web 界面

```bash
streamlit run app.py
```

访问 http://localhost:8501

### 使用指南

1. **查看行情**：点击"行情中心"查看全市场股票
2. **模拟交易**：在"模拟交易"页面买卖股票
3. **推进时间**：点击右上角「➡️ 下一交易日」进入下一天
4. **查看持仓**："我的持仓"页面显示当前持仓和盈亏
5. **持仓分析**：在"持仓回测"页面分析持仓表现
6. **对比分析**："股票对比"页面可对比多只股票

### CLI（V3 暂不支持时间推进，仅 Web 支持）

```bash
# 查看行情
python cli.py market
python cli.py market --industry 新能源

# 查看行业
python cli.py industries

# 个股详情
python cli.py info 000001.SZ --days 60 --freq D

# 模拟交易（以当前价格）
python cli.py buy --code 000001.SZ --price 10.5 --amount 1000
python cli.py sell --code 000001.SZ --price 11.0 --amount 500

# 查看持仓
python cli.py portfolio

# 股票对比
python cli.py compare 000001.SZ 600519.SH 002594.SZ --days 60

# 策略回测
python cli.py backtest --strategy simple_ma --days 252 --cash 100000

# 导出数据
python cli.py export 000001.SZ -o data.csv --format csv --days 252
```

---

## 项目结构

```
stock-playground/
├── src/
│   ├── data/
│   │   └── mock_data.py           # Mock 数据生成（含沪深300）
│   ├── core/
│   │   ├── portfolio.py           # 账户、持仓、交易（V3 记录买入日期）
│   │   ├── backtest.py            # 回测引擎
│   │   ├── time_manager.py        # 【V3 新增】时间推进管理
│   │   └── position_analyzer.py   # 【V3 新增】持仓分析器
│   └── strategies/
│       └── examples.py            # 策略示例
├── cli.py                         # CLI 入口
├── app.py                         # Streamlit Web（V3 时间推进版）
├── requirements.txt
├── LICENSE
├── DISCLAIMER.md
└── README.md
```

---

## 新模块说明（V3）

### TimeManager - 时间推进管理器
```python
from core.time_manager import TimeManager

# 初始化（传入所有交易日）
tm = TimeManager(all_dates)

# 获取当前日期
current_date = tm.current_date  # 如 "2024-01-15"

# 推进到下一交易日
if tm.advance():
    print(f"日期已推进到: {tm.current_date}")

# 检查是否最后一天
if tm.is_last_date:
    print("已是最后一天")
```

### PositionAnalyzer - 持仓分析器
```python
from core.position_analyzer import PositionAnalyzer

# 创建分析器
analyzer = PositionAnalyzer(stock_data, hs300_data)

# 分析持仓
result = analyzer.analyze(
    code="000001.SZ",
    name="平安银行",
    buy_date="2024-01-15",
    buy_price=10.5,
    amount=1000,
    current_date="2024-03-15",
    current_price=11.2
)

# 查看结果
print(f"总收益率: {result.total_return_pct}%")
print(f"最大盈利: {result.max_profit_pct}%")
print(f"最大回撤: {result.max_drawdown_pct}%")
print(f"最佳卖出日期: {result.best_sell_date}")
print(f"错过收益: {result.missed_profit_pct}%")
print(f"沪深300对比: {result.alpha}% (α)")
```

---

## 数据字段说明

### 股票数据

| 字段 | 说明 | 示例 |
|------|------|------|
| date | 交易日期 | 2024-01-15 |
| open | 开盘价 | 10.50 |
| high | 最高价 | 10.80 |
| low | 最低价 | 10.30 |
| close | 收盘价 | 10.65 |
| volume | 成交量 | 1500000 |
| amount | 成交额 | 15975000.00 |
| turnover | 换手率(%) | 3.25 |
| pe_ratio | 市盈率 | 15.50 |
| market_cap | 市值(亿) | 500.00 |
| amplitude | 振幅(%) | 4.76 |
| change_pct | 涨跌幅(%) | 1.43 |

### 持仓分析结果

| 字段 | 说明 |
|------|------|
| total_return_pct | 总收益率(%) |
| total_return_amount | 总盈亏金额(¥) |
| max_profit_pct | 持仓期间最大盈利(%) |
| max_loss_pct | 持仓期间最大亏损(%) |
| max_drawdown_pct | 最大回撤(%) |
| best_sell_date | 最佳卖出日期 |
| best_sell_return_pct | 最佳卖出收益率(%) |
| missed_profit_pct | 错过收益(%) |
| hs300_return_pct | 同期沪深300收益率(%) |
| alpha | 超额收益(%) |

---

## 免责声明

**本项目仅供学习交流，不构成任何投资建议。**

- 所有数据均为随机生成的 Mock 数据，与真实市场无关
- 模拟交易使用虚拟资金，不涉及真实金钱
- 股市有风险，投资需谨慎
- 作者不对因使用本项目产生的任何损失承担责任

---

## License

MIT License - 详见 [LICENSE](LICENSE) 文件
