"""
Streamlit Web 界面
"""
import streamlit as st
import sys
sys.path.insert(0, '/root/.openclaw/workspace/projects/stock-playground/src')

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from data.mock_data import MockStockData
from core.portfolio import Portfolio
from core.backtest import BacktestEngine
from strategies.examples import STRATEGIES

# 页面配置
st.set_page_config(
    page_title="股票模拟交易",
    page_icon="📈",
    layout="wide"
)

# 初始化
@st.cache_resource
def get_data():
    return MockStockData()

data = get_data()
pf = Portfolio()

# 侧边栏导航
st.sidebar.title("📈 股票 Playground")
page = st.sidebar.radio("导航", [
    "行情", "交易", "持仓", "回测", "交易记录"
])

if page == "行情":
    st.title("📊 市场行情")
    
    # 获取股票列表
    stocks = data.get_stock_list()
    
    # 显示为表格
    df = pd.DataFrame(stocks)
    df['涨跌幅'] = df['change'].apply(lambda x: f"{x:+.2f}%")
    df['价格'] = df['price'].apply(lambda x: f"¥{x:.2f}")
    df['成交量'] = df['volume'].apply(lambda x: f"{x:,}")
    
    st.dataframe(
        df[['code', 'name', '价格', '涨跌幅', '成交量']].rename(columns={
            'code': '代码',
            'name': '名称'
        }),
        use_container_width=True
    )
    
    # 选择股票查看K线
    st.subheader("📈 K线图")
    selected_code = st.selectbox("选择股票", [s['code'] for s in stocks], 
                                  format_func=lambda x: f"{x} - {next(s['name'] for s in stocks if s['code'] == x)}")
    days = st.slider("显示天数", 5, 60, 30)
    
    if selected_code:
        kline = data.get_kline(selected_code, days)
        info = data.get_stock_info(selected_code)
        
        fig = go.Figure(data=[go.Candlestick(
            x=kline['date'],
            open=kline['open'],
            high=kline['high'],
            low=kline['low'],
            close=kline['close'],
            name=info['name']
        )])
        
        fig.update_layout(
            title=f"{info['name']} ({selected_code})",
            yaxis_title="价格",
            xaxis_title="日期",
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)

elif page == "交易":
    st.title("💰 模拟交易")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("买入")
        stocks = data.get_stock_list()
        buy_code = st.selectbox("选择股票（买入）", [s['code'] for s in stocks],
                                 format_func=lambda x: f"{x} - {next(s['name'] for s in stocks if s['code'] == x)}")
        buy_price = st.number_input("买入价格", min_value=0.01, value=10.0, step=0.01)
        buy_amount = st.number_input("买入数量", min_value=100, value=1000, step=100)
        
        if st.button("买入", type="primary"):
            stock = next(s for s in data.MOCK_STOCKS if s['code'] == buy_code)
            result = pf.buy(buy_code, stock['name'], buy_price, int(buy_amount))
            if result['success']:
                st.success(result['message'])
            else:
                st.error(result['message'])
    
    with col2:
        st.subheader("卖出")
        positions = pf.get_positions()
        if positions:
            sell_code = st.selectbox("选择持仓", [p['code'] for p in positions],
                                     format_func=lambda x: f"{x} - {next(p['name'] for p in positions if p['code'] == x)}")
            sell_price = st.number_input("卖出价格", min_value=0.01, value=10.0, step=0.01)
            max_amount = next(p['amount'] for p in positions if p['code'] == sell_code)
            sell_amount = st.number_input("卖出数量", min_value=100, max_value=max_amount, value=min(100, max_amount), step=100)
            
            if st.button("卖出", type="primary"):
                stock = next(s for s in data.MOCK_STOCKS if s['code'] == sell_code)
                result = pf.sell(sell_code, stock['name'], sell_price, int(sell_amount))
                if result['success']:
                    st.success(result['message'])
                else:
                    st.error(result['message'])
        else:
            st.info("暂无持仓")

elif page == "持仓":
    st.title("💼 我的账户")
    
    summary = pf.get_summary()
    positions = pf.get_positions()
    
    # 账户概览卡片
    cols = st.columns(4)
    with cols[0]:
        st.metric("总资产", f"¥{summary['total_value']:,.2f}", f"{summary['total_profit_pct']:+.2f}%")
    with cols[1]:
        st.metric("可用资金", f"¥{summary['cash']:,.2f}")
    with cols[2]:
        st.metric("持仓市值", f"¥{summary['positions_value']:,.2f}")
    with cols[3]:
        st.metric("总盈亏", f"¥{summary['total_profit']:,.2f}")
    
    st.divider()
    
    # 持仓明细
    st.subheader("持仓明细")
    if positions:
        df = pd.DataFrame(positions)
        df['盈亏'] = df['profit'].apply(lambda x: f"{x:+,.2f}")
        df['盈亏率'] = df['profit_pct'].apply(lambda x: f"{x:+.2f}%")
        df['市值'] = df['market_value'].apply(lambda x: f"¥{x:,.2f}")
        st.dataframe(df, use_container_width=True)
    else:
        st.info("暂无持仓")

elif page == "回测":
    st.title("🔄 策略回测")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.subheader("参数设置")
        strategy_name = st.selectbox("选择策略", list(STRATEGIES.keys()))
        backtest_days = st.slider("回测天数", 30, 252, 120)
        initial_cash = st.number_input("初始资金", min_value=10000, value=100000, step=10000)
        
        run_backtest = st.button("开始回测", type="primary")
    
    with col2:
        if run_backtest:
            with st.spinner("正在运行回测..."):
                # 准备数据
                backtest_data = MockStockData(days=backtest_days)
                stock_data = {code: df for code, df in backtest_data.data.items()}
                
                # 运行回测
                engine = BacktestEngine(initial_cash=initial_cash)
                result = engine.run(STRATEGIES[strategy_name], stock_data)
            
            st.subheader("回测结果")
            
            # 结果指标
            cols = st.columns(4)
            with cols[0]:
                st.metric("最终资产", f"¥{result.final_value:,.2f}")
            with cols[1]:
                st.metric("总收益", f"¥{result.total_return:,.2f}")
            with cols[2]:
                st.metric("收益率", f"{result.total_return_pct:+.2f}%")
            with cols[3]:
                st.metric("交易次数", len(result.trades))
            
            # 收益曲线
            if result.daily_values:
                df = pd.DataFrame(result.daily_values)
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=df['date'],
                    y=df['value'],
                    mode='lines',
                    name='总资产'
                ))
                fig.add_trace(go.Scatter(
                    x=df['date'],
                    y=[result.initial_cash] * len(df),
                    mode='lines',
                    name='初始资金',
                    line=dict(dash='dash')
                ))
                fig.update_layout(
                    title="收益曲线",
                    xaxis_title="日期",
                    yaxis_title="资产价值",
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

elif page == "交易记录":
    st.title("📜 交易记录")
    
    trades = pf.get_trades(limit=100)
    if trades:
        df = pd.DataFrame(reversed(trades))  # 最新的在前
        df['操作'] = df['action'].apply(lambda x: '买入' if x == 'buy' else '卖出')
        df['金额'] = df['total'].apply(lambda x: f"¥{x:,.2f}")
        st.dataframe(df[['time', 'code', 'name', '操作', 'price', 'amount', '金额']], 
                     use_container_width=True)
    else:
        st.info("暂无交易记录")
