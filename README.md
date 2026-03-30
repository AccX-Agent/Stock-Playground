# stock-playground

A 股模拟交易 Playground，支持 CLI 和 Web 可视化界面，使用 Mock 数据进行离线测试。

## 功能

- 📈 **Mock 数据**：随机生成的 A 股数据，无需网络
- 💰 **模拟账户**：初始资金 100 万，虚拟买卖
- 📊 **可视化**：Streamlit Web 界面看行情、持仓、收益
- ⌨️ **CLI**：命令行快速交易
- 🔄 **回测**：支持自定义策略回测

## 安装

```bash
cd stock-playground
pip install -r requirements.txt
```

## 使用

### Web 界面（推荐）

```bash
streamlit run app.py
```

访问 http://localhost:8501

### CLI

```bash
# 查看行情
python cli.py market

# 买入
python cli.py buy --code 000001 --price 10.5 --amount 1000

# 查看持仓
python cli.py portfolio

# 查看交易记录
python cli.py history
```

## 项目结构

```
stock-playground/
├── src/
│   ├── data/          # Mock 数据生成
│   ├── core/          # 交易核心（账户、持仓、交易）
│   ├── strategies/    # 策略示例
│   └── web/           # Web 界面组件
├── cli.py             # CLI 入口
├── app.py             # Streamlit Web 入口
├── requirements.txt
└── README.md
```

## 免责声明

本项目仅供学习交流，不构成任何投资建议。股市有风险，投资需谨慎。
