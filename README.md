# stock-playground V2

A 股模拟交易 Playground V2 - 更多数据、更长时间、更强定制

## ✨ V2 新特性

### 📊 更多股票
- **50+ 只 A 股**，覆盖 10 大行业
  - 银行、白酒、新能源、科技、医药
  - 消费、房地产、制造业、能源、材料
- 每只股票有独特的波动特性

### 📈 更多数据维度
除了 OHLCV，还包括：
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
- 行业分布分析
- 关键指标对比（收益率、波动率、换手率）

### 💾 数据导出
- 导出 CSV / JSON
- 支持单股或全部导出
- 可自定义导出天数

### ⚙️ 自定义股票
- 创建自己的模拟股票
- 自定义波动率、市值、行业
- 适合测试特定场景

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

### CLI

```bash
# 查看行情
python cli.py market
python cli.py market --industry 新能源

# 查看行业
python cli.py industries

# 个股详情（支持日线/周线/月线）
python cli.py info 000001.SZ --days 60 --freq D

# 模拟交易
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

# 创建自定义股票
python cli.py create-stock --name "测试股份" --code 999999.SZ --price 50.0 --volatility 0.05
```

---

## 项目结构

```
stock-playground/
├── src/
│   ├── data/
│   │   └── mock_data.py      # 增强版 Mock 数据生成
│   ├── core/
│   │   ├── portfolio.py      # 账户、持仓、交易
│   │   └── backtest.py       # 回测引擎
│   └── strategies/
│       └── examples.py       # 策略示例
├── cli.py                    # CLI 入口
├── app.py                    # Streamlit Web
├── requirements.txt
├── LICENSE
├── DISCLAIMER.md
└── README.md
```

---

## 数据字段说明

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
